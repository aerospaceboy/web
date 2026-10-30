/* Resume layout enhancement; all resume text remains server-rendered by Halo. */
(() => {
    if (window.__abInstallResume) { window.__abInstallResume();return; }
    const install = () => {
        const path = window.__abPublicConfig?.resumePath;
        if (!path) return;
        const hero = document.querySelector('.ab-hero-copy');
        if (hero && !hero.querySelector('.ab-resume-link')) {
            const link = document.createElement('a');
            link.className = 'ab-resume-link';link.href = path;link.textContent = '个人简历 ↗';
            hero.append(link);
        }
        if (location.pathname.replace(/\/$/, '') !== path.replace(/\/$/, '')) return;
        const root = document.querySelector('#article-container');
        if (!root || root.dataset.abResume) return;
        root.dataset.abResume = 'true';root.classList.add('ab-resume');
        const nodes = [...root.children];
        let section;
        const sections = [];
        for (const node of nodes) {
            if (node.tagName === 'H2') {
                section = document.createElement(sections.length ? 'section' : 'header');
                section.className = sections.length ? 'ab-resume-section' : 'ab-resume-profile';
                section.id = 'ab-resume-section-' + sections.length;
                sections.push(section);root.insertBefore(section, node);
            }
            if (section) section.append(node);
        }
        const navigation = document.createElement('nav');
        navigation.className = 'ab-resume-toc';navigation.setAttribute('aria-label', '简历目录');
        for (const item of sections.slice(1)) {
            const title = item.querySelector('h2');
            const link = document.createElement('a');link.href = '#' + item.id;link.textContent = title.textContent;
            navigation.append(link);
        }
        if (sections[0]) sections[0].after(navigation);
        for (const item of sections.slice(1)) {
            let entry;
            for (const node of [...item.children]) {
                if (node.tagName === 'H3') {
                    entry = document.createElement('div');entry.className = 'ab-resume-entry';
                    item.insertBefore(entry, node);
                }
                if (entry && node.tagName !== 'H2') entry.append(node);
            }
        }
    };
    window.__abInstallResume = install;
    document.addEventListener('pjax:complete', install);
    if (document.readyState === 'loading') document.addEventListener('DOMContentLoaded', install, {once:true});
    else install();
})();
