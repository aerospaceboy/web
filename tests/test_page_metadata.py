from html import escape
import json
import unittest

from blog_tools.audit import PageMetadata, inspect_page_metadata


class PageMetadataTests(unittest.TestCase):
    base = 'https://aerospaceboy.site'
    path = '/archives/example'

    def fixture(self):
        data = {'@context': 'https://schema.org', '@type': 'BlogPosting', 'url': self.base + self.path,
                'mainEntityOfPage': self.base + self.path, 'headline': '协议 "A&B" 与 FPGA',
                'datePublished': '2026-11-14T09:26:41Z', 'dateModified': '2026-11-15T09:26:41Z',
                'author': {'@type': 'Person', 'name': '作者', 'url': self.base + '/authors/example'},
                'image': [self.base + '/upload/example.png']}
        attrs = {'data-canonical': data['url'], 'data-kind': 'post', 'data-headline': data['headline'],
                 'data-published': data['datePublished'], 'data-modified': data['dateModified'],
                 'data-author-name': data['author']['name'], 'data-author-url': data['author']['url'],
                 'data-image': data['image'][0]}
        source = '<meta id="ab-page-metadata" ' + ' '.join(f'{k}="{escape(v, quote=True)}"' for k, v in attrs.items()) + '>'
        source += f'<link rel="canonical" href="{data["url"]}"><meta property="og:title" content="{escape(data["headline"], quote=True)}">'
        source += '<script id="ab-page-schema" type="application/ld+json">' + json.dumps(data) + '</script>'
        return source

    def check(self, source, path=None):
        page = PageMetadata();page.feed(source)
        return inspect_page_metadata(path or self.path, page, {'base_url': self.base})

    def test_real_server_metadata_with_escaped_headline_passes(self):
        self.assertEqual(self.check(self.fixture()), [])

    def test_home_canonical_cannot_hide_wrong_article_url(self):
        source = self.fixture().replace(f'rel="canonical" href="{self.base}{self.path}"', f'rel="canonical" href="{self.base}/"')
        self.assertIn('page_canonical_mismatch', self.check(source))

    def test_stale_or_invalid_article_fields_are_detected(self):
        source = self.fixture()
        for old, new, issue in [
            ('"@type": "BlogPosting"', '"@type": "WebPage"', 'article_schema_identity_mismatch'),
            ('"datePublished": "2026-11-14T09:26:41Z"', '"datePublished": "2026-11-14"', 'article_schema_date_mismatch'),
            ('"headline":', 'broken:', 'article_schema_invalid_json_or_fields')]:
            with self.subTest(issue=issue):
                self.assertIn(issue, self.check(source.replace(old, new)))

    def test_collection_page_must_not_retain_article_schema(self):
        self.assertIn('article_schema_on_non_article', self.check(self.fixture(), '/archives'))

    def test_additional_single_page_has_its_own_canonical(self):
        page = PageMetadata()
        page.feed(f'<meta id="ab-page-metadata" data-canonical="{self.base}/guestbook" data-kind="page">'
                  f'<link rel="canonical" href="{self.base}/guestbook">')
        self.assertEqual(inspect_page_metadata('/guestbook', page, {'base_url': self.base}), [])

    def test_duplicate_schema_or_marker_is_rejected(self):
        source = self.fixture()
        self.assertIn('expected_one_page_metadata_marker', self.check(source + source))
        schema = source[source.index('<script'):]
        self.assertIn('expected_one_article_schema', self.check(source + schema))
