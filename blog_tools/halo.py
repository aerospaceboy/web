"""Bounded Halo JSON transport. Only read requests are automatically retried."""

import json
from http.client import HTTPException
import time
from urllib.error import HTTPError, URLError
from urllib.parse import urlencode, urlsplit
from urllib.request import HTTPRedirectHandler, Request, build_opener


class HaloError(RuntimeError):
    def __init__(self, method, path, status=None):
        self.status = status
        # Never include response bodies, authorization headers, or transport exceptions.
        super().__init__(f"{method} {path}: HTTP {status}" if status else
                         f"{method} {path}: connection failed; outcome may be unknown")


class NoRedirect(HTTPRedirectHandler):
    def redirect_request(self, req, fp, code, msg, headers, newurl):
        return None


def validate_base_url(value):
    parts = urlsplit(value)
    local = parts.hostname in {"localhost", "127.0.0.1", "::1"}
    if (not parts.hostname or parts.username or parts.password or parts.query or
            parts.fragment or parts.path not in {"", "/"} or
            not (parts.scheme == "https" or parts.scheme == "http" and local)):
        raise ValueError("base_url must be an HTTPS origin (HTTP is allowed for loopback tests)")
    return value.rstrip("/")


class HaloClient:
    def __init__(self, base_url, token, *, timeout=20, read_attempts=3, sleep=time.sleep):
        self.base_url = validate_base_url(base_url)
        if not token or any(c in token for c in "\r\n"):
            raise ValueError("HALO_PAT is missing or invalid")
        if timeout <= 0 or read_attempts < 1:
            raise ValueError("timeout and read_attempts must be positive")
        self._token = token
        self.timeout = timeout
        self.read_attempts = read_attempts
        self.sleep = sleep
        self.opener = build_opener(NoRedirect())

    def request(self, method, path, data=None):
        if not path.startswith("/apis/") or path.startswith("//"):
            raise ValueError("Only relative Halo API paths are supported")
        attempts = self.read_attempts if method == "GET" else 1
        payload = None if data is None else json.dumps(data, ensure_ascii=False).encode("utf-8")
        headers = {"Authorization": "Bearer " + self._token, "Accept": "application/json"}
        if payload is not None:
            headers["Content-Type"] = "application/json; charset=utf-8"
        for attempt in range(attempts):
            request = Request(self.base_url + path, data=payload, headers=headers, method=method)
            try:
                with self.opener.open(request, timeout=self.timeout) as response:
                    raw = response.read()
                if not raw:
                    return None
                try:
                    return json.loads(raw)
                except (ValueError, UnicodeDecodeError):
                    raise HaloError(method, path, 502) from None
            except HTTPError as exc:
                status = exc.code
                exc.close()
                if attempt + 1 < attempts and (status == 429 or status >= 500):
                    self.sleep(min(0.25 * 2 ** attempt, 2))
                    continue
                raise HaloError(method, path, status) from None
            except (URLError, TimeoutError, OSError, HTTPException):
                if attempt + 1 < attempts:
                    self.sleep(min(0.25 * 2 ** attempt, 2))
                    continue
                raise HaloError(method, path) from None

    def list_all(self, path):
        items = []
        names = set()
        for page in range(1, 1001):
            separator = "&" if "?" in path else "?"
            result = self.request("GET", path + separator + urlencode({"page": page, "size": 100}))
            if not isinstance(result, dict) or not isinstance(result.get("items"), list):
                raise ValueError("Invalid paginated Halo response")
            batch = result["items"]
            for item in batch:
                name = item.get("metadata", {}).get("name")
                if not name or name in names:
                    raise ValueError("Pagination repeated an item; retry against a stable site")
                names.add(name)
            items.extend(batch)
            if result.get("hasNext") is False:
                return items
            if "hasNext" not in result and (not batch or len(batch) < 100):
                return items
            if not batch:
                raise ValueError("Halo returned an empty page with hasNext=true")
        raise ValueError("Halo pagination exceeded 1000 pages")
