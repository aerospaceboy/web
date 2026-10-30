from html.parser import HTMLParser
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch

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

    def test_github_destination_cannot_be_another_host_or_script(self):
        for destination in ['https://github.com.evil.example/aerospaceboy',
                            'javascript:alert(1)', 'https://github.com/aerospaceboy?token=value',
                            'https://github.com/aerospaceboy/web', '//github.com/aerospaceboy']:
            with self.subTest(destination=destination), self.assertRaisesRegex(ValueError, 'GitHub'):
                navigation_source({'github_profile_url': destination})

    def test_script_bundle_rejects_thymeleaf_inline_expressions(self):
        # Halo parses injected text through Thymeleaf before sending the page.
        # This ordinary JS nested-array spelling caused a truncated HTTP 200.
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            (root / 'customization').mkdir()
            for name in ['mobile-navigation', 'header-layout', 'space-effects',
                         'pointer-effects', 'resume-enhancement', 'site-hub']:
                (root / f'customization/{name}.js').write_text('', encoding='utf-8')
            for source in ["for (const row of [['/projects'], ['/resume']]) {}",
                           "const label = '[(${expression})]';"]:
                with self.subTest(source=source), patch('blog_tools.build.ROOT', root):
                    (root / 'customization/site-hub.js').write_text(source, encoding='utf-8')
                    with self.assertRaisesRegex(ValueError, 'Thymeleaf'):
                        navigation_source({})
