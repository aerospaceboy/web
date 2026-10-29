from html.parser import HTMLParser
from pathlib import Path
import tempfile
import unittest

from blog_tools.build import NAV_ID, STYLE_ID, build
from blog_tools.build import navigation_source


class StyleParser(HTMLParser):
    def __init__(self):
        super().__init__()
        self.styles = []

    def handle_starttag(self, tag, attrs):
        if tag == "style":
            self.styles.append(dict(attrs))


class BuildTests(unittest.TestCase):
    def test_global_head_contains_one_identifiable_style(self):
        with tempfile.TemporaryDirectory() as directory:
            plan = build(directory)
            html = (Path(directory) / "global-head.html").read_text(encoding="utf-8")
            parser = StyleParser()
            parser.feed(html)
            self.assertEqual(len(parser.styles), 1)
            self.assertEqual(parser.styles[0]["id"], STYLE_ID)
            self.assertEqual(parser.styles[0]["data-ab-sha256"], plan["css_sha256"])
            self.assertEqual(plan["articles"], 7)
            self.assertIn(f'<script id="{NAV_ID}"', html)
            self.assertIn(plan["navigation_sha256"], html)
            self.assertIn('body:has(#home_top)', html)
            self.assertNotIn('overflow-x: hidden', html)

    def test_build_is_reproducible(self):
        with tempfile.TemporaryDirectory() as first, tempfile.TemporaryDirectory() as second:
            self.assertEqual(build(first), build(second))
            self.assertEqual((Path(first) / "global-head.html").read_bytes(),
                             (Path(second) / "global-head.html").read_bytes())

    def test_public_config_rejects_external_privacy_destinations(self):
        with self.assertRaisesRegex(ValueError, 'site origin'):
            navigation_source({'privacy_policy_path': '//example.com/privacy'})
