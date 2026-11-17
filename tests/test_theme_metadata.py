import unittest

from blog_tools.theme_metadata import patch_head, patch_layout, HEAD_ANCHOR, HEAD_INCLUDE, SELECTOR_ANCHOR


class ThemeMetadataTests(unittest.TestCase):
    def test_head_patch_preserves_existing_content_and_charset_order(self):
        source = '<th:block>\n' + HEAD_ANCHOR + '\n<script>existing()</script></th:block>'
        result = patch_head(source)
        self.assertEqual(result.replace('\n' + HEAD_INCLUDE, '', 1), source)
        self.assertLess(result.index('charset'), result.index('ab-page-metadata'))

    def test_ambiguous_or_already_patched_theme_is_rejected(self):
        for source in ['', HEAD_ANCHOR * 2, 'modules/ab-page-metadata']:
            with self.subTest(source=source), self.assertRaises(ValueError):
                patch_head(source)
        for source in ['', SELECTOR_ANCHOR * 2, 'meta#ab-page-metadata']:
            with self.subTest(source=source), self.assertRaises(ValueError):
                patch_layout(source)

    def test_pjax_changes_only_metadata_marker_not_jsonld_root(self):
        source = SELECTOR_ANCHOR + " '#body-wrap']; existing();"
        result = patch_layout(source)
        self.assertEqual(result.replace("'meta#ab-page-metadata', ", '', 1), source)
        self.assertNotIn('ab-page-schema', result)
