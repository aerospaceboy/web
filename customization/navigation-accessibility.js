/* Progressive navigation: keep the CMS links, improve grouping and keyboard access. */
(() => {
    if (window.__abInstallAccessibleNavigation) { window.__abInstallAccessibleNavigation();return; }
    const mainPaths = ['/', '/projects', '/archives', '/about', '/resume'];
    const pathOf = link => new URL(link.href, document.baseURI).pathname.replace(/\/$/, '') || '/';
    let panel, observer, wasOpen = false, returnFocus, background, previousInert = false;
    const focusables = () => [...(panel?.querySelectorAll('a[href],button,summary,select,[tabindex="0"]') || [])]
        .filter(element => !element.disabled && element.getClientRects().length &&
            !element.closest('[inert]') && !element.closest('details:not([open]) > :not(summary)'));
    const closePanel = () => document.querySelector('#menu-mask')?.click();
    const syncPanel = () => {
        if (!panel) return;
        const open = panel.classList.contains('open');
        const toggle = document.querySelector('#toggle-menu a');
        toggle?.setAttribute('aria-expanded', String(open));
        panel.inert = !open;
        panel.setAttribute('aria-hidden', String(!open));
        if (open === wasOpen) return;
        wasOpen = open;
        if (open) {
            returnFocus = document.activeElement;
            background = document.querySelector('#body-wrap, .body-wrap');
            if (background) { previousInert = background.inert;background.inert = true; }
            panel.setAttribute('aria-modal', 'true');
            focusables()[0]?.focus({preventScroll:true});
        } else {
            if (background) background.inert = previousInert;
            panel.removeAttribute('aria-modal');
            if (returnFocus?.isConnected && !returnFocus.closest('[inert]')) returnFocus.focus({preventScroll:true});
            returnFocus = null;
        }
    };
    const install = () => {
        const row = document.querySelector('#menus > .menus_items');
        if (row && !row.querySelector('#ab-nav-more')) {
            const items = [...row.children].filter(item => item.matches('.menus_item'));
            const primary = mainPaths.map(path => items.find(item => {
                const link = item.querySelector('a.site-page[href]');return link && pathOf(link) === path;
            })).filter(Boolean);
            const extra = items.filter(item => !primary.includes(item));
            if (primary.length && extra.length) {
                const details = document.createElement('details');details.id = 'ab-nav-more';
                const summary = document.createElement('summary');summary.textContent = '更多';
                const list = document.createElement('div');list.className = 'ab-more-links';
                list.setAttribute('aria-label', '更多页面');
                details.append(summary, list);
                for (const item of extra) list.append(item);
                row.append(...primary, details);
            }
        }
        const mobile = document.querySelector('#ab-mobile-navigation .ab-mobile-nav-links');
        if (mobile && !mobile.querySelector('.ab-mobile-secondary')) {
            const links = [...mobile.children].filter(item => item.matches('a[href]'));
            const primary = mainPaths.map(path => links.find(link => pathOf(link) === path)).filter(Boolean);
            const extra = links.filter(link => !primary.includes(link));
            mobile.append(...primary);
            if (extra.length) {
                const label = document.createElement('span');label.className = 'ab-mobile-secondary';label.textContent = '发现与交流';
                mobile.append(label, ...extra);
            }
        }
        for (const link of document.querySelectorAll('#menus a.site-page[href],#ab-mobile-navigation a[href]')) {
            link.removeAttribute('aria-current');
            const path = pathOf(link);
            const here = location.pathname.replace(/\/$/, '') || '/';
            if (path === here) link.setAttribute('aria-current', 'page');
            else if (path !== '/' && here.startsWith(path + '/')) link.setAttribute('aria-current', 'location');
        }
        const target = document.querySelector('#post, #page, #recent-posts');
        if (target) {
            let skip = document.querySelector('#ab-skip-link');
            if (!skip) {
                skip = document.createElement('a');skip.id = 'ab-skip-link';skip.className = 'ab-skip-link';
                skip.textContent = '跳到主要内容';document.body.prepend(skip);
            }
            skip.href = '#' + target.id;
            if (!target.hasAttribute('tabindex')) target.tabIndex = -1;
        }
        const toggle = document.querySelector('#toggle-menu a');
        if (toggle) {
            toggle.setAttribute('role', 'button');toggle.tabIndex = 0;
            toggle.setAttribute('aria-controls', 'sidebar-menus');
        }
        const next = document.querySelector('#sidebar-menus');
        if (next !== panel) {
            observer?.disconnect();
            if (wasOpen && background) background.inert = previousInert;
            panel = next;wasOpen = false;returnFocus = null;
            if (panel) {
                panel.setAttribute('role', 'dialog');panel.setAttribute('aria-label', '站点导航');
                const close = document.createElement('button');close.type = 'button';close.id = 'ab-close-navigation';
                close.textContent = '关闭导航 ×';panel.prepend(close);
                observer = new MutationObserver(syncPanel);observer.observe(panel, {attributes:true, attributeFilter:['class']});
            }
        }
        syncPanel();
        window.__abInstallHeaderLayout?.();
    };
    document.addEventListener('click', event => {
        const element = event.target instanceof Element ? event.target : null;
        const more = document.querySelector('#ab-nav-more');
        if (more?.open && (!element?.closest('#ab-nav-more') || element.closest('a[href]'))) more.open = false;
        if (element?.closest('#ab-close-navigation')) closePanel();
        if (element?.closest('#ab-skip-link')) {
            const target = document.querySelector('#post, #page, #recent-posts');
            if (target) { event.preventDefault();target.focus();target.scrollIntoView({block:'start',behavior:'instant'}); }
        }
    });
    document.addEventListener('keydown', event => {
        if (event.target instanceof Element && event.target.closest('#toggle-menu a') && ['Enter', ' '].includes(event.key)) {
            event.preventDefault();event.target.closest('#toggle-menu a').click();return;
        }
        if (panel?.classList.contains('open')) {
            if (event.key === 'Escape') { event.preventDefault();closePanel(); }
            if (event.key === 'Tab') {
                const items = focusables();const first = items[0];const last = items.at(-1);
                if (!first) { event.preventDefault();return; }
                if (event.shiftKey && (document.activeElement === first || !panel.contains(document.activeElement))) {
                    event.preventDefault();last.focus();
                } else if (!event.shiftKey && (document.activeElement === last || !panel.contains(document.activeElement))) {
                    event.preventDefault();first.focus();
                }
            }
        }
        const more = document.querySelector('#ab-nav-more');
        if (event.key === 'Escape' && more?.open) { more.open = false;more.querySelector('summary')?.focus(); }
    });
    document.addEventListener('focusin', event => {
        const more = document.querySelector('#ab-nav-more');
        if (more?.open && !more.contains(event.target)) more.open = false;
    });
    window.__abInstallAccessibleNavigation = install;
    document.addEventListener('pjax:complete', install);
    if (document.readyState === 'loading') document.addEventListener('DOMContentLoaded', install, {once:true});else install();
})();
