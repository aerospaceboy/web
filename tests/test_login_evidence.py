import importlib.util
from pathlib import Path
import unittest


spec = importlib.util.spec_from_file_location('login_evidence', Path(__file__).resolve().parents[1] / 'tools/login_evidence.py')
module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(module)


class LoginEvidenceTests(unittest.TestCase):
    def sample(self):
        return {'collected_at': '2026-10-30T04:00:00Z',
                'users': [{'account': 'demo', 'password': 'never-export-this'}],
                'devices': [], 'notifications': [],
                'login_requests': [{'time': '30/Oct/2026:12:00:00 +0800', 'ip': '192.0.2.1',
                                    'http_status': 302, 'source_file': 'access.log', 'source_line': 1,
                                    'cookie': 'never-export-cookie'}]}

    def test_unknown_redirect_does_not_become_a_success_or_failure(self):
        html = module.render_report(self.sample())
        self.assertIn('未知 / 未知', html)
        self.assertIn('不能单独判定认证结果', html)
        self.assertIn('不表示该账号从未登录', html)

    def test_unselected_secret_fields_never_reach_the_report(self):
        html = module.render_report(self.sample())
        self.assertNotIn('never-export-this', html)
        self.assertNotIn('never-export-cookie', html)

    def test_account_and_log_fields_are_escaped(self):
        sample = self.sample()
        sample['users'][0]['account'] = '<script>bad()</script>'
        html = module.render_report(sample)
        self.assertNotIn('<script>', html)
        self.assertIn('&lt;script&gt;bad()&lt;/script&gt;', html)


if __name__ == '__main__':
    unittest.main()
