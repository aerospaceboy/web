import unittest

from blog_tools.share_metadata import OPEN, URL, IMAGE, patch_share_metadata
from blog_tools.audit import PageMetadata, inspect_share_metadata


class ShareMetadataTests(unittest.TestCase):
    def fixture(self):
        return OPEN + '\n' + '\n'.join([URL, IMAGE, URL, IMAGE]) + '\n<!-- other content -->\n</th:block>'

    def test_both_social_formats_get_normalized_url_and_image_variables(self):
        result = patch_share_metadata(self.fixture(), '/upload/default.webp')
        self.assertEqual(result.count('th:content="${abShareUrl}"'), 2)
        self.assertEqual(result.count('image=${#strings.startsWith(rawImage'), 2)
        self.assertIn("#strings.endsWith(site.url, '/')", result)
        self.assertIn("#strings.startsWith(rawImage, '//')", result)
        self.assertIn('<!-- other content -->', result)
        self.assertNotIn("'null'", result)

    def test_unknown_or_repeated_patch_is_rejected(self):
        for source in ['', self.fixture() + OPEN, self.fixture().replace(URL, '', 1),
                       patch_share_metadata(self.fixture(), '/upload/default.webp')]:
            with self.subTest(source=source), self.assertRaises(ValueError):
                patch_share_metadata(source, '/upload/default.webp')

    def test_path_cannot_break_thymeleaf_attribute(self):
        for path in ['//evil.example/image.webp', '/upload/a\'b.webp', '/upload/a"b.webp', '/other/image.webp']:
            with self.subTest(path=path), self.assertRaises(ValueError):
                patch_share_metadata(self.fixture(), path)


class ShareAuditTests(unittest.TestCase):
    base = 'https://aerospaceboy.site'

    def inspect(self, url, image):
        parser = PageMetadata()
        parser.feed(f'<meta property="og:url" content="{url}"><meta name="twitter:url" content="{url}">'
                    f'<meta property="og:image" content="{image}"><meta name="twitter:image" content="{image}">')
        return inspect_share_metadata('/projects', parser, self.base)

    def test_exact_share_url_and_absolute_cover_pass(self):
        self.assertEqual(self.inspect(self.base + '/projects', self.base + '/upload/cover.webp'), [])

    def test_duplicate_path_separator_is_reported(self):
        issues = self.inspect(self.base + '//projects', self.base + '/upload/cover.webp')
        self.assertIn('og:url_mismatch', issues)
        self.assertIn('twitter:url_mismatch', issues)

    def test_relative_unsafe_or_missing_image_is_rejected(self):
        for image in ['/upload/cover.webp', '//example.com/cover.webp', 'null', 'http://example.com/cover.webp', 'https://name:secret@example.com/cover.webp']:
            with self.subTest(image=image):
                self.assertIn('og:image_not_absolute_https', self.inspect(self.base + '/projects', image))
