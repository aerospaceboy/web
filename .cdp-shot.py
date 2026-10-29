"""CDP screenshot at mobile metrics."""
import json, subprocess, sys, time, urllib.request, os, base64

EDGE = r"C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe"

def main():
    url, width, height, out = sys.argv[1], int(sys.argv[2]), int(sys.argv[3]), sys.argv[4]
    port = 9335
    prof = os.path.join(os.getcwd(), ".cdp-profile3")
    proc = subprocess.Popen([EDGE, "--headless=new", "--disable-gpu", "--hide-scrollbars",
        f"--remote-debugging-port={port}", f"--user-data-dir={prof}", "--no-first-run", "about:blank"],
        stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    try:
        ws_url = None
        for _ in range(50):
            try:
                with urllib.request.urlopen(f"http://127.0.0.1:{port}/json/list") as r:
                    for t in json.load(r):
                        if t.get("type") == "page":
                            ws_url = t["webSocketDebuggerUrl"]; break
                if ws_url: break
            except Exception:
                time.sleep(0.3)
        import websocket
        ws = websocket.create_connection(ws_url, timeout=30)
        mid = 0
        def cmd(method, params=None):
            nonlocal mid
            mid += 1
            ws.send(json.dumps({"id": mid, "method": method, "params": params or {}}))
            while True:
                m = json.loads(ws.recv())
                if m.get("id") == mid:
                    return m.get("result", {})
        dsf = 2 if width < 768 else 1
        cmd("Emulation.setDeviceMetricsOverride",
            {"width": width, "height": height, "deviceScaleFactor": dsf, "mobile": width < 768})
        cmd("Page.enable")
        cmd("Page.navigate", {"url": url})
        time.sleep(7)
        shot = cmd("Page.captureScreenshot", {"format": "png"})
        data = shot.get("data", "")
        if not data:
            print("NO_SCREENSHOT"); return 1
        with open(out, "wb") as f:
            f.write(base64.b64decode(data))
        print("saved", out, len(data))
        ws.close()
    finally:
        try:
            proc.terminate(); proc.wait(timeout=5)
        except Exception:
            pass
    return 0

if __name__ == "__main__":
    sys.exit(main())
