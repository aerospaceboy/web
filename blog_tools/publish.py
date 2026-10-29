"""Publish starter articles with deterministic identities and snapshot verification."""

import argparse
import hashlib
import json
import os
from pathlib import Path
import re
import sys
import time
from urllib.parse import urlencode, urlsplit

from markdown_it import MarkdownIt

from . import configure_console
from .halo import HaloClient, HaloError, validate_base_url

ROOT = Path(__file__).resolve().parents[1]
CORE = "/apis/content.halo.run/v1alpha1"
CONSOLE = "/apis/api.console.halo.run/v1alpha1"
SLUG = re.compile(r"[a-z0-9]+(?:-[a-z0-9]+)*\Z")


def managed_name(slug):
    return "ab-post-" + hashlib.sha256(slug.encode("utf-8")).hexdigest()[:24]


def render_markdown(raw):
    return MarkdownIt("commonmark", {"html": False}).render(raw)


def load_posts(manifest):
    manifest = Path(manifest).resolve()
    records = json.loads(manifest.read_text(encoding="utf-8-sig"))
    if not isinstance(records, list) or not records:
        raise ValueError("Article manifest must be a nonempty list")
    posts = []
    for record in records:
        target = (manifest.parent / record["file"]).resolve()
        if not target.is_relative_to(manifest.parent):
            raise ValueError("Article file must stay within the content directory")
        raw = target.read_text(encoding="utf-8-sig")
        posts.append({**record, "raw": raw, "html": render_markdown(raw)})
    validate_posts(posts)
    return posts


def validate_posts(posts):
    seen = set()
    for post in posts:
        slug = post.get("slug", "")
        if not isinstance(slug, str) or not SLUG.fullmatch(slug) or slug in seen:
            raise ValueError("Article slug is invalid or duplicated")
        seen.add(slug)
        if not all(isinstance(post.get(k), str) and post[k].strip()
                   for k in ("title", "category", "raw", "html")):
            raise ValueError(f"Article {slug} is missing required content")
        if not isinstance(post.get("tags"), list) or not all(
                isinstance(tag, str) and SLUG.fullmatch(tag) for tag in post["tags"]):
            raise ValueError(f"Article {slug} has invalid tags")
        cover = post.get('cover', '')
        if not isinstance(cover, str):
            raise ValueError(f"Article {slug} has an invalid cover")
        if cover:
            parsed = urlsplit(cover)
            relative = cover.startswith('/') and not cover.startswith('//')
            secure = parsed.scheme == 'https' and parsed.hostname and not parsed.username and not parsed.password
            if not (relative or secure) or any(c in cover for c in '\r\n<>\\'):
                raise ValueError(f"Article {slug} has an invalid cover")


def taxonomy_map(items, kind):
    result = {}
    for item in items:
        slug = item.get("spec", {}).get("slug")
        if slug in result:
            raise ValueError(f"Duplicate {kind} slug")
        if slug:
            result[slug] = item["metadata"]["name"]
    return result


class Publisher:
    def __init__(self, api, owner, *, sleep=time.sleep):
        if not isinstance(owner, str) or not owner.strip():
            raise ValueError("A configured owner is required")
        self.api = api
        self.owner = owner
        self.sleep = sleep

    def _check_identity(self, resource, post):
        if not isinstance(resource, dict):
            raise ValueError("Halo did not return a post resource")
        spec = resource.get("spec", {})
        if (resource.get("metadata", {}).get("name") != managed_name(post["slug"]) or
                spec.get("slug") != post["slug"] or spec.get("owner") != self.owner or
                spec.get("deleted") or resource.get("metadata", {}).get("deletionTimestamp")):
            raise ValueError("Managed post identity conflict; refusing to overwrite")

    def _draft(self, post, categories, tags):
        name = managed_name(post["slug"])
        resource = {
            "apiVersion": "content.halo.run/v1alpha1", "kind": "Post",
            "metadata": {"name": name},
            "spec": {"title": post["title"], "slug": post["slug"], "owner": self.owner,
                     "publish": False, "pinned": False, "allowComment": True,
                     "visible": "PUBLIC", "priority": 0, "deleted": False,
                     "excerpt": {"autoGenerate": True, "raw": ""}, "cover": post.get('cover', ''),
                     "categories": [categories[post["category"]]],
                     "tags": [tags[t] for t in post["tags"]]},
        }
        try:
            created = self.api.request("POST", CORE + "/posts", resource)
        except HaloError as exc:
            if exc.status not in (None, 409) and exc.status < 500:
                raise
            # A timeout or 5xx may happen after creation. Never resend this POST.
            created = self.api.request("GET", CORE + "/posts/" + name)
        self._check_identity(created, post)
        return created

    @staticmethod
    def _check_content(content, post):
        if not isinstance(content, dict) or any(content.get(k) != value for k, value in
                (("raw", post["raw"]), ("content", post["html"]), ("rawType", "MARKDOWN"))):
            raise ValueError("Content snapshot readback does not match the planned article")

    def _verify_release(self, name, post):
        for attempt in range(5):
            resource = self.api.request("GET", CORE + "/posts/" + name)
            if not isinstance(resource, dict):
                raise ValueError("Halo did not return publication state")
            if resource.get("spec", {}).get("publish") is True and resource.get(
                    "status", {}).get("phase") == "PUBLISHED":
                released = self.api.request("GET", CONSOLE + f"/posts/{name}/release-content")
                self._check_content(released, post)
                return
            self.sleep(0.2 * (attempt + 1))
        raise ValueError("Publication was not confirmed by Halo")

    def run(self, posts):
        validate_posts(posts)
        categories = taxonomy_map(self.api.list_all(CORE + "/categories"), "category")
        tags = taxonomy_map(self.api.list_all(CORE + "/tags"), "tag")
        for post in posts:
            if post["category"] not in categories:
                raise ValueError(f"Missing category slug: {post['category']}")
            if any(tag not in tags for tag in post["tags"]):
                raise ValueError(f"Missing tag slug for article: {post['slug']}")
        existing = {}
        for resource in self.api.list_all(CORE + "/posts"):
            slug = resource.get("spec", {}).get("slug")
            if slug in existing:
                raise ValueError("Duplicate remote post slug; resolve before publishing")
            existing[slug] = resource
        result = {"published": [], "skipped": [], "failed": []}
        for post in posts:
            slug = post["slug"]
            try:
                resource = existing.get(slug)
                if resource:
                    if resource.get("spec", {}).get("deleted"):
                        raise ValueError("Slug belongs to a deleted article; restore or rename it first")
                    if resource.get("spec", {}).get("publish") or resource.get(
                            "metadata", {}).get("name") != managed_name(slug):
                        result["skipped"].append(slug)
                        continue
                    self._check_identity(resource, post)
                else:
                    resource = self._draft(post, categories, tags)
                name = resource["metadata"]["name"]
                if resource.get("spec", {}).get("publish"):
                    self._verify_release(name, post)
                    result["skipped"].append(slug)
                    continue
                content = {"raw": post["raw"], "content": post["html"], "rawType": "MARKDOWN"}
                self.api.request("PUT", CONSOLE + f"/posts/{name}/content", content)
                verified = self.api.request("GET", CONSOLE + f"/posts/{name}/head-content")
                self._check_content(verified, post)
                snapshot = verified.get("snapshotName")
                if not isinstance(snapshot, str) or not snapshot:
                    raise ValueError("Verified content is missing its snapshot identity")
                publish_path = CONSOLE + f"/posts/{name}/publish?" + urlencode({"headSnapshot": snapshot})
                try:
                    self.api.request("PUT", publish_path)
                except HaloError as exc:
                    if exc.status is not None and exc.status < 500:
                        raise
                    # A publish may have succeeded even if the response was lost.
                self._verify_release(name, post)
                result["published"].append(slug)
            except (HaloError, ValueError, KeyError, TypeError) as exc:
                result["failed"].append({"slug": slug, "error": str(exc)})
        return result


def main(argv=None):
    configure_console()
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--config", type=Path, default=ROOT / "config/site.json")
    parser.add_argument("--manifest", type=Path, default=ROOT / "content/posts.json")
    mode = parser.add_mutually_exclusive_group()
    mode.add_argument("--apply", action="store_true", help="Create and publish missing articles")
    mode.add_argument("--dry-run", action="store_true", help="Validate offline (the default)")
    args = parser.parse_args(argv)
    try:
        config = json.loads(args.config.read_text(encoding="utf-8-sig"))
        validate_base_url(config["base_url"])
        posts = load_posts(args.manifest)
        if not args.apply:
            result = {"mode": "dry-run", "target": config["base_url"], "owner": config["owner"],
                      "articles": [{**{k: p[k] for k in ("slug", "title", "category", "tags")},
                                    'cover': p.get('cover', '')} for p in posts]}
        else:
            api = HaloClient(config["base_url"], os.environ.get("HALO_PAT", ""))
            result = Publisher(api, config["owner"]).run(posts)
        print(json.dumps(result, ensure_ascii=False, indent=2))
        return 1 if result.get("failed") else 0
    except (ValueError, KeyError, TypeError, OSError, HaloError) as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
