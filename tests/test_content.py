from pathlib import Path
import contextlib
import importlib.util
import io
import os
import tempfile
import unittest
from unittest.mock import patch

from blog_tools.publish import ROOT, load_posts, main, render_markdown


class ContentTests(unittest.TestCase):
    def test_original_seven_articles_are_available(self):
        posts = load_posts(ROOT / "content/posts.json")
        self.assertEqual(len(posts), 7)
        self.assertIn("ros2-basics", {post["slug"] for post in posts})

    def test_html_is_escaped_and_code_is_not_interpreted_as_emphasis(self):
        html = render_markdown('<script>alert(1)</script>\n\n`**literal** <x>`\n')
        self.assertNotIn("<script>", html)
        self.assertIn("&lt;script&gt;", html)
        self.assertIn("<code>**literal** &lt;x&gt;</code>", html)

    def test_unsafe_link_protocol_is_not_rendered(self):
        self.assertNotIn('href="javascript:', render_markdown("[click](javascript:alert(1))"))

    def test_manifest_cannot_read_outside_content_directory(self):
        (ROOT / ".cache").mkdir(exist_ok=True)
        with tempfile.TemporaryDirectory(dir=ROOT / ".cache") as directory:
            manifest = Path(directory) / "posts.json"
            manifest.write_text('[{"file":"../outside.md"}]', encoding="utf-8")
            with self.assertRaisesRegex(ValueError, "content directory"):
                load_posts(manifest)

    def test_default_command_is_offline_without_credentials(self):
        # main configures real stdout, so use a StringIO which intentionally has no reconfigure.
        with patch.dict(os.environ, {}, clear=True), patch(
                'blog_tools.publish.HaloClient', side_effect=AssertionError('network access')), \
                contextlib.redirect_stdout(io.StringIO()) as output:
            self.assertEqual(main([]), 0)
            self.assertIn('dry-run', output.getvalue())

    def test_importing_compatibility_entry_point_does_not_publish(self):
        with patch.dict(os.environ, {}, clear=True), patch(
                'blog_tools.publish.main', side_effect=AssertionError('publication on import')):
            spec = importlib.util.spec_from_file_location('legacy_entry', ROOT / '.make-posts.py')
            spec.loader.exec_module(importlib.util.module_from_spec(spec))
