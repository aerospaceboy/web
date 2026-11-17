/* Server HTML already contains metadata. Keep that metadata in sync on Pjax navigation. */
(() => {
    if (window.__abSyncPageMetadata) return;
    const absolute = value => {
        if (!value) return '';
        try {
            const url = new URL(value);
            return url.protocol === 'https:' && !url.username && !url.password ? url.href : '';
        } catch { return ''; }
    };
    const sync = () => {
        const marker = document.querySelector('#ab-page-metadata');
        if (!marker) return;
        const data = marker.dataset;
        const canonical = absolute(data.canonical);
        let link = document.querySelector('#ab-page-canonical');
        if (canonical) {
            if (!link) { link = document.createElement('link');link.id = 'ab-page-canonical';link.rel = 'canonical';document.head.append(link); }
            link.href = canonical;
        } else link?.remove();
        let script = document.querySelector('#ab-page-schema');
        if (data.kind !== 'post' || !canonical || !data.headline) { script?.remove();return; }
        const schema = {'@context': 'https://schema.org', '@type': 'BlogPosting', url: canonical,
            mainEntityOfPage: canonical, headline: data.headline,
            datePublished: data.published || null, dateModified: data.modified || null,
            author: {'@type': 'Person', name: data.authorName || '', url: absolute(data.authorUrl)},
            image: absolute(data.image) ? [absolute(data.image)] : []};
        if (!script) {
            script = document.createElement('script');script.id = 'ab-page-schema';
            script.type = 'application/ld+json';document.head.append(script);
        }
        script.textContent = JSON.stringify(schema);
    };
    window.__abSyncPageMetadata = sync;
    document.addEventListener('pjax:complete', sync);
})();
