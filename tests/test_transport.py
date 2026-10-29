from contextlib import contextmanager
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
import json
import socket
import threading
import unittest

from blog_tools.halo import HaloClient, HaloError, validate_base_url
from blog_tools.publish import Publisher
from test_publish import FakeHalo, POST


@contextmanager
def server_for(callback):
    class Handler(BaseHTTPRequestHandler):
        def log_message(self, *args):
            pass

        def handle_request(self):
            raw = self.rfile.read(int(self.headers.get("Content-Length", 0)))
            status, headers, body = callback(self.command, self.path, raw)
            if status is None:
                self.connection.shutdown(socket.SHUT_RDWR)
                self.connection.close()
                return
            self.send_response(status)
            for key, value in headers.items():
                self.send_header(key, value)
            self.end_headers()
            self.wfile.write(body)

        do_GET = do_POST = do_PUT = handle_request

    server = ThreadingHTTPServer(("127.0.0.1", 0), Handler)
    thread = threading.Thread(target=server.serve_forever, daemon=True)
    thread.start()
    try:
        yield f"http://127.0.0.1:{server.server_port}"
    finally:
        server.shutdown()
        server.server_close()
        thread.join(timeout=2)


class TransportTests(unittest.TestCase):
    def test_only_get_is_retried_on_server_error(self):
        calls = []
        def callback(method, path, body):
            calls.append(method)
            return 503, {}, b'{"secret":"do-not-log-this"}'
        with server_for(callback) as base:
            client = HaloClient(base, "test-token", sleep=lambda _: None)
            for method, expected in (("GET", 3), ("POST", 1), ("PUT", 1)):
                calls.clear()
                with self.assertRaises(HaloError) as error:
                    client.request(method, "/apis/test", {})
                self.assertEqual(len(calls), expected)
                self.assertNotIn("do-not-log-this", str(error.exception))
                self.assertNotIn("test-token", str(error.exception))

    def test_connection_drop_does_not_retry_post(self):
        calls = []
        with server_for(lambda m, p, b: (calls.append(m) or None, {}, b"")) as base:
            with self.assertRaises(HaloError):
                HaloClient(base, "test-token").request("POST", "/apis/test", {})
        self.assertEqual(calls, ["POST"])

    def test_redirect_is_not_followed_with_credentials(self):
        paths = []
        def callback(method, path, body):
            paths.append(path)
            return 302, {"Location": "/stolen"}, b""
        with server_for(callback) as base:
            with self.assertRaises(HaloError) as error:
                HaloClient(base, "test-token").request("GET", "/apis/test")
        self.assertEqual(error.exception.status, 302)
        self.assertEqual(paths, ["/apis/test"])

    def test_permission_error_is_not_retried(self):
        calls = []
        with server_for(lambda m, p, b: (calls.append(m) or 403, {}, b"{}")) as base:
            with self.assertRaises(HaloError):
                HaloClient(base, "test-token").request("GET", "/apis/test")
        self.assertEqual(calls, ["GET"])

    def test_paginated_taxonomy_follows_has_next(self):
        def callback(method, path, body):
            more = "page=1&" in path
            data = {"items": [{"metadata": {"name": "a" if more else "b"}}], "hasNext": more}
            return 200, {}, json.dumps(data).encode()
        with server_for(callback) as base:
            items = HaloClient(base, "test-token").list_all("/apis/tags")
        self.assertEqual([item["metadata"]["name"] for item in items], ["a", "b"])

    def test_repeated_pagination_is_an_error(self):
        response = json.dumps({"items": [{"metadata": {"name": "a"}}], "hasNext": True}).encode()
        with server_for(lambda m, p, b: (200, {}, response)) as base:
            with self.assertRaisesRegex(ValueError, "Pagination"):
                HaloClient(base, "test-token").list_all("/apis/tags")

    def test_full_publisher_uses_transport_and_verifies_release(self):
        api = FakeHalo()
        def callback(method, path, raw):
            try:
                if "?page=" in path:
                    result = {"items": api.list_all(path.split("?")[0]), "hasNext": False}
                else:
                    result = api.request(method, path, json.loads(raw) if raw else None)
                return 200, {}, json.dumps(result, ensure_ascii=False).encode("utf-8")
            except HaloError as exc:
                return exc.status or 500, {}, b"{}"
        with server_for(callback) as base:
            publisher = Publisher(HaloClient(base, "test-token"), "aerospaceboy")
            self.assertEqual(publisher.run([POST])["published"], ["demo"])
            self.assertEqual(publisher.run([POST])["skipped"], ["demo"])

    def test_rejects_remote_plain_http_and_credential_urls(self):
        for value in ("http://example.com", "https://user:pass@example.com", "https://example.com/path"):
            with self.subTest(value=value), self.assertRaises(ValueError):
                validate_base_url(value)


if __name__ == "__main__":
    unittest.main()
