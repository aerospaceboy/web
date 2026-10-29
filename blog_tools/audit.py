"""Read-only checks for deployed CSS and SEO; findings are never silently passed."""

import argparse
from concurrent.futures import ThreadPoolExecutor
import hashlib
from html.parser import HTMLParser
import json
from pathlib import Path
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen
import xml.etree.ElementTree as ET

from . import configure_console
from .build import NAV_ID, STYLE_ID
from .halo import validate_base_url
from .publish import ROOT


class PageMetadata(HTMLParser):
    def __init__(self):
        super().__init__()
        self.meta = {}
        self.styles = []
        self.legacy_styles = 0
        self.navigation = []
        self._style_attrs = None
        self._style_text = []
        self._script_attrs = None
        self._script_text = []

    def handle_starttag(self, tag, attrs):
        attrs = dict(attrs)
        if tag == "meta":
            key = attrs.get("name", attrs.get("property"))
            if key:
                self.meta.setdefault(key, []).append(attrs.get("content", ""))
        if tag == "style":
            self._style_attrs = attrs
            self._style_text = []
            if attrs.get("id") == STYLE_ID:
                self.styles.append(attrs)
        if tag == "script" and attrs.get("id") == NAV_ID:
            self.navigation.append(attrs)
            self._script_attrs = attrs
            self._script_text = []

    def handle_data(self, data):
        if self._style_attrs is not None:
            self._style_text.append(data)
        if self._script_attrs is not None:
            self._script_text.append(data)

    def handle_endtag(self, tag):
        if tag == "style" and self._style_attrs is not None:
            self._style_attrs["actual_sha256"] = content_hash("".join(self._style_text))
            if self._style_attrs.get("id") != STYLE_ID and "--ab-radius" in "".join(self._style_text):
                self.legacy_styles += 1
            self._style_attrs = None
        if tag == "script" and self._script_attrs is not None:
            self._script_attrs["actual_sha256"] = content_hash("".join(self._script_text))
            self._script_attrs = None


def content_hash(text):
    return hashlib.sha256((text.replace("\r\n", "\n").strip() + "\n").encode("utf-8")).hexdigest()


def inspect_html(path, source, config, digest, navigation_digest=None):
    page = PageMetadata()
    page.feed(source)
    issues = []
    if len(page.styles) != 1:
        issues.append("expected_one_global_style")
    elif page.styles[0].get("data-ab-sha256") != digest:
        issues.append("global_style_version_mismatch")
    elif page.styles[0].get("actual_sha256") != digest:
        issues.append("global_style_content_mismatch")
    expected = config.get("site_description") if path == "/" else config.get("about_description") if path == "/about" else None
    if expected:
        for name in ("description", "og:description"):
            if page.meta.get(name) != [expected]:
                issues.append(name + "_mismatch")
    if page.legacy_styles:
        issues.append("legacy_homepage_style_injection")
    if navigation_digest is not None and (len(page.navigation) != 1 or
            page.navigation[0].get("data-ab-sha256") != navigation_digest):
        issues.append("mobile_navigation_version_mismatch")
    elif navigation_digest is not None and page.navigation[0].get("actual_sha256") != navigation_digest:
        issues.append("mobile_navigation_content_mismatch")
    return {"path": path, "issues": issues,
            "description": page.meta.get("description", []),
            "og_description": page.meta.get("og:description", []),
            "global_style_count": len(page.styles)}


def audit(config):
    base = validate_base_url(config["base_url"])
    css = (ROOT / "customization/aerospaceboy-custom.css").read_text(encoding="utf-8")
    digest = content_hash(css)
    navigation = (ROOT / "customization/mobile-navigation.js").read_text(encoding="utf-8")
    navigation_digest = content_hash(navigation)
    paths = ["/", "/archives", "/projects", "/about", "/archives/pid-control-intro", "/rss.xml", "/sitemap.xml"]

    def check(path):
        try:
            request = Request(base + path, headers={"User-Agent": "AerospaceBoy-ReadOnlyAudit/1.0"})
            with urlopen(request, timeout=15) as response:
                source = response.read().decode("utf-8")
                status = response.status
                redirected = response.url != base + path
            if path.endswith(".xml"):
                xml = ET.fromstring(source)
                result = {"path": path, "issues": [], "entries": len(xml.findall(".//item")) if path == "/rss.xml" else
                          sum(1 for node in xml.iter() if node.tag.endswith("}loc"))}
                if result["entries"] == 0:
                    result["issues"].append("empty_feed_or_sitemap")
            else:
                result = inspect_html(path, source, config, digest, navigation_digest)
            result["status"] = status
            if redirected:
                result["issues"].append("unexpected_redirect")
            return result
        except (HTTPError, URLError, OSError, ValueError, ET.ParseError) as exc:
            return {"path": path, "issues": ["request_or_parse_failed"], "status": getattr(exc, "code", None)}

    with ThreadPoolExecutor(max_workers=4) as pool:
        results = list(pool.map(check, paths))
    return {"target": base, "ok": all(not result["issues"] for result in results), "pages": results}


def main(argv=None):
    configure_console()
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--config", type=Path, default=ROOT / "config/site.json")
    parser.add_argument("--output", type=Path)
    args = parser.parse_args(argv)
    config = json.loads(args.config.read_text(encoding="utf-8-sig"))
    result = audit(config)
    text = json.dumps(result, ensure_ascii=False, indent=2) + "\n"
    if args.output:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(text, encoding="utf-8")
    print(text, end="")
    return 0 if result["ok"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
