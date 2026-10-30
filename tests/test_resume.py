import unittest

from blog_tools.resume import render_resume


def sample():
    return {'name': '示例姓名', 'affiliation': '示例学校', 'email': 'demo@example.invalid', 'phone': '0000',
            'download': '/upload/resume.pdf',
            'education': {'school': '示例学校', 'period': '2024-至今', 'courses': '示例课程', 'performance': '示例描述'},
            'projects': [{'title': '示例项目', 'role': '成员', 'summary': '内容', 'work': '工作', 'results': '成果'}],
            'research': [], 'leadership': [], 'awards': ['示例荣誉']}


class ResumeTests(unittest.TestCase):
    def test_render_preserves_sections_and_pdf_link(self):
        html = render_resume(sample())
        for title in ['教育经历', '项目经历', '科研经历', '在校工作经历', '荣誉奖项']:
            self.assertEqual(html.count('<h2>' + title + '</h2>'), 1)
        self.assertIn('href="/upload/resume.pdf"', html)
        self.assertIn('下载简历（PDF）', html)

    def test_document_text_is_escaped_not_executed(self):
        data = sample();data['name'] = '<script>alert(1)</script>'
        html = render_resume(data)
        self.assertNotIn('<script>', html)
        self.assertIn('&lt;script&gt;', html)

    def test_unsafe_attachment_and_contact_are_rejected(self):
        for key, value in [('download', '//other.example/resume.pdf'), ('email', '" onclick="alert(1)'), ('phone', 'javascript:alert(1)')]:
            data = sample();data[key] = value
            with self.subTest(key=key), self.assertRaises(ValueError):
                render_resume(data)
