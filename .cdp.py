"""Mini CDP harness: measure layout overflow on a URL at a given viewport."""
import json, subprocess, sys, time, urllib.request, os, signal

EDGE = r"C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe"
PY_DIR = os.path.dirname(os.path.abspath(__file__))

def main():
    url = sys.argv[1]
    width = int(sys.argv[2]); height = int(sys.argv[3])
    port = 9333
    prof = os.path.join(PY_DIR, ".cdp-profile")
    proc = subprocess.Popen([
        EDGE, "--headless=new", "--disable-gpu", "--hide-scrollbars",
        f"--remote-debugging-port={port}", f"--user-data-dir={prof}",
        "--no-first-run", "about:blank",
    ], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    try:
        ws_url = None
        for _ in range(50):
            try:
                with urllib.request.urlopen(f"http://127.0.0.1:{port}/json/list") as r:
                    tabs = json.load(r)
                for t in tabs:
                    if t.get("type") == "page":
                        ws_url = t["webSocketDebuggerUrl"]; break
                if ws_url: break
            except Exception:
                time.sleep(0.3)
        if not ws_url:
            print("ERR: no CDP target"); return 1

        import websocket
        ws = websocket.create_connection(ws_url, timeout=30)
        mid = 0
        def cmd(method, params=None):
            nonlocal mid
            mid += 1
            ws.send(json.dumps({"id": mid, "method": method, "params": params or {}}))
            while True:
                msg = json.loads(ws.recv())
                if msg.get("id") == mid:
                    return msg.get("result", {})

        cmd("Emulation.setDeviceMetricsOverride",
            {"width": width, "height": height, "deviceScaleFactor": 2, "mobile": True})
        cmd("Page.enable")
        cmd("Page.navigate", {"url": url})
        time.sleep(6)  # let theme JS finish entrance animations

        measure_js = r"""
(() => {
  const iw = window.innerWidth;
  const de = document.documentElement;
  const offenders = [];
  for (const el of document.querySelectorAll('*')) {
    const r = el.getBoundingClientRect();
    if (r.width > 0 && r.right > iw + 2) {
      const cls = (el.className || '').toString().slice(0, 60);
      offenders.push({tag: el.tagName, cls, right: Math.round(r.right), w: Math.round(r.width)});
    }
  }
  // 去重取最外层的少数
  const uniq = [];
  const seen = new Set();
  for (const o of offenders) {
    const k = o.tag + '|' + o.cls;
    if (!seen.has(k)) { seen.add(k); uniq.push(o); }
  }
  return JSON.stringify({
    innerWidth: iw,
    scrollWidth: de.scrollWidth,
    bodyScrollWidth: document.body.scrollWidth,
    hasHorizontalScroll: de.scrollWidth > iw,
    offenders: uniq.slice(0, 15),
    title: document.title,
    body_class: document.body.className
  }, null, 1);
})()
"""
        res = cmd("Runtime.evaluate", {"expression": measure_js, "returnByValue": True})
        val = res.get("result", {}).get("value", "")
        print(val if val else json.dumps(res)[:500])
        ws.close()
    finally:
        try:
            proc.terminate(); proc.wait(timeout=5)
        except Exception:
            pass
    return 0

if __name__ == "__main__":
    sys.exit(main())
