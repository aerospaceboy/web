/* In-article navigation and public links; no storage, analytics or network requests. */
(() => {
    const fragment = id => '#' + encodeURIComponent(id);
    const claimId = (existing, label, occupied) => {
        if (existing && !occupied.has(existing)) { occupied.add(existing);return existing; }
        const slug = Array.from(label.normalize('NFKC').toLowerCase().replace(/[^\p{L}\p{N}]+/gu, '-').replace(/^-|-$/g, '')).slice(0, 60).join('') || 'section';
        const base = 'ab-section-' + slug;
        let id = base, suffix = 2;
        while (occupied.has(id)) id = base + '-' + suffix++;
        occupied.add(id);return id;
    };
    const publicUrl = (canonical, current, id = '') => {
        let url = new URL(current);
        try {
            const candidate = new URL(canonical);
            if (candidate.origin === url.origin && candidate.pathname === url.pathname) url = candidate;
        } catch { /* Use the current article when no valid canonical is available. */ }
        url.search = '';url.hash = id ? fragment(id) : '';
        return url.href;
    };
    if (typeof module !== 'undefined' && module.exports) { module.exports = {fragment, claimId, publicUrl};return; }
    if (window.__abInstallArticleTools) { window.__abInstallArticleTools();return; }
    const headingText = heading => {
        const copy = heading.cloneNode(true);
        for (const element of copy.querySelectorAll('button,.anchorjs-link,.headerlink')) element.remove();
        return copy.textContent.replace(/\s+/g, ' ').trim();
    };
    const articleUrl = id => publicUrl(document.querySelector('#ab-page-canonical')?.href, location.href, id);
    const moveTo = heading => {
        if (!heading) return;
        heading.focus({preventScroll:true});
        heading.scrollIntoView({block:'start', behavior:'instant'});
    };
    const followHash = () => {
        if (!location.hash) return;
        const raw = location.hash.slice(1);
        let decoded = raw;
        try { decoded = decodeURIComponent(raw); } catch { /* Literal malformed fragment. */ }
        const heading = document.getElementById(decoded) || document.getElementById(raw);
        if (heading?.matches('#post #article-container [data-ab-section]')) moveTo(heading);
    };
    const feedbackTimers = new WeakMap();
    const copyLink = async (url, section, trigger) => {
        const tools = document.querySelector('#ab-article-tools');
        const status = tools?.querySelector('[role="status"]');
        const manual = tools?.querySelector('.ab-link-fallback');
        try {
            if (!navigator.clipboard?.writeText) throw new Error('Clipboard unavailable');
            await navigator.clipboard.writeText(url);
            if (status) status.textContent = section ? '本节链接已复制' : '文章链接已复制';
            if (manual) manual.hidden = true;
            if (trigger) {
                const title = trigger.dataset.abOriginalTitle ?? trigger.title;
                trigger.dataset.abOriginalTitle = title;
                trigger.classList.add('ab-link-copied');trigger.title = section ? '本节链接已复制' : '文章链接已复制';
                clearTimeout(feedbackTimers.get(trigger));
                feedbackTimers.set(trigger, setTimeout(() => {
                    trigger.classList.remove('ab-link-copied');trigger.title = title;feedbackTimers.delete(trigger);
                }, 2200));
            }
        } catch {
            if (status) status.textContent = '请在下面手动复制链接';
            if (manual) { manual.value = url;manual.hidden = false;manual.focus();manual.select(); }
        }
    };
    const install = () => {
        const article = document.querySelector('#post #article-container');
        if (!article) { document.querySelector('#ab-article-tools')?.remove();return; }
        const headings = [...article.querySelectorAll('h2,h3')].filter(heading =>
            !heading.closest('[data-ab-no-count],.ab-project-brief') && headingText(heading));
        const occupied = new Set([...document.querySelectorAll('[id]')].filter(element => !headings.includes(element)).map(element => element.id));
        for (const heading of headings) {
            const label = headingText(heading);
            heading.id = claimId(heading.id, label, occupied);
            heading.dataset.abSection = '';
            if (!heading.hasAttribute('tabindex')) heading.tabIndex = -1;
            if (!heading.querySelector('.ab-section-link')) {
                const button = document.createElement('button');button.type = 'button';button.className = 'ab-section-link';
                button.setAttribute('aria-label', '复制本节链接：' + label);
                button.title = '复制本节链接';button.dataset.abNoCount = '';heading.append(button);
            }
        }
        let tools = document.querySelector('#ab-article-tools');
        if (!tools) {
            tools = document.createElement('section');tools.id = 'ab-article-tools';
            tools.setAttribute('aria-label', '文章导航与分享');tools.dataset.abNoCount = '';
            const bar = document.createElement('div');bar.className = 'ab-article-toolbar';
            const copy = document.createElement('button');copy.type = 'button';copy.className = 'ab-copy-article';copy.textContent = '复制文章链接';
            const status = document.createElement('span');status.className = 'ab-link-status';status.setAttribute('role', 'status');
            bar.append(copy, status);
            const manual = document.createElement('input');manual.type = 'text';manual.readOnly = true;manual.hidden = true;
            manual.className = 'ab-link-fallback';manual.setAttribute('aria-label', '手动复制链接');
            tools.append(bar, manual);article.before(tools);
        }
        let details = tools.querySelector('.ab-article-toc');
        if (location.hash) requestAnimationFrame(followHash);
        if (headings.length < 2) { details?.remove();return; }
        if (!details) {
            details = document.createElement('details');details.className = 'ab-article-toc';
            const summary = document.createElement('summary');
            const nav = document.createElement('nav');nav.setAttribute('aria-label', '文章章节');
            details.append(summary, nav);tools.append(details);
        }
        details.querySelector('summary').textContent = `文章目录 · ${headings.length} 个章节`;
        const list = document.createElement('ol');
        for (const heading of headings) {
            const item = document.createElement('li');
            if (heading.tagName === 'H3') item.className = 'ab-toc-subsection';
            const link = document.createElement('a');link.href = fragment(heading.id);link.textContent = headingText(heading);
            link.addEventListener('click', event => {
                if (event.button !== 0 || event.ctrlKey || event.metaKey || event.shiftKey || event.altKey) return;
                event.preventDefault();event.stopImmediatePropagation();
                const url = new URL(location.href);url.hash = fragment(heading.id);
                const state = history.state;
                const next = state && typeof state === 'object' && 'url' in state ? {...state, url:url.href} : state;
                history.replaceState(next, '', url.href);moveTo(heading);
            });
            item.append(link);list.append(item);
        }
        details.querySelector('nav').replaceChildren(list);
    };
    document.addEventListener('click', event => {
        const target = event.target instanceof Element ? event.target : null;
        const articleButton = target?.closest('#ab-article-tools .ab-copy-article');
        if (articleButton) copyLink(articleUrl(), false, articleButton);
        const sectionButton = target?.closest('.ab-section-link');
        const section = sectionButton?.closest('[data-ab-section]');
        if (section) copyLink(articleUrl(section.id), true, sectionButton);
    });
    window.addEventListener('hashchange', followHash);
    window.__abInstallArticleTools = install;
    document.addEventListener('pjax:complete', install);
    if (document.readyState === 'loading') document.addEventListener('DOMContentLoaded', install, {once:true});else install();
})();
