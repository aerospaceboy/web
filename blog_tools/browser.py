"""Isolated Edge CDP runner used by the repository's browser checks."""

import argparse
import base64
import json
import os
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
import time
from urllib.request import urlopen

import websocket

from . import configure_console
ROOT = Path(__file__).resolve().parents[1]


def find_edge():
    candidates = [os.environ.get("EDGE_PATH"), shutil.which("msedge"),
                  r"C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe",
                  r"C:\Program Files\Microsoft\Edge\Application\msedge.exe"]
    for candidate in candidates:
        if candidate and Path(candidate).is_file():
            return str(Path(candidate).resolve())
    raise RuntimeError("Microsoft Edge was not found; set EDGE_PATH to its executable")


class Browser:
    def __init__(self, width, height):
        if width <= 0 or height <= 0:
            raise ValueError("Viewport dimensions must be positive")
        self.width, self.height = width, height
        self.process = self.ws = None
        self.profile = None
        self.mid = 0

    def __enter__(self):
        cache = (ROOT / ".cache/browser").resolve()
        cache.mkdir(parents=True, exist_ok=True)
        self.profile = Path(tempfile.mkdtemp(prefix="edge-", dir=cache)).resolve()
        try:
            self.process = subprocess.Popen(
                [find_edge(), "--headless=new", "--disable-gpu", "--hide-scrollbars",
                 "--remote-debugging-address=127.0.0.1", "--remote-debugging-port=0",
                 f"--user-data-dir={self.profile}", "--no-first-run", "about:blank"],
                stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL,
                creationflags=subprocess.CREATE_NO_WINDOW if os.name == "nt" else 0)
            deadline = time.monotonic() + 20
            active_port = self.profile / "DevToolsActivePort"
            while time.monotonic() < deadline:
                if self.process.poll() is not None:
                    raise RuntimeError("Edge exited before opening a debugging endpoint")
                if active_port.is_file():
                    lines = active_port.read_text().splitlines()
                    if lines and lines[0].isdigit():
                        port = int(lines[0])
                        try:
                            with urlopen(f"http://127.0.0.1:{port}/json/list", timeout=2) as response:
                                tabs = json.load(response)
                        except (OSError, ValueError):
                            time.sleep(0.1)
                            continue
                        target = next((t for t in tabs if t.get("type") == "page"), None)
                        if target:
                            self.ws = websocket.create_connection(
                                target["webSocketDebuggerUrl"], timeout=20, suppress_origin=True)
                            self.command("Page.enable")
                            self.command("Emulation.setDeviceMetricsOverride", {
                                "width": self.width, "height": self.height,
                                "deviceScaleFactor": 2 if self.width < 768 else 1,
                                "mobile": self.width < 768})
                            return self
                time.sleep(0.1)
            raise RuntimeError("Timed out starting Edge")
        except Exception:
            self.__exit__(None, None, None)
            raise

    def command(self, method, params=None):
        self.mid += 1
        self.ws.send(json.dumps({"id": self.mid, "method": method, "params": params or {}}))
        deadline = time.monotonic() + 20
        while time.monotonic() < deadline:
            result = json.loads(self.ws.recv())
            if result.get("id") == self.mid:
                if "error" in result:
                    raise RuntimeError(f"CDP {method} failed")
                return result.get("result", {})
        raise RuntimeError(f"CDP {method} timed out")

    def evaluate(self, expression, *, promise=False):
        result = self.command("Runtime.evaluate", {
            "expression": expression, "returnByValue": True, "awaitPromise": promise})
        if "exceptionDetails" in result:
            raise RuntimeError("Page evaluation failed")
        return result.get("result", {}).get("value")

    def navigate(self, url):
        result = self.command("Page.navigate", {"url": url})
        if result.get("errorText"):
            raise RuntimeError("Page navigation failed: " + result["errorText"])
        deadline = time.monotonic() + 20
        while time.monotonic() < deadline:
            frame = self.command("Page.getFrameTree").get("frameTree", {}).get("frame", {})
            committed = not result.get("loaderId") or frame.get("loaderId") == result["loaderId"]
            if committed and self.evaluate("document.readyState === 'complete' && location.href !== 'about:blank'"):
                self.evaluate("Promise.race([document.fonts.ready.then(() => true), "
                              "new Promise(r => setTimeout(() => r(false), 2000))])", promise=True)
                # Animation frames are only a layout-settling aid. Keep this
                # bounded even when the browser temporarily stops producing them.
                self.evaluate("Promise.race([new Promise(resolve => requestAnimationFrame(() => "
                              "requestAnimationFrame(() => resolve(true)))), "
                              "new Promise(resolve => setTimeout(() => resolve(false), 1000))])", promise=True)
                return
            time.sleep(0.1)
        raise RuntimeError("Page did not finish loading")

    def inject_css(self, path):
        # Preview only: this changes the isolated browser document, never the server.
        css = Path(path).read_text(encoding="utf-8")
        self.evaluate("(() => { for (const s of document.querySelectorAll('style')) {"
                      "if(s.textContent.includes('--ab-radius')) s.remove(); }"
                      "const s = document.createElement('style');"
                      "s.id = 'ab-local-preview'; s.textContent = " + json.dumps(css) +
                      ";document.head.append(s); return true; })()")

    def screenshot(self, path):
        path = Path(path)
        extension = path.suffix.lower()
        image_format = {".png": "png", ".webp": "webp", ".jpg": "jpeg", ".jpeg": "jpeg"}.get(extension)
        if image_format is None:
            raise ValueError("Screenshot output must use .png, .webp, .jpg, or .jpeg")
        params = {"format": image_format}
        if image_format != "png":
            params["quality"] = 88
        result = self.command("Page.captureScreenshot", params)
        if not result.get("data"):
            raise RuntimeError("Edge did not return a screenshot")
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_bytes(base64.b64decode(result["data"], validate=True))

    def __exit__(self, *args):
        if self.ws:
            self.ws.close()
        if self.process and self.process.poll() is None:
            self.process.terminate()
            try:
                self.process.wait(timeout=5)
            except subprocess.TimeoutExpired:
                self.process.kill()
                self.process.wait(timeout=5)
        cache = (ROOT / ".cache/browser").resolve()
        if self.profile and self.profile.is_relative_to(cache) and self.profile != cache:
            # Each directory is unique to this run; never touch the user's browser profile.
            shutil.rmtree(self.profile, ignore_errors=True)


MEASURE = r"""(() => {
  const width = document.documentElement.clientWidth;
  const offenders = [...document.querySelectorAll('body *')].map(el => {
    const r = el.getBoundingClientRect(), s = getComputedStyle(el);
    return {tag: el.tagName, cls: String(el.className || '').slice(0, 80),
      left: Math.round(r.left), right: Math.round(r.right), width: Math.round(r.width), visible:
      !!el.getClientRects().length && s.visibility !== 'hidden' && s.display !== 'none'};
  }).filter(r => r.visible && r.width > 0 && r.left < width && r.right > width + 2).slice(0, 20);
  return {title: document.title, url: location.href, innerWidth: innerWidth,
    clientWidth: width, scrollWidth: document.documentElement.scrollWidth,
    hasHorizontalScroll: document.documentElement.scrollWidth > width + 1,
    articleCards: document.querySelectorAll('#recent-posts .recent-post-item').length,
    articleFontSize: document.querySelector('#article-container') ?
      getComputedStyle(document.querySelector('#article-container')).fontSize : null,
    globalStyle: !!document.querySelector('#aerospaceboy-global-style'),
    localPreview: !!document.querySelector('#ab-local-preview'), offenders};
})()"""


def main(mode="measure", argv=None):
    configure_console()
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("url")
    parser.add_argument("width", type=int)
    parser.add_argument("height", type=int)
    if mode in {"screenshot", "evaluate"}:
        parser.add_argument("output" if mode == "screenshot" else "expression")
    parser.add_argument("--inject-css", type=Path)
    parser.add_argument("--settle-seconds", type=float, default=2)
    parser.add_argument("--check", action="store_true", help="Fail on horizontal overflow")
    args = parser.parse_args(argv)
    try:
        if not 0 <= args.settle_seconds <= 10:
            raise ValueError("settle-seconds must be between 0 and 10")
        with Browser(args.width, args.height) as browser:
            browser.navigate(args.url)
            if args.inject_css:
                browser.inject_css(args.inject_css)
            time.sleep(args.settle_seconds)
            if mode == "screenshot":
                browser.screenshot(args.output)
                result = {"screenshot": str(Path(args.output).resolve())}
            else:
                result = browser.evaluate(args.expression if mode == "evaluate" else MEASURE)
        print(json.dumps(result, ensure_ascii=False, indent=2))
        return 1 if args.check and isinstance(result, dict) and result.get("hasHorizontalScroll") else 0
    except (RuntimeError, OSError, ValueError, websocket.WebSocketException) as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 1
