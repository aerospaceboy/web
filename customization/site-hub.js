/* Social links and local reading preferences. No requests, tracking or remote fonts. */
(() => {
    if (window.__abInstallSiteHub) { window.__abInstallSiteHub();return; }
    const config = window.__abPublicConfig || {};
    const github = config.githubProfileUrl;
    const storageKey = 'ab:reader:v1';
    let preferences = {font: 'default', calm: false};
    let canSave = true;
    const parse = value => {
        const item = JSON.parse(value);
        return {font: ['default', 'large', 'larger'].includes(item?.font) ? item.font : 'default', calm: item?.calm === true};
    };
    try { preferences = parse(localStorage.getItem(storageKey)); } catch { canSave = false; }
    const apply = () => {
        const root = document.documentElement;
        root.dataset.abReadingSize = preferences.font;
        root.classList.toggle('ab-calm-mode', preferences.calm);
        for (const button of document.querySelectorAll('[data-ab-font]')) {
            button.setAttribute('aria-pressed', String(button.dataset.abFont === preferences.font));
        }
        for (const button of document.querySelectorAll('[data-ab-calm]')) {
            button.setAttribute('aria-checked', String(preferences.calm));
            button.querySelector('.ab-switch-state').textContent = preferences.calm ? '已开启' : '已关闭';
        }
        for (const note of document.querySelectorAll('.ab-preference-note')) {
            note.textContent = canSave ? '设置仅保存在此浏览器。' : '当前浏览器无法保存，设置在本次访问内生效。';
        }
        document.dispatchEvent(new Event('ab:preferences'));
    };
    apply();
    // Small inline vectors keep the feature independent of icon-font availability.
    const icons = {
        github: '<path d="M9 19c-4.3 1.3-4.3-2.2-6-2.7m12 5v-3.4a3 3 0 0 0-.8-2.3c2.7-.3 5.5-1.3 5.5-6A4.7 4.7 0 0 0 18.4 6a4.3 4.3 0 0 0-.1-3.5S17.2 2.2 14.8 4a12.1 12.1 0 0 0-6.4 0C6 2.2 4.9 2.5 4.9 2.5A4.3 4.3 0 0 0 4.8 6a4.7 4.7 0 0 0-1.3 3.6c0 4.7 2.8 5.7 5.5 6A3 3 0 0 0 8.2 18v3.3"/>',
        rss: '<path d="M4 4a16 16 0 0 1 16 16M4 11a9 9 0 0 1 9 9"/><circle cx="5" cy="19" r="1"/>',
        projects: '<rect x="3" y="6" width="18" height="15" rx="2"/><path d="M8 6V3h8v3M3 12h18M10 12v3h4v-3"/>',
        resume: '<path d="M14 3H5v18h14V8zM14 3v5h5M8 12h8M8 16h6"/>',
        archives: '<rect x="3" y="4" width="18" height="4" rx="1"/><path d="M5 8v13h14V8M9 12h6"/>',
        guestbook: '<path d="M21 15a3 3 0 0 1-3 3H8l-5 3V6a3 3 0 0 1 3-3h12a3 3 0 0 1 3 3zM7 8h10M7 12h7"/>'
    };
    const icon = name => `<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.7" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true" focusable="false">${icons[name]}</svg>`;
    const link = (url, label, glyph, external = false) => {
        const anchor = document.createElement('a');anchor.href = url;
        anchor.innerHTML = icon(glyph);
        const text = document.createElement('span');text.textContent = label;anchor.append(text);
        if (external) {
            anchor.target = '_blank';anchor.rel = 'noopener noreferrer';
            anchor.setAttribute('aria-label', `${label}（新标签页）`);
            anchor.title = `${label}（新标签页）`;
        }
        return anchor;
    };
    const socialLinks = className => {
        const group = document.createElement('div');group.className = className;
        group.setAttribute('aria-label', '社交与订阅');
        if (github) group.append(link(github, 'GitHub', 'github', true));
        group.append(link('/rss.xml', 'RSS 订阅', 'rss'));
        return group;
    };
    const settings = () => {
        const content = document.createElement('div');content.className = 'ab-preferences';
        content.innerHTML = `<div class="ab-font-label">文章字号</div>
            <div class="ab-font-options" role="group" aria-label="文章字号">
                <button type="button" data-ab-font="default" aria-pressed="false">标准</button>
                <button type="button" data-ab-font="large" aria-pressed="false">大</button>
                <button type="button" data-ab-font="larger" aria-pressed="false">特大</button>
            </div>
            <button class="ab-calm-switch" type="button" role="switch" aria-checked="false" data-ab-calm>
                <span>减少装饰动效</span><span class="ab-switch-state"></span>
            </button><p class="ab-preference-note"></p>`;
        return content;
    };
    const install = () => {
        const tools = document.querySelector('#nav-right');
        if (tools && github && !tools.querySelector('#ab-github-button')) {
            const wrapper = document.createElement('div');wrapper.id = 'ab-github-button';wrapper.className = 'nav-button';
            const anchor = link(github, 'GitHub', 'github', true);anchor.className = 'ab-github-nav';
            wrapper.append(anchor);tools.prepend(wrapper);
        }
        const hero = document.querySelector('.ab-hero-copy');
        if (hero && !hero.querySelector('.ab-hero-socials')) {
            const socials = socialLinks('ab-hero-socials');
            const resume = hero.querySelector('.ab-resume-link');
            if (resume) socials.append(resume);
            hero.append(socials);
        }
        const profile = document.querySelector('#aside-content .card-info');
        if (profile && !profile.querySelector('.ab-profile-links')) {
            profile.classList.add('ab-profile-card');
            const description = profile.querySelector('.author-info__description');
            if (description && !description.textContent.trim()) description.textContent = '记录代码、硬件与星空之间的探索。';
            const content = profile.querySelector('.card-content');
            if (content) content.append(socialLinks('ab-profile-links'));
        }
        const aside = document.querySelector('#aside-content');
        const isHome = !!document.querySelector('#home_top');
        if (!isHome) {
            aside?.querySelector('#ab-explore-card')?.remove();
            aside?.querySelector('#ab-preferences-card')?.remove();
        }
        if (aside && isHome && !aside.querySelector('#ab-explore-card')) {
            const card = document.createElement('section');card.id = 'ab-explore-card';card.className = 'card-widget ab-hub-card';
            card.innerHTML = '<h2 class="ab-widget-title"><span aria-hidden="true">✦</span> 探索站点</h2><nav class="ab-shortcuts" aria-label="探索站点"></nav>';
            const navigation = card.querySelector('nav');
            const shortcuts = [
                ['/projects', '项目记录', 'projects'], [config.resumePath, '个人简历', 'resume'],
                ['/archives', '文章归档', 'archives'], ['/guestbook', '留言交流', 'guestbook']
            ];
            for (const [url, label, glyph] of shortcuts) {
                if (url) navigation.append(link(url, label, glyph));
            }
            const preferences = document.createElement('section');preferences.id = 'ab-preferences-card';preferences.className = 'card-widget ab-hub-card';
            preferences.innerHTML = '<h2 class="ab-widget-title"><span aria-hidden="true">Aa</span> 阅读偏好</h2>';
            preferences.append(settings());
            if (profile) profile.after(card, preferences);else aside.prepend(card, preferences);
        }
        const sidebar = document.querySelector('#sidebar-menus');
        if (sidebar && !sidebar.querySelector('#ab-sidebar-hub')) {
            const hub = document.createElement('section');hub.id = 'ab-sidebar-hub';
            hub.append(socialLinks('ab-sidebar-socials'));
            const details = document.createElement('details');details.className = 'ab-reading-details';
            const summary = document.createElement('summary');summary.textContent = '阅读与动效设置';
            details.append(summary, settings());hub.append(details);
            const navigation = sidebar.querySelector('#ab-mobile-navigation');
            if (navigation) navigation.after(hub);else sidebar.prepend(hub);
        }
        const article = document.querySelector('#article-container');
        const isPost = location.pathname.startsWith('/archives/') && !!article?.closest('#post');
        if (article) article.classList.toggle('ab-readable-post', isPost);
        if (isPost && !document.querySelector('#ab-article-settings')) {
            const details = document.createElement('details');details.id = 'ab-article-settings';details.className = 'ab-reading-details';
            const summary = document.createElement('summary');summary.textContent = '阅读设置';
            details.append(summary, settings());article.before(details);
        }
        apply();
    };
    document.addEventListener('click', event => {
        const target = event.target instanceof Element ? event.target.closest('[data-ab-font], [data-ab-calm]') : null;
        if (!target) return;
        if (target.hasAttribute('data-ab-font')) preferences.font = target.dataset.abFont;
        else preferences.calm = !preferences.calm;
        try { localStorage.setItem(storageKey, JSON.stringify(preferences));canSave = true; } catch { canSave = false; }
        apply();
    });
    window.addEventListener('storage', event => {
        if (event.key !== storageKey) return;
        try { preferences = parse(event.newValue); } catch { return; }
        apply();
    });
    window.__abInstallSiteHub = install;
    document.addEventListener('pjax:complete', install);
    if (document.readyState === 'loading') document.addEventListener('DOMContentLoaded', install, {once:true});else install();
})();
