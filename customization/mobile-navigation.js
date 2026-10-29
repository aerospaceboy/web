/* Hao 1.7.3 omits flat primary-menu entries from its mobile sidebar. */
(() => {
    const guardDisabledWidgets = () => {
        // Sidebar mode buttons and Escape still call rm when the optional right
        // menu module is disabled. Delegate to Hao's normal theme controller.
        if (typeof rm === 'undefined') {
            window.rm = {
                hideRightMenu() {},
                switchDarkMode() {
                    if (typeof navFn !== 'undefined') navFn.switchDarkMode();
                }
            };
        }
        if (typeof rm !== 'undefined' && typeof rm.copyPageUrl !== 'function') {
            rm.copyPageUrl = async function () {
                const button = document.querySelector('.post-copyright-copybtn');
                try {
                    if (!navigator.clipboard?.writeText) throw new Error('Clipboard unavailable');
                    await navigator.clipboard.writeText(location.href);
                    if (button) button.setAttribute('aria-label', '文章链接已复制');
                    if (typeof btf !== 'undefined' && typeof btf.snackbarShow === 'function') {
                        btf.snackbarShow('文章链接已复制', false, 2000);
                    }
                    return true;
                } catch {
                    if (button) {
                        button.setAttribute('aria-label', '复制失败，请手动复制地址栏');
                        button.title = '复制失败，请手动复制地址栏';
                    }
                    return false;
                }
            };
        }
        // Escape calls this even when the loading-box setting is disabled.
        if (typeof heo !== 'undefined' && typeof heo.hideLoading === 'function' &&
            !heo.__abLoadingGuard) {
            const original = heo.hideLoading;
            heo.hideLoading = function (...args) {
                if (document.querySelector('#loading-box')) return original.apply(this, args);
            };
            heo.__abLoadingGuard = true;
        }
    };

    const repairPageControls = () => {
        const config = window.__abPublicConfig || {};
        const privacy = config.privacyPolicyPath;
        if (privacy) {
            for (const link of document.querySelectorAll('.comment-randomInfo a[href]')) {
                const url = new URL(link.href, document.baseURI);
                if (url.origin === location.origin && url.pathname === '/privacy') {
                    link.setAttribute('href', privacy);
                }
            }
        }
        for (const button of document.querySelectorAll('.post-copyright-copybtn')) {
            button.setAttribute('aria-label', '复制文章链接');
            button.title = '复制文章链接';
        }
        for (const image of document.querySelectorAll('img.post_bg')) {
            image.decoding = 'async';
            if (image.dataset.abCoverGuard) continue;
            image.dataset.abCoverGuard = 'true';
            image.addEventListener('error', () => {
                if (!config.defaultCoverPath) return;
                const fallback = new URL(config.defaultCoverPath, document.baseURI);
                if (image.src === fallback.href) return;
                image.removeAttribute('data-lazy-src');
                image.src = fallback.href;
            }, {once: true});
        }
        const first = document.querySelector('#recent-posts img.post_bg');
        if (first) {
            const rect = first.getBoundingClientRect();
            if (rect.top < innerHeight && rect.bottom > 0) {
                first.loading = 'eager';
                first.fetchPriority = 'high';
                if (!first.getAttribute('src') && first.dataset.lazySrc) first.src = first.dataset.lazySrc;
            }
        }
    };

    const install = () => {
        guardDisabledWidgets();
        repairPageControls();
        const sidebar = document.querySelector('#sidebar-menus');
        const primary = document.querySelector('#menus');
        if (!sidebar || !primary) return;

        const existing = new Set([...sidebar.querySelectorAll('a[href]')]
            .filter(link => !link.closest('#ab-mobile-navigation'))
            .map(link => link.href));
        const seen = new Set();
        const links = [...primary.querySelectorAll('a.site-page[href]')].filter(link => {
            const url = new URL(link.href, document.baseURI);
            const label = link.textContent.trim();
            if (!['http:', 'https:'].includes(url.protocol) || !label ||
                existing.has(url.href) || seen.has(url.href)) return false;
            seen.add(url.href);
            return true;
        });

        let nav = sidebar.querySelector('#ab-mobile-navigation');
        if (!links.length) {
            if (nav) nav.remove();
            return;
        }
        if (!nav) {
            nav = document.createElement('nav');
            nav.id = 'ab-mobile-navigation';
            nav.setAttribute('aria-label', '主导航');
            sidebar.prepend(nav);
        }
        const heading = document.createElement('span');
        heading.className = 'sidebar-menu-item-title';
        heading.textContent = '主导航';
        const list = document.createElement('div');
        list.className = 'ab-mobile-nav-links';
        for (const source of links) {
            const link = document.createElement('a');
            link.href = source.href;
            link.textContent = source.textContent.trim();
            if (source.target === '_blank') {
                link.target = '_blank';
                link.rel = 'noopener noreferrer';
            }
            list.append(link);
        }
        nav.replaceChildren(heading, list);
    };

    // Pjax can execute injected scripts again; keep a single listener pair.
    if (window.__abInstallMobileNavigation) {
        window.__abInstallMobileNavigation();
        return;
    }
    window.__abInstallMobileNavigation = install;
    document.addEventListener('pjax:complete', install);
    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', install, {once: true});
    } else {
        install();
    }
})();
