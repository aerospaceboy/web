import copy
import unittest

from blog_tools.halo import HaloError
from blog_tools.publish import Publisher, managed_name


POST = {"slug": "demo", "title": "Demo", "category": "embedded",
        "tags": ["python"], "raw": "# Demo\n\n正文", "html": "<h1>Demo</h1>\n<p>正文</p>\n"}


class FakeHalo:
    """Model independent draft and release snapshots, including failed requests."""

    def __init__(self):
        self.posts = {}
        self.head = {}
        self.release = {}
        self.calls = []
        self.fail_content = False
        self.corrupt_head = False
        self.corrupt_release = False
        self.missing_snapshot = False
        self.ambiguous_create = False
        self.ambiguous_publish = False
        self.fail_publish = False

    def list_all(self, path):
        if path.endswith("categories"):
            return [{"metadata": {"name": "category-1"}, "spec": {"slug": "embedded"}}]
        if path.endswith("tags"):
            return [{"metadata": {"name": "tag-1"}, "spec": {"slug": "python"}}]
        return list(copy.deepcopy(self.posts).values())

    def request(self, method, path, data=None):
        self.calls.append((method, path, copy.deepcopy(data)))
        if method == "POST":
            name = data["metadata"]["name"]
            if name in self.posts:
                raise HaloError(method, path, 409)
            self.posts[name] = copy.deepcopy(data)
            if self.ambiguous_create:
                self.ambiguous_create = False
                raise HaloError(method, path)
            return copy.deepcopy(data)
        parts = path.split("/")
        name = parts[parts.index("posts") + 1]
        if name not in self.posts:
            raise HaloError(method, path, 404)
        if path.endswith("/content") and method == "PUT":
            if self.fail_content:
                raise HaloError(method, path, 500)
            self.head[name] = {**copy.deepcopy(data), "snapshotName": "verified-snapshot"}
            if self.missing_snapshot:
                self.head[name].pop("snapshotName")
            return copy.deepcopy(self.posts[name])
        if path.endswith("/head-content"):
            return {**self.head[name], "raw": "wrong"} if self.corrupt_head else self.head[name]
        if path.endswith("/release-content"):
            return {**self.release[name], "raw": "wrong"} if self.corrupt_release else self.release[name]
        if "/publish" in path:
            if self.fail_publish:
                raise HaloError(method, path, 500)
            self.release[name] = copy.deepcopy(self.head[name])
            self.posts[name]["spec"]["publish"] = True
            self.posts[name]["status"] = {"phase": "PUBLISHED"}
            if self.ambiguous_publish:
                self.ambiguous_publish = False
                raise HaloError(method, path)
        return copy.deepcopy(self.posts[name])


class PublishTests(unittest.TestCase):
    def setUp(self):
        self.api = FakeHalo()
        self.publisher = Publisher(self.api, "aerospaceboy", sleep=lambda _: None)

    def run_posts(self):
        return self.publisher.run([copy.deepcopy(POST)])

    def test_content_failure_never_publishes_or_counts_success(self):
        self.api.fail_content = True
        result = self.run_posts()
        self.assertEqual(result["published"], [])
        self.assertEqual(len(result["failed"]), 1)
        self.assertFalse(any("/publish" in path for _, path, _ in self.api.calls))

    def test_head_readback_mismatch_never_publishes(self):
        self.api.corrupt_head = True
        self.assertEqual(len(self.run_posts()["failed"]), 1)
        self.assertFalse(any("/publish" in path for _, path, _ in self.api.calls))

    def test_missing_snapshot_identity_never_publishes(self):
        self.api.missing_snapshot = True
        self.assertEqual(len(self.run_posts()["failed"]), 1)
        self.assertFalse(any("/publish" in path for _, path, _ in self.api.calls))

    def test_publish_pins_the_verified_snapshot(self):
        self.run_posts()
        path = next(path for _, path, _ in self.api.calls if "/publish" in path)
        self.assertTrue(path.endswith("?headSnapshot=verified-snapshot"))

    def test_repeat_run_creates_and_publishes_only_once(self):
        self.assertEqual(self.run_posts()["published"], ["demo"])
        self.assertEqual(self.run_posts()["skipped"], ["demo"])
        self.assertEqual(sum(method == "POST" for method, _, _ in self.api.calls), 1)
        self.assertEqual(sum("/publish" in path for _, path, _ in self.api.calls), 1)

    def test_planned_cover_is_preserved_in_created_article(self):
        post = copy.deepcopy(POST)
        post['cover'] = '/upload/demo.webp'
        self.assertEqual(self.publisher.run([post])['published'], ['demo'])
        self.assertEqual(next(iter(self.api.posts.values()))['spec']['cover'], '/upload/demo.webp')

    def test_unsafe_cover_url_prevents_all_mutations(self):
        post = copy.deepcopy(POST)
        post['cover'] = 'javascript:alert(1)'
        with self.assertRaisesRegex(ValueError, 'cover'):
            self.publisher.run([post])
        self.assertEqual(self.api.calls, [])

    def test_ambiguous_creation_is_reconciled_without_second_post(self):
        self.api.ambiguous_create = True
        self.assertEqual(self.run_posts()["published"], ["demo"])
        self.assertEqual(sum(method == "POST" for method, _, _ in self.api.calls), 1)

    def test_failed_content_can_resume_managed_draft(self):
        self.api.fail_content = True
        self.run_posts()
        self.api.fail_content = False
        self.assertEqual(self.run_posts()["published"], ["demo"])
        self.assertEqual(len(self.api.posts), 1)

    def test_does_not_overwrite_unmanaged_draft(self):
        self.api.posts["manual"] = {"metadata": {"name": "manual"},
                                    "spec": {"slug": "demo", "publish": False}}
        self.assertEqual(self.run_posts()["skipped"], ["demo"])
        self.assertFalse(any(method != "GET" for method, _, _ in self.api.calls))

    def test_managed_name_collision_does_not_overwrite(self):
        name = managed_name("demo")
        self.api.posts[name] = {"metadata": {"name": name},
                               "spec": {"slug": "other", "owner": "someone"}}
        self.assertEqual(len(self.run_posts()["failed"]), 1)
        self.assertFalse(any(method == "PUT" for method, _, _ in self.api.calls))

    def test_release_readback_mismatch_is_not_reported_as_success(self):
        self.api.corrupt_release = True
        result = self.run_posts()
        self.assertEqual(result["published"], [])
        self.assertEqual(len(result["failed"]), 1)

    def test_publish_failure_is_not_reported_as_success(self):
        self.api.fail_publish = True
        self.assertEqual(self.run_posts()["published"], [])

    def test_ambiguous_publish_is_verified_without_retrying_write(self):
        self.api.ambiguous_publish = True
        self.assertEqual(self.run_posts()["published"], ["demo"])
        self.assertEqual(sum("/publish" in path for _, path, _ in self.api.calls), 1)

    def test_missing_taxonomy_prevents_all_mutations(self):
        post = copy.deepcopy(POST)
        post["tags"] = ["missing"]
        with self.assertRaisesRegex(ValueError, "tag"):
            self.publisher.run([post])
        self.assertEqual(self.api.calls, [])

    def test_duplicate_manifest_slugs_prevent_all_mutations(self):
        with self.assertRaisesRegex(ValueError, "slug"):
            self.publisher.run([POST, POST])
        self.assertEqual(self.api.calls, [])


if __name__ == "__main__":
    unittest.main()
