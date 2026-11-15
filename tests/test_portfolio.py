import unittest

from blog_tools.portfolio import render_projects, validate_projects


class PortfolioTests(unittest.TestCase):
    def project(self):
        return dict(title='Demo <project>', label='FPGA', summary='One & two',
                    focus='Protocol', scope='Simulation', version='2026',
                    path='/archives/demo', image='/upload/demo.png', tags=['RTL'],
                    github='https://github.com/aerospaceboy/FPGA')

    def test_markup_escapes_content_and_keeps_native_links(self):
        html = render_projects([self.project()])
        self.assertIn('Demo &lt;project&gt;', html)
        self.assertIn('One &amp; two', html)
        self.assertIn('href="/archives/demo"', html)
        self.assertIn('noopener noreferrer', html)
        self.assertIn('width="640" height="360"', html)

    def test_rejects_external_paths_and_executable_links(self):
        for key, value in [('path', '//example.com/demo'), ('image', 'data:image/png,x'),
                           ('path', '/archives/a" onclick="alert(1)'),
                           ('github', 'https://github.com.evil.test/a/b')]:
            with self.subTest(key=key, value=value):
                item = self.project()
                item[key] = value
                with self.assertRaises(ValueError):
                    validate_projects([item])

    def test_duplicate_project_paths_are_rejected(self):
        with self.assertRaisesRegex(ValueError, 'unique'):
            validate_projects([self.project(), self.project()])
