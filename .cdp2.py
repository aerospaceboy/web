import json, subprocess, sys, time, urllib.request, os
EDGE = r"C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe"
def main():
    url, width, height = sys.argv[1], int(sys.argv[2]), int(sys.argv[3])
    port = 9334
    prof = os.path.join(os.getcwd(), ".cdp-profile2")
    proc = subprocess.Popen([EDGE, "--headless=new", "--disable-gpu", "--hide-scrollbars",
        f"--remote-debugging-port={port}", f"--user-data-dir={prof}", "--no-first-run", "about:blank"],
        stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    try:
        ws_url = None
        for _ in range(50):
            try:
                with urllib.request.urlopen(f"http://127.0.0.1:{port}/json/list") as r:
                    for t in json.load(r):
                        if t.get("type") == "page": ws_url = t["webSocketDebuggerUrl"]; break
                if ws_url: break
            except Exception: time.sleep(0.3)
        import websocket
        ws = websocket.create_connection(ws_url, timeout=30)
        mid = 0
        def cmd(method, params=None):
            nonlocal mid
            mid += 1
            ws.send(json.dumps({"id": mid, "method": method, "params": params or {}}))
            while True:
                m = json.loads(ws.recv())
                if m.get("id") == mid: return m.get("result", {})
        cmd("Emulation.setDeviceMetricsOverride", {"width": width, "height": height, "deviceScaleFactor": 2, "mobile": True})
        cmd("Page.enable"); cmd("Page.navigate", {"url": url}); time.sleep(6)
        expr = sys.argv[4]
        res = cmd("Runtime.evaluate", {"expression": expr, "returnByValue": True})
        print(json.dumps(res.get("result", {}).get("value", res), ensure_ascii=False, indent=1))
        ws.close()
    finally:
        try: proc.terminate(); proc.wait(timeout=5)
        except Exception: pass
if __name__ == "__main__": sys.exit(main())
