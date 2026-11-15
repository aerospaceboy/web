import json
import unittest

from blog_tools.audit import inspect_html
from blog_tools.seo import SEO_ID, identity_json, site_identity


class IdentityTests(unittest.TestCase):
    def setUp(self):
        self.config = {'base_url': 'https://aerospaceboy.site', 'site_title': '半截的诗',
                       'author_name': 'AerospaceBoy', 'site_description': '工程记录',
                       'github_profile_url': 'https://github.com/aerospaceboy'}

    def test_identity_references_public_profile_and_does_not_invent_article(self):
        graph = site_identity(self.config)['@graph']
        self.assertEqual([node['@type'] for node in graph], ['WebSite', 'Person'])
        self.assertEqual(graph[0]['publisher']['@id'], graph[1]['@id'])
        self.assertEqual(graph[1]['sameAs'], ['https://github.com/aerospaceboy'])
        self.assertNotIn('datePublished', identity_json(self.config))

    def test_script_breakout_is_escaped_without_changing_json_value(self):
        self.config['site_title'] = '</script><script>alert("x")</script>&'
        source = identity_json(self.config)
        self.assertNotIn('<', source)
        self.assertNotIn('&', source)
        self.assertEqual(json.loads(source)['@graph'][0]['name'], self.config['site_title'])

    def test_arbitrary_same_as_destination_is_rejected(self):
        self.config['github_profile_url'] = 'https://github.com.evil.example/person'
        with self.assertRaises(ValueError):
            site_identity(self.config)

    def test_audit_requires_real_valid_single_server_script(self):
        def audit(source):
            return inspect_html('/projects', source, self.config, 'unused')['issues']
        block = f'<script id="{SEO_ID}" type="application/ld+json">{identity_json(self.config)}</script>'
        self.assertNotIn('expected_one_site_identity', audit(block))
        self.assertNotIn('site_identity_mismatch', audit(block))
        self.assertIn('expected_one_site_identity', audit(block * 2))
        self.assertIn('site_identity_invalid_json', audit(block.replace('"@graph"', 'broken')))
        self.assertIn('site_identity_mismatch', audit(block.replace('AerospaceBoy', 'Another author')))
