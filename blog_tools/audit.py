"""Read-only checks for deployed CSS and SEO; findings are never silently passed."""

import argparse
from concurrent.futures import ThreadPoolExecutor
import hashlib
from html.parser import HTMLParser
import json
from pathlib import Path
from urllib.error import HTTPError, URLError
from urllib.parse import urljoin, urlsplit
from urllib.request import Request, urlopen
import xml.etree.ElementTree as ET

from . import configure_console
from .build import NAV_ID, STYLE_ID, navigation_source
from .halo import validate_base_url
from .publish import ROOT


class PageMetadata(HTMLParser):
    def __init__(self):
        super().__init__()
        self.meta = {}
        self.styles = []
        self.legacy_styles = 0
        self.navigation = []
        self.links = []
        self.cover_sources = []
        self._style_attrs = None
        self._style_text = []
        self._script_attrs = None
        self._script_text = []

    def handle_starttag(self, tag, attrs):
        attrs = dict(attrs)
        if tag == "a" and attrs.get("href"):
            self.links.append(attrs["href"])
        if tag == "img" and ('post_bg' in attrs.get('class', '').split() or attrs.get('alt') == 'cover'):
            source = attrs.get('data-lazy-src') or attrs.get('data-src') or attrs.get('src')
            if source:
                self.cover_sources.append(source)
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


class ArticleContent(HTMLParser):
    """Inspect only server-rendered article content, excluding injected scripts."""
    VOID = {'area', 'base', 'br', 'col', 'embed', 'hr', 'img', 'input', 'link', 'meta', 'param', 'source', 'track', 'wbr'}

    def __init__(self):
        super().__init__()
        self.stack = []
        self.text = []
        self.headings = []
        self.links = []
        self._heading = None

    def handle_starttag(self, tag, attrs):
        attrs = dict(attrs)
        if not self.stack and attrs.get('id') == 'article-container':
            self.stack.append(tag)
            return
        if not self.stack:
            return
        if tag == 'a' and attrs.get('href'):
            self.links.append(attrs['href'])
        if tag == 'h2':
            self._heading = []
        if tag not in self.VOID:
            self.stack.append(tag)

    def handle_data(self, data):
        if self.stack and not any(tag in {'script', 'style'} for tag in self.stack):
            self.text.append(data)
            if self._heading is not None:
                self._heading.append(data)

    def handle_endtag(self, tag):
        if not self.stack:
            return
        if tag == 'h2' and self._heading is not None:
            self.headings.append(''.join(self._heading).strip())
            self._heading = None
        if tag in self.stack:
            while self.stack:
                if self.stack.pop() == tag:
                    break


def inspect_resume(source, record):
    page = ArticleContent()
    page.feed(source)
    issues = []
    expected = {'教育经历', '项目经历', '科研经历', '在校工作经历', '荣誉奖项'}
    if not expected.issubset(page.headings):
        issues.append('resume_sections_missing')
    if len(''.join(page.text).strip()) < 300:
        issues.append('resume_content_empty_or_truncated')
    if urlsplit(record['attachment_url']).path not in page.links:
        issues.append('resume_pdf_link_missing')
    return issues


def content_hash(text):
    return hashlib.sha256((text.replace("\r\n", "\n").strip() + "\n").encode("utf-8")).hexdigest()


def inspect_html(path, source, config, digest, navigation_digest=None, covers=None):
    page = PageMetadata()
    page.feed(source)
    issues = []
    warnings = []
    if path == config.get('privacy_policy_path') and '请在此处添加你的隐私政策内容' in source:
        warnings.append('privacy_policy_placeholder_content')
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
    base = config.get("base_url", "https://aerospaceboy.site")
    if path == '/' and config.get('resume_path') and config['resume_path'] not in page.links:
        issues.append('resume_navigation_missing')
    if '/cc' in page.links:
        issues.append('broken_legacy_license_link')
    client_rewrites = {}
    if '/privacy' in page.links:
        if config.get('privacy_policy_path') and navigation_digest is not None:
            client_rewrites['/privacy'] = config['privacy_policy_path']
        else:
            issues.append('legacy_privacy_link_without_compatibility')
    if covers is not None:
        paths = {urlsplit(urljoin(base, value)).path for value in page.cover_sources}
        if any(urlsplit(urljoin(base, value)).netloc != urlsplit(base).netloc for value in page.cover_sources):
            issues.append('external_article_cover')
        expected = {urlsplit(record['url']).path for slug, record in covers.items() if slug != 'default'}
        if path == '/' and not expected.issubset(paths):
            issues.append('homepage_cover_mapping_mismatch')
        slug = path.removeprefix('/archives/')
        if path.startswith('/archives/') and slug in covers:
            if not page.cover_sources or urlsplit(urljoin(base, page.cover_sources[0])).path != urlsplit(covers[slug]['url']).path:
                issues.append('article_cover_mismatch')
            if config.get('license_url') not in page.links:
                issues.append('license_destination_mismatch')
    return {"path": path, "issues": issues, "warnings": warnings,
            "description": page.meta.get("description", []),
            "og_description": page.meta.get("og:description", []),
            "global_style_count": len(page.styles), "cover_sources": page.cover_sources,
            "client_link_rewrites": client_rewrites}


def audit(config):
    base = validate_base_url(config["base_url"])
    css = (ROOT / "customization/aerospaceboy-custom.css").read_text(encoding="utf-8")
    digest = content_hash(css)
    navigation = navigation_source(config)
    navigation_digest = content_hash(navigation)
    covers_path = ROOT / 'config/covers.json'
    covers = json.loads(covers_path.read_text(encoding='utf-8-sig')) if covers_path.exists() else None
    paths = ["/", "/archives", "/projects", "/about", "/archives/pid-control-intro", "/rss.xml", "/sitemap.xml"]
    if covers is not None:
        paths.extend('/archives/' + slug for slug in covers if slug != 'default')
    if config.get('privacy_policy_path'):
        paths.append(config['privacy_policy_path'])
    resume_path = ROOT / 'config/resume-deployment.json'
    resume = json.loads(resume_path.read_text(encoding='utf-8-sig')) if config.get('resume_path') and resume_path.exists() else None
    if resume:
        paths.append(config['resume_path'])
    paths = list(dict.fromkeys(paths))

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
                result = inspect_html(path, source, config, digest, navigation_digest, covers)
                if resume and path == config['resume_path']:
                    result['issues'].extend(inspect_resume(source, resume))
            result["status"] = status
            if redirected:
                result["issues"].append("unexpected_redirect")
            return result
        except (HTTPError, URLError, OSError, ValueError, ET.ParseError) as exc:
            return {"path": path, "issues": ["request_or_parse_failed"], "status": getattr(exc, "code", None)}

    with ThreadPoolExecutor(max_workers=4) as pool:
        results = list(pool.map(check, paths))
    assets = []
    asset_records = dict(covers or {})
    visual_assets_path = ROOT / 'config/visual-assets.json'
    if visual_assets_path.exists():
        visual_assets = json.loads(visual_assets_path.read_text(encoding='utf-8-sig'))
        asset_records.update({'visual/' + key: value for key, value in visual_assets.items()})
    if resume:
        asset_records['resume/pdf'] = {'url': resume['attachment_url'], 'sha256': resume['sha256'],
                                       'bytes': resume['bytes'], 'mime': 'application/pdf'}
    if asset_records:
        def check_asset(item):
            slug, record = item
            if urlsplit(record['url']).netloc != urlsplit(base).netloc:
                return {'slug': slug, 'ok': False, 'error': 'asset_origin_mismatch'}
            try:
                with urlopen(record['url'], timeout=15) as response:
                    data = response.read(1024 * 1024 + 1)
                    actual_hash = hashlib.sha256(data).hexdigest()
                    ok = (actual_hash == record['sha256'] and len(data) == record['bytes'] and
                          response.headers.get_content_type() == record.get('mime', 'image/webp'))
                return {'slug': slug, 'ok': ok, 'bytes': len(data), 'sha256': actual_hash}
            except (HTTPError, URLError, OSError):
                return {'slug': slug, 'ok': False, 'error': 'asset_request_failed'}
        with ThreadPoolExecutor(max_workers=4) as pool:
            assets = list(pool.map(check_asset, asset_records.items()))
    return {"target": base, "ok": all(not result["issues"] for result in results) and all(a['ok'] for a in assets),
            "pages": results, "assets": assets}


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
