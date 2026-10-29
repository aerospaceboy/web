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
                <div class="ab-hero-grid" aria-hidden="true"></div>
                <div class="ab-hero-copy">
                    <p class="ab-hero-eyebrow"><span></span> AEROSPACEBOY / EXPLORATION LOG</p>
                    <h1 id="ab-space-title"></h1>
                    <p class="ab-hero-english">Build beyond <span>the ordinary.</span></p>
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
                <div class="ab-orbit-art" aria-hidden="true">
                    <svg viewBox="0 0 460 400" focusable="false">
                        <defs>
                            <radialGradient id="ab-planet-fill"><stop stop-color="#224e6e"/><stop offset=".7" stop-color="#0c253c"/><stop offset="1" stop-color="#071322"/></radialGradient>
                            <linearGradient id="ab-orbit-line"><stop stop-color="#6de2db" stop-opacity=".1"/><stop offset=".5" stop-color="#6de2db"/><stop offset="1" stop-color="#879bff" stop-opacity=".25"/></linearGradient>
                        </defs>
                        <g class="ab-orbit-guide" fill="none" stroke="currentColor">
                            <circle cx="230" cy="200" r="174" stroke-dasharray="2 10"/>
                            <path d="M230 10v24m0 332v24M36 200h24m340 0h24"/>
                            <circle cx="230" cy="200" r="148" opacity=".25"/>
                        </g>
                        <g class="ab-planet">
                            <circle cx="230" cy="200" r="102" fill="url(#ab-planet-fill)" stroke="#6de2db" stroke-opacity=".5"/>
                            <g fill="none" stroke="#6de2db" stroke-opacity=".25">
                                <ellipse cx="230" cy="200" rx="102" ry="38"/><ellipse cx="230" cy="200" rx="102" ry="73"/>
                                <ellipse cx="230" cy="200" rx="38" ry="102"/><ellipse cx="230" cy="200" rx="73" ry="102"/>
                                <path d="M128 200h204M230 98v204"/>
                            </g>
                        </g>
                        <g class="ab-orbit-track" fill="none" stroke="url(#ab-orbit-line)" stroke-width="1.5">
                            <ellipse cx="230" cy="200" rx="194" ry="66" transform="rotate(-30 230 200)"/>
                            <ellipse cx="230" cy="200" rx="161" ry="119" transform="rotate(42 230 200)" opacity=".5"/>
                        </g>
                        <g class="ab-orbit-satellite"><circle cx="398" cy="102" r="5" fill="#a5fff0"/><circle cx="398" cy="102" r="11" fill="none" stroke="#6de2db" stroke-opacity=".35"/></g>
                        <g fill="#a5c3d8" font-family="monospace" font-size="10" letter-spacing="2">
                            <text x="31" y="51">IDEAS IN ORBIT</text><text x="289" y="363">KEEP EXPLORING</text>
                        </g>
                    </svg>
                    <span class="ab-orbit-label ab-orbit-label-one">01 / HARDWARE</span>
                    <span class="ab-orbit-label ab-orbit-label-two">02 / INTELLIGENCE</span>
                    <span class="ab-orbit-core">A<span>✦</span></span>
                </div>
                <div class="ab-hero-footer"><span>CODE · HARDWARE · COSMOS</span><span>持续探索，持续构建 <i aria-hidden="true">↗</i></span></div>`;
            hero.querySelector('h1').textContent = home.querySelector('.banners-title-big')?.textContent.trim() || '半截的诗';
            const source = home.querySelector('.banners-title-small');
            hero.querySelector('.ab-hero-description').textContent = source?.firstChild?.textContent.trim() || '在代码、硬件与星空之间，记录每一次探索。';
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
                for (const entry of entries) entry.target.classList.toggle('ab-orbit-paused', document.hidden || !entry.isIntersecting);
            });
            observer.observe(hero);
        }
        hero.classList.toggle('ab-orbit-paused', document.hidden);
    };
    document.addEventListener('visibilitychange', () => {
        if (activeHero) {
            const rect = activeHero.getBoundingClientRect();
            activeHero.classList.toggle('ab-orbit-paused', document.hidden || rect.bottom <= 0 || rect.top >= innerHeight);
        }
    });
    window.__abInstallSpaceHero = install;
    document.addEventListener('pjax:complete', install);
    if (document.readyState === 'loading') document.addEventListener('DOMContentLoaded', install, {once: true});
    else install();
})();
