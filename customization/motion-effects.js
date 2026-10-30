/* Bounded CSS atmosphere and a single-timer typewriter. No fetched assets. */
(() => {
    if (window.__abInstallMotion) { window.__abInstallMotion();return; }
    const key = 'ab:motion:v1';
    const root = document.documentElement;
    const reduced = matchMedia('(prefers-reduced-motion: reduce)');
    const small = matchMedia('(max-width: 768px)');
    const connection = navigator.connection;
    let preferences = {ambient: 'sakura', typing: true};
    let canSave = true;
    let layer, target, visibleHero, observer, timer = 0;
    let phrases = [], phraseIndex = 0, length = 0, deleting = true, heroVisible = false;
    const parse = value => {
        const item = JSON.parse(value);
        return {ambient: ['sakura', 'fireflies', 'off'].includes(item?.ambient) ? item.ambient : 'sakura', typing: item?.typing !== false};
    };
    try { preferences = parse(localStorage.getItem(key)); } catch { canSave = false; }
    const allowed = () => !reduced.matches && !connection?.saveData && !root.classList.contains('ab-calm-mode');
    const stop = () => { if (timer) clearTimeout(timer);timer = 0; };
    const drawText = () => {
        const text = target?.querySelector('.ab-typewriter-text');
        if (text) text.textContent = Array.from(phrases[phraseIndex]).slice(0, length).join('');
    };
    const canType = () => !!target?.isConnected && allowed() && preferences.typing && !document.hidden && heroVisible;
    const tick = () => {
        timer = 0;
        if (!canType()) { syncTyping();return; }
        let delay;
        if (deleting) {
            length = Math.max(0, length - 1);delay = 55;
            if (!length) { phraseIndex = (phraseIndex + 1) % phrases.length;deleting = false;delay = 320; }
        } else {
            length = Math.min(Array.from(phrases[phraseIndex]).length, length + 1);delay = 110;
            if (length === Array.from(phrases[phraseIndex]).length) { deleting = true;delay = 2600; }
        }
        drawText();timer = setTimeout(tick, delay);
    };
    const syncTyping = () => {
        if (!target?.isConnected) { stop();return; }
        const running = canType();target.classList.toggle('ab-typewriter-running', running);
        if (!running) {
            stop();phraseIndex = 0;length = Array.from(phrases[0]).length;deleting = true;drawText();
        } else if (!timer) timer = setTimeout(tick, 2200);
    };
    const syncAmbient = () => {
        if (!document.body) return;
        if (!allowed() || preferences.ambient === 'off') { layer?.remove();layer = null;return; }
        const count = small.matches ? 10 : 22;
        if (!layer?.isConnected) {
            layer = document.createElement('div');layer.id = 'ab-ambient-effects';
            layer.setAttribute('aria-hidden', 'true');document.body.append(layer);
        }
        layer.dataset.mode = preferences.ambient;
        if (layer.children.length === count) return;
        layer.replaceChildren();
        let seed = 105703;
        const random = () => ((seed = (seed * 1664525 + 1013904223) >>> 0) / 4294967296);
        for (let i = 0; i < count; i++) {
            const track = document.createElement('span');track.className = 'ab-fall-track';
            track.style.left = `${((i + random()) / count * 100).toFixed(2)}%`;
            track.style.setProperty('--ab-fall-size', `${(7 + random() * 6).toFixed(1)}px`);
            track.style.setProperty('--ab-fall-drift', `${(-65 + random() * 130).toFixed(1)}px`);
            const duration = 16 + random() * 14;
            track.style.setProperty('--ab-fall-duration', `${duration.toFixed(2)}s`);
            track.style.setProperty('--ab-fall-delay', `${(-random() * duration).toFixed(2)}s`);
            track.style.setProperty('--ab-fall-sway', `${(3 + random() * 4).toFixed(2)}s`);
            const petal = document.createElement('i');petal.className = 'ab-fall-particle';
            track.append(petal);layer.append(track);
        }
    };
    const sync = () => {
        root.classList.toggle('ab-motion-enabled', allowed());
        root.classList.toggle('ab-motion-paused', document.hidden);
        root.dataset.abAmbientMode = preferences.ambient;
        for (const select of document.querySelectorAll('select[data-ab-ambient]')) select.value = preferences.ambient;
        for (const button of document.querySelectorAll('[data-ab-typing]')) {
            button.setAttribute('aria-checked', String(preferences.typing));
            button.querySelector('.ab-switch-state').textContent = preferences.typing ? '已开启' : '已关闭';
        }
        for (const note of document.querySelectorAll('.ab-motion-note')) {
            note.textContent = !allowed() ? '已按减少动效或节省流量偏好暂停。' : canSave ? '可随时切换，选择保存在此浏览器。' : '当前浏览器无法保存，选择在本次访问内生效。';
        }
        syncAmbient();syncTyping();
    };
    const install = () => {
        for (const slot of document.querySelectorAll('[data-ab-motion-settings]')) {
            if (slot.children.length) continue;
            slot.innerHTML = `<label class="ab-ambient-label"><span>氛围特效</span>
                <select data-ab-ambient><option value="sakura">樱花飘落</option><option value="fireflies">流萤光点</option><option value="off">关闭飘落与光点</option></select></label>
                <button class="ab-calm-switch ab-typing-switch" type="button" role="switch" aria-checked="true" data-ab-typing>
                    <span>首页打字字幕</span><span class="ab-switch-state">已开启</span>
                </button><p class="ab-motion-note"></p>`;
        }
        const next = document.querySelector('#ab-space-hero .ab-hero-english');
        if (next !== target) {
            stop();observer?.disconnect();target = next;visibleHero = target?.closest('#ab-space-hero');
            if (target) {
                phrases = [target.textContent.trim() || '写代码，也仰望星空。', '让想法在代码里生长。', '在代码与星空之间探索。'];
                target.setAttribute('aria-label', phrases[0]);
                target.innerHTML = '<span class="ab-typewriter-text" aria-hidden="true"></span><span class="ab-typewriter-caret" aria-hidden="true"></span>';
                phraseIndex = 0;length = Array.from(phrases[0]).length;deleting = true;drawText();
                const rect = visibleHero.getBoundingClientRect();heroVisible = rect.bottom > 0 && rect.top < innerHeight;
                if ('IntersectionObserver' in window) {
                    observer = new IntersectionObserver(entries => { heroVisible = entries[0].isIntersecting;syncTyping(); });
                    observer.observe(visibleHero);
                }
            }
        }
        sync();
    };
    const save = () => {
        try { localStorage.setItem(key, JSON.stringify(preferences));canSave = true; } catch { canSave = false; }
        sync();
    };
    document.addEventListener('change', event => {
        if (!(event.target instanceof HTMLSelectElement) || !event.target.matches('[data-ab-ambient]')) return;
        preferences.ambient = ['sakura', 'fireflies', 'off'].includes(event.target.value) ? event.target.value : 'sakura';save();
    });
    document.addEventListener('click', event => {
        if (!(event.target instanceof Element) || !event.target.closest('[data-ab-typing]')) return;
        preferences.typing = !preferences.typing;save();
    });
    document.addEventListener('ab:preferences', sync);
    document.addEventListener('visibilitychange', sync);
    document.addEventListener('pjax:send', stop);
    document.addEventListener('pjax:complete', install);
    reduced.addEventListener('change', sync);small.addEventListener('change', sync);
    connection?.addEventListener('change', sync);
    window.addEventListener('storage', event => {
        if (event.key !== key) return;
        try { preferences = parse(event.newValue); } catch { return; }sync();
    });
    window.__abInstallMotion = install;
    if (document.readyState === 'loading') document.addEventListener('DOMContentLoaded', install, {once:true});else install();
})();
