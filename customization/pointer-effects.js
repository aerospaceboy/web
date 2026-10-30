/* Decorative pointer light: bounded pool, no network and no idle animation loop. */
(() => {
    if (window.__abInstallPointerLight) {
        window.__abInstallPointerLight();
        return;
    }
    const fine = matchMedia('(hover: hover) and (pointer: fine)');
    const reduced = matchMedia('(prefers-reduced-motion: reduce)');
    const connection = navigator.connection;
    let layer, halo, sparks = [], enabled = false, frame = 0, point, previous, index = 0;

    const hide = () => {
        if (frame) cancelAnimationFrame(frame);
        frame = 0;point = null;previous = null;
        if (layer) layer.classList.remove('ab-pointer-visible');
        for (const item of sparks) item.animation?.cancel();
    };
    const move = event => {
        if (event.pointerType !== 'mouse' || document.hidden) return;
        point = {x: event.clientX, y: event.clientY, time: event.timeStamp};
        if (frame) return;
        frame = requestAnimationFrame(() => {
            frame = 0;
            if (!point || !layer?.isConnected) return;
            const {x, y, time} = point;
            layer.classList.add('ab-pointer-visible');
            halo.style.transform = `translate3d(${x}px, ${y}px, 0)`;
            if (!previous) previous = {x, y, time};
            const distance = Math.hypot(x - previous.x, y - previous.y);
            if (distance >= 18 && time - previous.time >= 35) {
                const item = sparks[index++ % sparks.length];
                item.animation?.cancel();
                item.animation = item.element.animate([
                    {transform: `translate3d(${x}px, ${y}px, 0) scale(1)`, opacity: .8},
                    {transform: `translate3d(${x - 7}px, ${y - 18}px, 0) scale(.2)`, opacity: 0}
                ], {duration: 480, easing: 'ease-out', fill: 'forwards'});
                previous = {x, y, time};
            }
        });
    };
    const leave = event => {
        if (!event.relatedTarget || event.relatedTarget.tagName === 'IFRAME') hide();
    };
    const sync = () => {
        hide();
        if (!document.body) return;
        const allowed = fine.matches && !reduced.matches && !connection?.saveData && !document.documentElement.classList.contains('ab-calm-mode');
        if (!allowed) {
            if (enabled) document.removeEventListener('pointermove', move);
            enabled = false;
            layer?.remove();layer = null;halo = null;sparks = [];
            return;
        }
        if (!layer?.isConnected) {
            layer = document.createElement('div');layer.id = 'ab-pointer-light';
            layer.setAttribute('aria-hidden', 'true');
            halo = document.createElement('div');halo.className = 'ab-pointer-halo';
            layer.append(halo);
            sparks = Array.from({length: 12}, () => {
                const element = document.createElement('span');
                element.className = 'ab-pointer-spark';element.textContent = '✦';
                layer.append(element);
                return {element, animation: null};
            });
            document.body.append(layer);
        }
        if (!enabled) document.addEventListener('pointermove', move, {passive: true});
        enabled = true;
    };
    fine.addEventListener('change', sync);
    reduced.addEventListener('change', sync);
    connection?.addEventListener('change', sync);
    document.addEventListener('ab:preferences', sync);
    document.addEventListener('pointerout', leave);
    window.addEventListener('blur', hide);
    document.addEventListener('visibilitychange', () => { if (document.hidden) hide(); });
    document.addEventListener('pjax:send', hide);
    document.addEventListener('pjax:complete', sync);
    window.__abInstallPointerLight = sync;
    if (document.readyState === 'loading') document.addEventListener('DOMContentLoaded', sync, {once: true});
    else sync();
})();
