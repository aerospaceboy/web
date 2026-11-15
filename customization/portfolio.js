/* Shared project catalogue and readable article metadata; safe to rerun after Pjax. */
(() => {
    if (window.__abInstallPortfolio) { window.__abInstallPortfolio();return; }
    const projects = window.__abPublicConfig?.featuredProjects || [];
    const node = (tag, className, text) => {
        const element = document.createElement(tag);
        if (className) element.className = className;
        if (text) element.textContent = text;
        return element;
    };
    const card = item => {
        const article = node('article', 'ab-project-card ab-project-compact');
        const cover = node('a', 'ab-project-cover');cover.href = item.path;
        cover.setAttribute('aria-label', `查看${item.title}`);
        const image = node('img');image.src = item.image;image.alt = '';image.loading = 'lazy';
        image.width = 640;image.height = 360;cover.append(image);
        const body = node('div', 'ab-project-body');
        body.append(node('p', 'ab-project-kicker', item.label));
        const heading = node('h3');const title = node('a', '', item.title);title.href = item.path;heading.append(title);
        body.append(heading, node('p', 'ab-project-summary', item.summary));
        const tags = node('div', 'ab-project-tags');
        for (const tag of item.tags) tags.append(node('span', '', tag));
        const actions = node('div', 'ab-project-actions');
        const detail = node('a', '', '查看项目 →');detail.href = item.path;actions.append(detail);
        if (item.github) {
            const github = node('a', '', 'GitHub ↗');github.href = item.github;
            github.target = '_blank';github.rel = 'noopener noreferrer';actions.append(github);
        }
        body.append(tags, actions);article.append(cover, body);return article;
    };
    const countText = article => {
        const copy = article.cloneNode(true);
        for (const element of copy.querySelectorAll('script,style,button,[data-ab-no-count]')) element.remove();
        const walker = document.createTreeWalker(copy, NodeFilter.SHOW_TEXT);
        const parts = [];
        while (walker.nextNode()) parts.push(walker.currentNode.textContent);
        const text = parts.join(' ');
        const han = (text.match(/\p{Script=Han}/gu) || []).length;
        const words = (text.match(/[A-Za-z0-9]+(?:[._'’\/-][A-Za-z0-9]+)*/g) || []).length;
        return {units: han + words, minutes: Math.max(1, Math.ceil(han / 350 + words / 200))};
    };
    const install = () => {
        const hero = document.querySelector('#ab-space-hero');
        if (hero && projects.length && !document.querySelector('#ab-featured-projects')) {
            const section = node('section', 'ab-featured-projects');section.id = 'ab-featured-projects';
            section.setAttribute('aria-labelledby', 'ab-featured-title');
            const top = node('div', 'ab-section-heading');const heading = node('h2', '', '精选项目');heading.id = 'ab-featured-title';
            const all = node('a', '', '全部项目 →');all.href = '/projects';top.append(heading, all);
            const grid = node('div', 'ab-project-grid');
            for (const item of projects) grid.append(card(item));
            section.append(top, grid);hero.after(section);
        }
        const article = document.querySelector('#post #article-container');
        const header = document.querySelector('#page-header');
        header?.classList.toggle('ab-post-header', !!article);
        if (!article) return;
        const stats = countText(article);
        const meta = document.querySelector('.post-meta-wordcount');
        if (meta) {
            const count = meta.querySelector('.word-count');
            if (count) { count.textContent = `${stats.units.toLocaleString('zh-CN')} 字/词`;count.title = '按正文统计：汉字逐字、英文和数字按词；不计 HTML 标记。'; }
            const time = meta.querySelector(':scope > span:last-child');
            if (time && time !== count) { time.textContent = `约 ${stats.minutes} 分钟`;time.title = '按汉字每分钟 350 字、英文每分钟 200 词估算。'; }
            meta.dataset.abCount = String(stats.units);meta.dataset.abMinutes = String(stats.minutes);
        }
        const item = projects.find(item => item.path === location.pathname.replace(/\/$/, ''));
        if (item && !article.querySelector('.ab-project-brief')) {
            const brief = node('aside', 'ab-project-brief');brief.setAttribute('aria-label', '项目速览');brief.dataset.abNoCount = '';
            brief.append(node('p', 'ab-project-kicker', '项目速览'), node('p', 'ab-brief-summary', item.summary));
            const list = node('dl');
            for (const [label, value] of [ ['实现重点', item.focus], ['验证范围', item.scope], ['资料版本', item.version] ]) {
                const row = node('div');row.append(node('dt', '', label), node('dd', '', value));list.append(row);
            }
            brief.append(list);article.prepend(brief);
        }
    };
    window.__abInstallPortfolio = install;
    document.addEventListener('pjax:complete', install);
    if (document.readyState === 'loading') document.addEventListener('DOMContentLoaded', install, {once: true});else install();
})();
