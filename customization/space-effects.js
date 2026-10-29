/* Progressive homepage enhancement: native Halo content remains the fallback. */
(() => {
    if (window.__abInstallSpaceHero) {
        window.__abInstallSpaceHero();
        return;
    }

    let observer;
    let activeHero;
    let frame = 0;
    const reduced = matchMedia('(prefers-reduced-motion: reduce)');
    const finePointer = matchMedia('(hover: hover) and (pointer: fine)');

    const install = () => {
        const home = document.querySelector('#home_top');
        if (observer) observer.disconnect();
        if (frame) cancelAnimationFrame(frame);
        frame = 0;
        activeHero = null;
        if (!home) return;
        let hero = home.querySelector('#ab-space-hero');
        if (!hero) {
            hero = document.createElement('section');
            hero.id = 'ab-space-hero';
            hero.setAttribute('aria-labelledby', 'ab-space-title');
            // Static, repository-owned markup; page text is assigned separately.
            hero.innerHTML = `
                <div class="ab-nebula-scene" aria-hidden="true">
                    <img class="ab-nebula-image" alt="" decoding="async" fetchpriority="high">
                    <svg class="ab-starfield" viewBox="0 0 1200 500" preserveAspectRatio="xMidYMid slice" focusable="false"></svg>
                    <span class="ab-shooting-star"></span>
                </div>
                <div class="ab-hero-copy">
                    <p class="ab-hero-eyebrow"><span></span> AEROSPACEBOY · UNDER THE STARS</p>
                    <h1 id="ab-space-title"></h1>
                    <p class="ab-hero-english">写代码，<span>也仰望星空。</span></p>
                    <p class="ab-hero-description"></p>
                    <div class="ab-hero-actions">
                        <a class="ab-hero-primary" href="/projects">探索项目 <span aria-hidden="true">↗</span></a>
                        <a class="ab-hero-secondary" href="/archives">阅读文章 <span aria-hidden="true">→</span></a>
                    </div>
                    <div class="ab-hero-topics" aria-label="技术方向">
                        <a href="/categories/embedded">Embedded</a><a href="/categories/ai">AI</a>
                        <a href="/categories/robotics">Robotics</a><a href="/tags/fpga">FPGA</a>
                    </div>
                </div>
                <div class="ab-hero-footer"><span>CODE · HARDWARE · STARRY NIGHTS</span><span>持续探索，持续构建 <i aria-hidden="true">↗</i></span></div>`;
            hero.querySelector('h1').textContent = home.querySelector('.banners-title-big')?.textContent.trim() || '半截的诗';
            const source = home.querySelector('.banners-title-small');
            hero.querySelector('.ab-hero-description').textContent = source?.firstChild?.textContent.trim() || '在代码、硬件与星空之间，记录每一次探索。';
            const background = window.__abPublicConfig?.nebulaBackgroundPath;
            const image = hero.querySelector('.ab-nebula-image');
            image.addEventListener('error', () => image.remove(), {once: true});
            if (background) image.src = background;
            else image.remove();
            // A small, deterministic decorative field; these are not sky coordinates.
            let seed = 72931;
            const random = () => ((seed = (seed * 1664525 + 1013904223) >>> 0) / 4294967296);
            const svg = hero.querySelector('.ab-starfield');
            for (let layer = 0; layer < 2; layer++) {
                const group = document.createElementNS('http://www.w3.org/2000/svg', 'g');
                group.setAttribute('class', 'ab-stars-depth-' + layer);
                for (let i = 0; i < 75; i++) {
                    const star = document.createElementNS('http://www.w3.org/2000/svg', 'circle');
                    star.setAttribute('cx', (random() * 1200).toFixed(1));
                    star.setAttribute('cy', (random() * 500).toFixed(1));
                    star.setAttribute('r', (.25 + Math.pow(random(), 4) * 1.1).toFixed(2));
                    star.setAttribute('opacity', (.15 + random() * .55).toFixed(2));
                    group.append(star);
                }
                svg.append(group);
            }
            home.prepend(hero);
            hero.addEventListener('pointermove', event => {
                if (reduced.matches || !finePointer.matches || navigator.connection?.saveData || frame) return;
                const x = event.clientX;
                const y = event.clientY;
                frame = requestAnimationFrame(() => {
                    frame = 0;
                    if (!hero.isConnected) return;
                    const rect = hero.getBoundingClientRect();
                    hero.style.setProperty('--ab-pointer-x', `${x - rect.left}px`);
                    hero.style.setProperty('--ab-pointer-y', `${y - rect.top}px`);
                });
            });
            hero.addEventListener('pointerleave', () => {
                if (frame) cancelAnimationFrame(frame);
                frame = 0;
                hero.style.removeProperty('--ab-pointer-x');
                hero.style.removeProperty('--ab-pointer-y');
            });
        }
        activeHero = hero;
        if ('IntersectionObserver' in window) {
            observer = new IntersectionObserver(entries => {
                for (const entry of entries) entry.target.classList.toggle('ab-sky-paused', document.hidden || !entry.isIntersecting);
            });
            observer.observe(hero);
        }
        hero.classList.toggle('ab-sky-paused', document.hidden);
    };
    document.addEventListener('visibilitychange', () => {
        if (activeHero) {
            const rect = activeHero.getBoundingClientRect();
            activeHero.classList.toggle('ab-sky-paused', document.hidden || rect.bottom <= 0 || rect.top >= innerHeight);
        }
    });
    window.__abInstallSpaceHero = install;
    document.addEventListener('pjax:complete', install);
    if (document.readyState === 'loading') document.addEventListener('DOMContentLoaded', install, {once: true});
    else install();
})();
