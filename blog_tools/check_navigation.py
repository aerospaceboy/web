"""Run the actual navigation bundle in Edge against flat and mixed-menu fixtures."""

import json
from pathlib import Path
import tempfile

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
            '<base href="https://aerospaceboy.site/">'
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
            '</body></html>', encoding="utf-8")
        with Browser(390, 844) as browser:
            browser.navigate(fixture.as_uri())
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
    print(json.dumps({"ok": True, "scenarios": ["flat_and_mixed_menu", "repeat_pjax", "menu_update", "native_menu_recovery", "theme_toggle", "disabled_widgets", "native_loading_preserved"]}))


if __name__ == "__main__":
    main()
