"""Check actual Halo header links for overlap across desktop and zoomed viewports."""

import argparse
from functools import partial
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
import json
from pathlib import Path
import re
import tempfile
import time
from threading import Thread
from urllib.request import urlopen
from urllib.parse import urlsplit

from . import configure_console
from .browser import Browser
from .build import ROOT, build


MEASURE = r"""(() => {
    const visible = e => !!e.getClientRects().length &&
        getComputedStyle(e).display !== 'none' && getComputedStyle(e).visibility !== 'hidden';
    const brand = document.querySelector('#blog_name');
    const tools = document.querySelector('#nav-right');
    const nav = document.querySelector('#nav');
    if (!brand || !tools || !nav) return {missingHeader: true};
    const b = brand.getBoundingClientRect(), t = tools.getBoundingClientRect();
    const group = document.querySelector('#nav-group');
    const menu = document.querySelector('#menus > .menus_items');
    const links = [...document.querySelectorAll('#menus > .menus_items > .menus_item > a')].filter(visible);
    const rectangles = links.map(e => e.getBoundingClientRect());
    const first = rectangles.length ? Math.min(...rectangles.map(r => r.left)) : null;
    const last = rectangles.length ? Math.max(...rectangles.map(r => r.right)) : null;
    const toggle = document.querySelector('#toggle-menu');
    const copied = [...document.querySelectorAll('#ab-mobile-navigation a')].map(e => new URL(e.href).pathname);
    const expected = [...document.querySelectorAll('#menus a.site-page[href]')]
        .filter(e => ['http:', 'https:'].includes(new URL(e.href).protocol)).map(e => new URL(e.href).pathname);
    return {width: innerWidth, visibleLinks: links.length, navClass: nav.className,
        geometry: {brand: [b.left, b.right], tools: [t.left, t.right], first, last,
            groupWidth: group.clientWidth, menuWidth: menu.scrollWidth,
            menuBox: document.querySelector('#menus').getBoundingClientRect().toJSON(),
            styles: ['#nav-group', '#menus', '#menus > .menus_items'].map(selector => {
                const s = getComputedStyle(document.querySelector(selector));
                return {selector, display:s.display, position:s.position, width:s.width, flex:s.flex,
                    padding:s.padding, margin:s.margin, transform:s.transform, left:s.left, gap:s.gap,
                    justify:s.justifyContent, visibility:s.visibility};
            }),
            toolChildren: [...tools.children].map(e => ({id:e.id, width:e.getBoundingClientRect().width,
                marginLeft:getComputedStyle(e).marginLeft, display:getComputedStyle(e).display}))},
        brandOverlap: rectangles.length > 0 && first < b.right - 1,
        toolsOverlap: rectangles.length > 0 && last > t.left + 1,
        brandToolsOverlap: b.right > t.left + 1,
        wrapped: rectangles.some(r => r.top < b.top - 1 || r.bottom > b.bottom + 1),
        compactToggleVisible: !!toggle && visible(toggle),
        sidebarComplete: expected.every(path => copied.includes(path) ||
            [...document.querySelectorAll('#sidebar-menus a[href]')].some(a =>
                new URL(a.href).pathname === path && !a.closest('#ab-mobile-navigation'))),
        horizontalOverflow: document.documentElement.scrollWidth > innerWidth + 1};
})()"""


def check(browser, output, widths):
    results = []
    for width in widths:
        browser.command('Emulation.setDeviceMetricsOverride', {
            'width': width, 'height': 900, 'deviceScaleFactor': 1, 'mobile': False})
        browser.evaluate('new Promise(r => setTimeout(r, 250))', promise=True)
        row = browser.evaluate(MEASURE)
        row['ok'] = (not any(row.get(k, False) for k in
                            ['missingHeader', 'brandOverlap', 'toolsOverlap', 'brandToolsOverlap', 'wrapped'])
                     and row.get('sidebarComplete', False)
                     and (row.get('visibleLinks', 0) > 0 or row.get('compactToggleVisible', False)))
        results.append(row)
        if width in [1920, 1200, 900, 390]:
            browser.screenshot(output.parent / (output.stem + '-' + str(width) + '.png'))
    return results


def check_train_hover(browser):
    snapshot = """(() => {
        const link = document.querySelector('#travellings_button a');
        if (!link) return {missing:true};
        const box = link.getBoundingClientRect();
        return {x:box.x, y:box.y, width:box.width, height:box.height,
            mode:document.querySelector('#nav').classList.contains('ab-nav-compact') ? 'compact' : 'wide'};
    })()"""
    results = []
    for width in [800, 849, 900, 1100, 1300]:
        browser.command('Input.dispatchMouseEvent', {'type':'mouseMoved', 'x':20, 'y':500})
        browser.command('Emulation.setDeviceMetricsOverride', {
            'width':width, 'height':900, 'deviceScaleFactor':1, 'mobile':False})
        browser.evaluate('new Promise(r=>setTimeout(r,450))', promise=True)
        before = browser.evaluate(snapshot)
        if before.get('missing') or not before['width']:
            results.append({'width':width, 'ok':False, 'reason':'train_button_missing_or_hidden'})
            continue
        browser.command('Input.dispatchMouseEvent', {
            'type':'mouseMoved', 'x':before['x']+before['width']/2, 'y':before['y']+before['height']/2})
        samples = []
        for _ in range(20):
            samples.append(browser.evaluate(snapshot))
            time.sleep(.1)
        movement = max(abs(row['x'] - before['x']) for row in samples)
        modes = sorted({row['mode'] for row in samples})
        results.append({'width':width, 'before_mode':before['mode'], 'hover_modes':modes,
                        'button_movement':round(movement, 2),
                        'ok':modes == [before['mode']] and movement <= 1})
    return results


def main():
    configure_console()
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--url', default='https://aerospaceboy.site/')
    parser.add_argument('--local-bundle', action='store_true', help='Preview current sources without changing the site')
    parser.add_argument('--output', type=Path, default=ROOT / 'reports/header-check.json')
    parser.add_argument('--widths', nargs='+', type=int, default=[1920, 1600, 1440, 1366, 1280, 1200, 1100, 1000, 900, 800, 769, 768, 390, 1200, 1920])
    parser.add_argument('--train-hover', action='store_true', help='Assert train hover cannot move the button or switch header mode')
    args = parser.parse_args()
    args.output.parent.mkdir(parents=True, exist_ok=True)
    with tempfile.TemporaryDirectory(prefix='header-', dir=ROOT / '.cache') as directory:
        directory = Path(directory)
        server = None
        worker = None
        target = args.url
        if args.local_bundle:
            with urlopen(args.url, timeout=20) as response:
                html = response.read().decode('utf-8')
            build(directory)
            # Preserve the deployed cascade/script order; prepending to <head> would
            # put the customization before the theme and test a different layout.
            bundle = (directory / 'global-head.html').read_text(encoding='utf-8')
            for tag, identifier in [('style', 'aerospaceboy-global-style'),
                                    ('script', 'aerospaceboy-mobile-navigation-script')]:
                pattern = rf'<{tag}\b[^>]*id="{identifier}"[^>]*>[\s\S]*?</{tag}>'
                replacement = re.search(pattern, bundle).group()
                html, count = re.subn(pattern, lambda match: replacement, html, count=1)
                if count != 1:
                    raise RuntimeError('Expected deployed customization block was not found')
            html = html.replace('<head>', '<head><base href="https://aerospaceboy.site/">', 1)
            (directory / 'index.html').write_text(html, encoding='utf-8')
            preview_path = urlsplit(args.url).path or '/'
            snapshot = html.encode('utf-8')
            class QuietHandler(SimpleHTTPRequestHandler):
                def log_message(self, *args):
                    pass
                def do_GET(self):
                    if self.path.split('?', 1)[0] == preview_path:
                        self.send_response(200)
                        self.send_header('Content-Type', 'text/html; charset=utf-8')
                        self.send_header('Content-Length', str(len(snapshot)))
                        self.end_headers()
                        self.wfile.write(snapshot)
                    else:
                        super().do_GET()
            server = ThreadingHTTPServer(('127.0.0.1', 0), partial(QuietHandler, directory=str(directory)))
            worker = Thread(target=server.serve_forever, daemon=True)
            worker.start()
            target = f'http://127.0.0.1:{server.server_port}{preview_path}'
        try:
            with Browser(1920, 900) as browser:
                browser.navigate(target)
                rows = check(browser, args.output, args.widths)
                hover_rows = check_train_hover(browser) if args.train_hover else []
        finally:
            if server:
                server.shutdown()
                server.server_close()
                worker.join()
    result = {'ok': all(row['ok'] for row in rows + hover_rows), 'preview': args.local_bundle,
              'viewports': rows, 'train_hover':hover_rows}
    args.output.write_text(json.dumps(result, indent=2) + '\n', encoding='utf-8')
    print(json.dumps({'ok': result['ok'], 'preview': args.local_bundle,
                      'cases': len(rows), 'failed_widths': [r['width'] for r in rows if not r['ok']],
                      'train_hover':hover_rows}))
    raise SystemExit(0 if result['ok'] else 1)


if __name__ == '__main__':
    main()
