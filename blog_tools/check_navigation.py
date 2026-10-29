"""Run the actual navigation bundle in Edge against flat and mixed-menu fixtures."""

import json
from pathlib import Path
import tempfile
import time
from functools import partial
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
from threading import Thread

from . import configure_console
from .browser import Browser
from .build import build
from .publish import ROOT


def main():
    configure_console()
    cache = ROOT / ".cache"
    cache.mkdir(exist_ok=True)
    with tempfile.TemporaryDirectory(prefix="navigation-", dir=cache) as directory:
        directory = Path(directory)
        build(directory)
        bundle = (directory / "global-head.html").read_text(encoding="utf-8")
        fixture = directory / "fixture.html"
        fixture.write_text('<!doctype html><html><head><meta charset="utf-8">'
            '<meta name="viewport" content="width=device-width,initial-scale=1">'
            '<script>var navFn={switchDarkMode(){document.documentElement.dataset.theme='
            'document.documentElement.dataset.theme==="dark"?"light":"dark";}};'
            'var heo={hideLoading(){document.querySelector("#loading-box").classList.add("loaded");}};'
            '</script>' + bundle + '</head><body>'
            '<header id="menus"><a class="site-page" href="/">首页</a>'
            '<a class="site-page" href="/projects">项目</a>'
            '<a class="site-page" href="/about">关于</a>'
            '<a class="site-page" href="/projects">重复链接</a>'
            '<a class="site-page" href="javascript:void(0)">分组</a></header>'
            '<aside id="sidebar-menus"><a href="/about">原有关于入口</a>'
            '<a class="darkmode_switchbutton" onclick="rm.switchDarkMode()">显示模式</a></aside>'
            '<div class="comment-randomInfo"><a href="/privacy">隐私政策</a></div>'
            '<button class="post-copyright-copybtn" onclick="rm.copyPageUrl()">复制</button>'
            '<div id="recent-posts"><img class="post_bg" width="10" height="10" '
            'data-lazy-src="data:image/gif;base64,R0lGODlhAQABAIAAAAAAAP///ywAAAAAAQABAAACAUwAOw=="></div>'
            '</body></html>', encoding="utf-8")
        class QuietHandler(SimpleHTTPRequestHandler):
            def log_message(self, *args):
                pass
        server = ThreadingHTTPServer(('127.0.0.1', 0), partial(QuietHandler, directory=str(directory)))
        worker = Thread(target=server.serve_forever, daemon=True)
        worker.start()
        try:
            run_browser_checks(server.server_port)
            run_pointer_checks(server.server_port)
        finally:
            server.shutdown()
            server.server_close()
            worker.join()
    print(json.dumps({"ok": True, "scenarios": ["flat_and_mixed_menu", "repeat_pjax", "menu_update", "native_menu_recovery", "theme_toggle", "disabled_widgets", "native_loading_preserved", "privacy_link", "copy_success", "copy_denied", "visible_cover_priority", "cover_fallback", "space_hero_pjax", "space_hero_page_exit", "space_hero_reduced_motion", "space_hero_light_mode", "nebula_image_fallback", "light_profile_contrast", "pointer_tracks_and_trails", "pointer_click_through", "pointer_pjax_pool_bound", "pointer_reduced_motion", "pointer_touch_disabled"]}))


def run_browser_checks(port):
    with Browser(390, 844) as browser:
        browser.command('Emulation.setTouchEmulationEnabled', {'enabled': True, 'maxTouchPoints': 1})
        browser.navigate(f'http://127.0.0.1:{port}/fixture.html')
        assert browser.evaluate("document.querySelectorAll('#ab-pointer-light').length") == 0
        measure = "({count:document.querySelectorAll('#ab-mobile-navigation').length," \
            "paths:[...document.querySelectorAll('#ab-mobile-navigation a')].map(a=>new URL(a.href).pathname)})"
        initial = browser.evaluate(measure)
        assert initial == {"count": 1, "paths": ["/", "/projects"]}, initial
        browser.evaluate("document.dispatchEvent(new Event('pjax:complete'));true")
        repeated = browser.evaluate(measure)
        assert repeated == initial, repeated
        browser.evaluate("document.querySelector('#menus').insertAdjacentHTML('beforeend',"
                         "'<a class=\"site-page\" href=\"/archives\">文章</a>');"
                         "document.dispatchEvent(new Event('pjax:complete'));true")
        updated = browser.evaluate(measure)
        assert updated["paths"] == ["/", "/projects", "/archives"], updated
        browser.evaluate("document.querySelector('#sidebar-menus').insertAdjacentHTML('beforeend',"
                         "'<a href=\"/\">首页</a><a href=\"/projects\">项目</a><a href=\"/archives\">文章</a>');"
                         "document.dispatchEvent(new Event('pjax:complete'));true")
        native = browser.evaluate(measure)
        assert native == {"count": 0, "paths": []}, native
        browser.evaluate("document.documentElement.dataset.theme='dark';"
                         "document.querySelector('.darkmode_switchbutton').click();true")
        assert browser.evaluate("document.documentElement.dataset.theme") == "light"
        browser.evaluate("document.querySelector('.darkmode_switchbutton').click();true")
        assert browser.evaluate("document.documentElement.dataset.theme") == "dark"
        assert browser.evaluate("heo.hideLoading();rm.hideRightMenu();true") is True
        browser.evaluate("document.body.insertAdjacentHTML('beforeend','<div id=\"loading-box\"></div>');heo.hideLoading();true")
        assert browser.evaluate("document.querySelector('#loading-box').classList.contains('loaded')")
        assert browser.evaluate("document.querySelector('.comment-randomInfo a').getAttribute('href')") == '/privacy-policy'
        browser.evaluate("Object.defineProperty(navigator,'clipboard',{configurable:true,value:{writeText:async text=>{document.body.dataset.copied=text}}});document.querySelector('.post-copyright-copybtn').click();true")
        assert browser.evaluate("document.body.dataset.copied === location.href && document.querySelector('.post-copyright-copybtn').getAttribute('aria-label') === '文章链接已复制'")
        assert browser.evaluate("(async()=>{navigator.clipboard.writeText=async()=>{throw new Error('denied')};return await rm.copyPageUrl()})()", promise=True) is False
        assert browser.evaluate("document.querySelector('.post-copyright-copybtn').getAttribute('aria-label')") == '复制失败，请手动复制地址栏'
        assert browser.evaluate("(()=>{const i=document.querySelector('img.post_bg');return i.loading==='eager' && i.fetchPriority==='high' && i.complete && i.naturalWidth===1})()")
        fallback = browser.evaluate("(()=>{const i=document.querySelector('img.post_bg');i.dispatchEvent(new Event('error'));return {path:new URL(i.src).pathname,lazy:i.hasAttribute('data-lazy-src')}})()")
        assert fallback == {'path': '/upload/ab-cover-default-v1.webp', 'lazy': False}, fallback
        assert browser.evaluate("document.dispatchEvent(new Event('pjax:complete'));document.querySelectorAll('#ab-mobile-navigation').length") == 0
        browser.evaluate("document.body.insertAdjacentHTML('beforeend','<div id=\"home_top\"><div id=\"recent-top-post-group\"><div class=\"banners-title-big\">测试品牌</div><div class=\"banners-title-small\">测试描述</div></div></div>');document.dispatchEvent(new Event('pjax:complete'));true")
        browser.evaluate("document.dispatchEvent(new Event('pjax:complete'));window.__abInstallSpaceHero();true")
        hero = browser.evaluate("({count:document.querySelectorAll('#ab-space-hero').length,title:document.querySelector('#ab-space-title').textContent,description:document.querySelector('.ab-hero-description').textContent,original:getComputedStyle(document.querySelector('#recent-top-post-group')).display,paths:[...document.querySelectorAll('.ab-hero-actions a')].map(a=>new URL(a.href).pathname),buttons:[...document.querySelectorAll('.ab-hero-actions a')].every(a=>a.getBoundingClientRect().height>=44)})")
        assert hero == {'count': 1, 'title': '测试品牌', 'description': '测试描述', 'original': 'none', 'paths': ['/projects', '/archives'], 'buttons': True}, hero
        assert browser.evaluate("document.querySelectorAll('.ab-starfield circle').length") == 150
        browser.evaluate("document.querySelector('.ab-nebula-image')?.dispatchEvent(new Event('error'));true")
        assert browser.evaluate("document.querySelectorAll('.ab-nebula-image').length") == 0
        browser.command('Emulation.setEmulatedMedia', {'features': [{'name': 'prefers-reduced-motion', 'value': 'reduce'}]})
        assert browser.evaluate("getComputedStyle(document.querySelector('.ab-stars-depth-0')).animationName") == 'none'
        browser.evaluate("document.documentElement.dataset.theme='light';true")
        assert browser.evaluate("getComputedStyle(document.querySelector('#ab-space-hero')).color") == 'rgb(244, 241, 255)'
        browser.evaluate("document.documentElement.style.setProperty('--heo-white','white');document.body.insertAdjacentHTML('beforeend','<aside id=\"aside-content\"><div class=\"card-info\"><span class=\"author-info__name\" style=\"color:var(--heo-white)\">个人卡片</span></div></aside>');true")
        assert browser.evaluate("getComputedStyle(document.querySelector('.author-info__name')).color") == 'rgb(47, 41, 64)'
        browser.evaluate("document.querySelector('#home_top').remove();document.dispatchEvent(new Event('pjax:complete'));true")
        assert browser.evaluate("document.querySelectorAll('#ab-space-hero').length") == 0


def run_pointer_checks(port):
    with Browser(1366, 900) as browser:
        browser.navigate(f'http://127.0.0.1:{port}/fixture.html')
        browser.evaluate("document.body.insertAdjacentHTML('beforeend','<button id=\"pointer-target\" onclick=\"document.body.dataset.pointerClicked=1\" style=\"position:fixed;left:60px;top:60px;width:120px;height:50px;z-index:5\">点击目标</button>');true")
        for i in range(20):
            browser.command('Input.dispatchMouseEvent', {'type': 'mouseMoved', 'x': 30 + i * 5, 'y': 80})
            time.sleep(.04)
        browser.evaluate('new Promise(r=>requestAnimationFrame(r))', promise=True)
        assert browser.evaluate("document.querySelector('#ab-pointer-light').classList.contains('ab-pointer-visible')")
        assert browser.evaluate("getComputedStyle(document.querySelector('.ab-pointer-halo')).transform") != 'none'
        assert browser.evaluate("document.querySelector('#ab-pointer-light').getAnimations({subtree:true}).length") > 0
        assert browser.evaluate("document.elementFromPoint(125,80).id") == 'pointer-target'
        browser.command('Input.dispatchMouseEvent', {'type': 'mousePressed', 'x': 125, 'y': 80, 'button': 'left', 'clickCount': 1})
        browser.command('Input.dispatchMouseEvent', {'type': 'mouseReleased', 'x': 125, 'y': 80, 'button': 'left', 'clickCount': 1})
        assert browser.evaluate("document.body.dataset.pointerClicked") == '1'
        browser.evaluate("for(let i=0;i<5;i++)document.dispatchEvent(new Event('pjax:complete'));true")
        assert browser.evaluate("document.querySelectorAll('#ab-pointer-light').length") == 1
        assert browser.evaluate("document.querySelectorAll('.ab-pointer-spark').length") == 12
        browser.command('Emulation.setEmulatedMedia', {'features': [{'name': 'prefers-reduced-motion', 'value': 'reduce'}]})
        browser.evaluate('new Promise(r=>requestAnimationFrame(()=>requestAnimationFrame(r)))', promise=True)
        assert browser.evaluate("document.querySelectorAll('#ab-pointer-light').length") == 0

if __name__ == "__main__":
    main()
