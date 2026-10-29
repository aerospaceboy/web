import unittest

from blog_tools.audit import content_hash, inspect_html
from blog_tools.build import STYLE_ID


class AuditTests(unittest.TestCase):
    def test_http_success_does_not_hide_missing_style_and_default_excerpt(self):
        result = inspect_html("/about", '<meta name="description" content="default">',
                              {"about_description": "correct"}, "abc")
        self.assertIn("expected_one_global_style", result["issues"])
        self.assertIn("description_mismatch", result["issues"])
        self.assertIn("og:description_mismatch", result["issues"])

    def test_correct_global_style_and_metadata_pass(self):
        css = ':root {--ab-radius:14px}\n'
        digest = content_hash(css)
        source = (f'<style id="{STYLE_ID}" data-ab-sha256="{digest}">{css}</style>'
                  '<meta name="description" content="correct">'
                  '<meta property="og:description" content="correct">')
        self.assertEqual(inspect_html("/", source, {"site_description": "correct"}, digest)["issues"], [])

    def test_correct_hash_attribute_does_not_hide_truncated_css(self):
        digest = content_hash(':root {--ab-radius:14px}')
        source = f'<style id="{STYLE_ID}" data-ab-sha256="{digest}">broken</style>'
        self.assertIn("global_style_content_mismatch", inspect_html("/projects", source, {}, digest)["issues"])

    def test_duplicate_styles_are_reported(self):
        source = f'<style id="{STYLE_ID}"></style>' * 2
        self.assertIn("expected_one_global_style", inspect_html("/projects", source, {}, "abc")["issues"])

    def test_old_banner_style_is_reported_even_after_global_style_is_added(self):
        source = (f'<style id="{STYLE_ID}" data-ab-sha256="abc"></style>'
                  '<style>:root {--ab-radius:14px}</style>')
        self.assertIn("legacy_homepage_style_injection",
                      inspect_html("/projects", source, {}, "abc")["issues"])

    def test_navigation_bundle_version_is_checked_when_required(self):
        source = f'<style id="{STYLE_ID}" data-ab-sha256="abc"></style>'
        self.assertIn("mobile_navigation_version_mismatch",
                      inspect_html("/projects", source, {}, "abc", "nav-hash")["issues"])
