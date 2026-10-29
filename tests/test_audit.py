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

    def test_lazy_cover_sources_are_checked_for_external_requests(self):
        source = '<img class="post_bg" src="" data-lazy-src="https://picsum.photos/600/400?random">'
        covers = {'demo': {'url': 'https://aerospaceboy.site/upload/demo.webp'}}
        result = inspect_html('/', source, {}, 'abc', covers=covers)
        self.assertIn('external_article_cover', result['issues'])
        self.assertIn('homepage_cover_mapping_mismatch', result['issues'])

    def test_correct_lazy_cover_mapping_passes_media_checks(self):
        source = '<img class="post_bg" src="" data-lazy-src="/upload/demo.webp">'
        covers = {'demo': {'url': 'https://aerospaceboy.site/upload/demo.webp'}}
        result = inspect_html('/', source, {}, 'abc', covers=covers)
        self.assertNotIn('external_article_cover', result['issues'])
        self.assertNotIn('homepage_cover_mapping_mismatch', result['issues'])

    def test_legacy_license_and_privacy_links_are_not_silently_accepted(self):
        result = inspect_html('/archives/demo', '<a href="/cc">CC</a><a href="/privacy">隐私政策</a>', {}, 'abc')
        self.assertIn('broken_legacy_license_link', result['issues'])
        self.assertIn('legacy_privacy_link_without_compatibility', result['issues'])

    def test_related_cover_does_not_hide_wrong_article_cover(self):
        source = '<img alt="cover" src="/upload/wrong.webp"><img class="post_bg" src="/upload/demo.webp">'
        result = inspect_html('/archives/demo', source, {}, 'abc', covers={'demo': {'url': '/upload/demo.webp'}})
        self.assertIn('article_cover_mismatch', result['issues'])

    def test_placeholder_policy_is_reported_as_content_warning(self):
        result = inspect_html('/privacy-policy', '请在此处添加你的隐私政策内容。',
                              {'privacy_policy_path': '/privacy-policy'}, 'abc')
        self.assertIn('privacy_policy_placeholder_content', result['warnings'])
