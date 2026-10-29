from pathlib import Path
import hashlib
import json
import tempfile
import unittest
import xml.etree.ElementTree as ET

from blog_tools.cover_assets import DESIGNS, generate, render_cover
from blog_tools.publish import ROOT, load_posts


class CoverTests(unittest.TestCase):
    def test_deployment_manifest_matches_committed_exports_and_post_covers(self):
        covers = json.loads((ROOT / 'config/covers.json').read_text(encoding='utf-8'))
        for slug, record in covers.items():
            data = (ROOT / f'customization/assets/covers/ab-cover-{slug}-v1.webp').read_bytes()
            self.assertEqual(hashlib.sha256(data).hexdigest(), record['sha256'])
            self.assertEqual(len(data), record['bytes'])
        for post in load_posts(ROOT / 'content/posts.json'):
            self.assertTrue(covers[post['slug']]['url'].endswith(post['cover']))

    def test_each_article_has_a_cover(self):
        slugs = {post['slug'] for post in load_posts(ROOT / 'content/posts.json')}
        self.assertEqual(slugs | {'default'}, set(DESIGNS))

    def test_covers_are_small_self_contained_svg_with_accessible_text(self):
        for slug in DESIGNS:
            with self.subTest(slug=slug):
                svg = render_cover(slug)
                root = ET.fromstring(svg)
                self.assertEqual(root.attrib['viewBox'], '0 0 1200 675')
                self.assertLess(len(svg.encode('utf-8')), 6000)
                self.assertIsNotNone(root.find('{http://www.w3.org/2000/svg}title'))
                self.assertIsNotNone(root.find('{http://www.w3.org/2000/svg}desc'))
                self.assertNotIn('<script', svg)
                self.assertNotIn('<image', svg)
                self.assertNotIn('href=', svg)

    def test_generation_is_reproducible(self):
        with tempfile.TemporaryDirectory() as directory:
            records = generate(directory)
            for record in records:
                path = Path(directory) / record['file']
                self.assertEqual(path.read_text(encoding='utf-8'), render_cover(record['slug']))
