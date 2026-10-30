"""Check social destinations and saved preferences in isolated Edge, optionally before deploy."""

import argparse
from functools import partial
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
import json
from pathlib import Path
import re
import tempfile
from threading import Thread
from urllib.request import urlopen

from . import configure_console
from .browser import Browser
from .build import build
from .check_motion import run_motion_checks
from .publish import ROOT

BASE = 'https://aerospaceboy.site'
POST = '/archives/study-roadmap'


def run(browser, base, output):
    browser.navigate(base + '/')
    initial = browser.evaluate("""(() => ({
        github:[...document.querySelectorAll('#ab-github-button a,.ab-hero-socials a[target],.ab-profile-links a[target],.ab-sidebar-socials a[target]')]
            .map(a=>({href:a.href,target:a.target,rel:a.rel})),
        rss:document.querySelector('.ab-hero-socials a[href="/rss.xml"]')?.getAttribute('href'),
        shortcuts:document.querySelectorAll('#ab-explore-card a').length,
        hero:document.querySelectorAll('.ab-hero-socials').length,
        resume:document.querySelectorAll('.ab-hero-copy .ab-resume-link').length,
        preference:document.querySelectorAll('#ab-preferences-card').length,
        hashes:[...document.querySelectorAll('[data-ab-sha256]')].map(e=>e.dataset.abSha256),
        overflow:document.documentElement.scrollWidth>innerWidth+1
    }))()""")
    assert len(initial['github']) == 4, initial
    assert all(a['href'] == 'https://github.com/aerospaceboy' and a['target'] == '_blank'
               and {'noopener', 'noreferrer'} <= set(a['rel'].split()) for a in initial['github']), initial
    assert initial['rss'] == '/rss.xml' and initial['shortcuts'] == 4, initial
    assert initial['hero'] == initial['resume'] == initial['preference'] == 1, initial
    assert not initial['overflow'], initial
    motion = run_motion_checks(browser, base, output)
    browser.screenshot(output.parent / (output.stem + '-desktop.png'))
    browser.evaluate("document.querySelector('#content-inner').scrollIntoView()")
    browser.evaluate("new Promise(r=>setTimeout(r,400))", promise=True)
    browser.screenshot(output.parent / (output.stem + '-cards.png'))
    light = browser.evaluate("""(() => {
        document.documentElement.dataset.theme='light';
        const card=document.querySelector('#ab-preferences-card'), c=getComputedStyle(card);
        return {color:c.color,background:c.backgroundColor,links:document.querySelectorAll('.ab-profile-links a').length};
    })()""")
    assert light['color'] != light['background'] and light['links'] == 2, light
    browser.evaluate("new Promise(r=>setTimeout(r,1000))", promise=True)
    light = browser.evaluate("""(() => {
        const c=getComputedStyle(document.querySelector('#ab-preferences-card'));
        return {color:c.color,background:c.backgroundColor,theme:document.documentElement.dataset.theme,
            profileHeight:document.querySelector('.ab-profile-card').getBoundingClientRect().height,
            profileMin:getComputedStyle(document.querySelector('.ab-profile-card .card-content')).minHeight,
            descriptionColor:getComputedStyle(document.querySelector('.ab-profile-card .author-info__description')).color,
            surface:getComputedStyle(document.documentElement).getPropertyValue('--ab-surface')};
    })()""")
    assert light['theme'] == 'light' and light['surface'].strip() == 'rgba(250, 249, 255, .96)', light
    assert light['profileHeight'] < 330 and light['descriptionColor'] == 'rgb(85, 71, 101)', light
    browser.screenshot(output.parent / (output.stem + '-light.png'))
    browser.evaluate("document.documentElement.dataset.theme='dark'")
    browser.evaluate("""document.querySelector('#ab-preferences-card [data-ab-font="larger"]').click();
        document.querySelector('#ab-preferences-card [data-ab-calm]').click();
        for(let i=0;i<5;i++) document.dispatchEvent(new Event('pjax:complete'));""")
    repeat = browser.evaluate("""({
        github:document.querySelectorAll('#ab-github-button').length,
        hub:document.querySelectorAll('#ab-sidebar-hub').length,
        card:document.querySelectorAll('#ab-explore-card').length,
        hero:document.querySelectorAll('.ab-hero-socials').length,
        resume:document.querySelectorAll('.ab-hero-copy .ab-resume-link').length,
        pointer:document.querySelectorAll('#ab-pointer-light').length,
        animation:getComputedStyle(document.querySelector('.ab-stars-depth-0')).animationName,
        saved:JSON.parse(localStorage.getItem('ab:reader:v1'))})""")
    assert all(repeat[k] == 1 for k in ['github', 'hub', 'card', 'hero', 'resume']), repeat
    assert repeat['pointer'] == 0 and repeat['animation'] == 'none', repeat
    assert repeat['saved'] == {'font':'larger', 'calm':True}, repeat

    browser.navigate(base + POST)
    post = browser.evaluate("""({
        font:getComputedStyle(document.querySelector('#article-container')).fontSize,
        settings:document.querySelectorAll('#ab-article-settings').length,
        extraSidebarCards:document.querySelectorAll('#ab-explore-card,#ab-preferences-card').length,
        calm:document.documentElement.classList.contains('ab-calm-mode'),
        selected:[...document.querySelectorAll('[data-ab-font="larger"]')].every(b=>b.getAttribute('aria-pressed')==='true'),
        overflow:document.documentElement.scrollWidth>innerWidth+1})""")
    assert post['font'] == '20px' and post['settings'] == 1 and post['calm'] and post['selected'] and post['extraSidebarCards'] == 0, post
    assert not post['overflow'], post
    browser.evaluate("document.querySelector('#ab-article-settings').open=true;document.querySelector('#ab-article-settings').scrollIntoView()")
    browser.screenshot(output.parent / (output.stem + '-article.png'))
    browser.evaluate("document.querySelector('#ab-article-settings [data-ab-font=large]').click()")
    assert browser.evaluate("getComputedStyle(document.querySelector('#article-container')).fontSize") == '18px'
    browser.command('Page.reload')
    browser.evaluate("new Promise(r=>setTimeout(r,600))", promise=True)
    assert browser.evaluate("document.documentElement.dataset.abReadingSize") == 'large'
    browser.navigate(base + '/resume')
    resume = browser.evaluate("""({
        size:getComputedStyle(document.querySelector('#article-container')).fontSize,
        class:document.querySelector('#article-container').className,
        toolbar:document.querySelectorAll('#ab-article-settings').length,
        sections:document.querySelectorAll('.ab-resume-section').length})""")
    assert resume['size'] == '16.5px' and 'ab-readable-post' not in resume['class'] and resume['toolbar'] == 0, resume

    browser.command('Emulation.setDeviceMetricsOverride', {'width':390,'height':844,'deviceScaleFactor':1,'mobile':True})
    browser.navigate(base + '/')
    browser.evaluate("document.querySelector('#toggle-menu a').click()")
    mobile = browser.evaluate("""({overflow:document.documentElement.scrollWidth>innerWidth+1,
        hub:document.querySelectorAll('#ab-sidebar-hub').length,
        social:document.querySelectorAll('.ab-sidebar-socials a').length,
        selected:document.querySelector('#ab-sidebar-hub [data-ab-font=large]').getAttribute('aria-pressed'),
        width:document.querySelector('#sidebar-menus').getBoundingClientRect().width})""")
    assert not mobile['overflow'] and mobile['hub'] == 1 and mobile['social'] == 2 and mobile['selected'] == 'true', mobile
    browser.screenshot(output.parent / (output.stem + '-mobile-menu.png'))
    browser.navigate(base + '/')
    browser.screenshot(output.parent / (output.stem + '-mobile.png'))
    return {'social':initial, 'motion':motion, 'light':light, 'repeat_pjax_and_calm':repeat, 'post_preferences':post, 'resume_unchanged':resume, 'mobile':mobile}


def main():
    configure_console()
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--local-bundle', action='store_true')
    parser.add_argument('--output', type=Path, default=ROOT / 'reports/site-hub-check.json')
    args = parser.parse_args()
    args.output.parent.mkdir(parents=True, exist_ok=True)
    with tempfile.TemporaryDirectory(prefix='site-hub-', dir=ROOT / '.cache') as directory:
        directory = Path(directory)
        server = worker = None
        base = BASE
        if args.local_bundle:
            build(directory)
            bundle = (directory / 'global-head.html').read_text(encoding='utf-8')
            snapshots = {}
            for path in ['/', POST, '/resume']:
                with urlopen(BASE + path, timeout=20) as response:
                    html = response.read().decode('utf-8')
                for tag, identifier in [('style','aerospaceboy-global-style'), ('script','aerospaceboy-mobile-navigation-script')]:
                    pattern = rf'<{tag}\b[^>]*id="{identifier}"[^>]*>[\s\S]*?</{tag}>'
                    replacement = re.search(pattern, bundle).group()
                    html, count = re.subn(pattern, lambda match:replacement, html, count=1)
                    assert count == 1, identifier
                snapshots[path] = html.replace('<head>', f'<head><base href="{BASE}/">', 1).encode('utf-8')
            class Handler(SimpleHTTPRequestHandler):
                def log_message(self, *args):
                    pass
                def do_GET(self):
                    snapshot = snapshots.get(self.path.split('?',1)[0])
                    if snapshot is None:
                        return super().do_GET()
                    self.send_response(200)
                    self.send_header('Content-Type','text/html; charset=utf-8')
                    self.send_header('Content-Length',str(len(snapshot)))
                    self.end_headers()
                    self.wfile.write(snapshot)
            server = ThreadingHTTPServer(('127.0.0.1',0), partial(Handler,directory=str(directory)))
            worker = Thread(target=server.serve_forever,daemon=True);worker.start()
            base = f'http://127.0.0.1:{server.server_port}'
        try:
            with Browser(1440,1000) as browser:
                result = run(browser,base,args.output)
        finally:
            if server:
                server.shutdown();server.server_close();worker.join()
    args.output.write_text(json.dumps({'ok':True,'preview':args.local_bundle,**result},ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    print(json.dumps({'ok':True,'preview':args.local_bundle,'checks':list(result)}))


if __name__ == '__main__':
    main()
