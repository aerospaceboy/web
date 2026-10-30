/* Measure all three header regions; browser zoom changes the available CSS width. */
(() => {
    if (window.__abInstallHeaderLayout) { window.__abInstallHeaderLayout();return; }
    let group, observer, measuredMenu, menuWidth = 0, frame = 0;
    const outerWidth = element => {
        const style = getComputedStyle(element);
        if (style.display === 'none') return 0;
        return element.getBoundingClientRect().width +
            (parseFloat(style.marginLeft) || 0) + (parseFloat(style.marginRight) || 0);
    };
    const measure = () => {
        frame = 0;
        if (!group?.isConnected) return;
        const nav = group.closest('#nav');
        const brand = group.querySelector('#blog_name');
        const menu = group.querySelector('#menus > .menus_items');
        const tools = group.querySelector('#nav-right');
        if (!nav || !brand || !menu || !tools) return;
        if (measuredMenu !== menu) { measuredMenu = menu;menuWidth = 0; }
        const currentWidth = menu.getBoundingClientRect().width;
        // Hao temporarily hides this row while showing toolbar hover tips.
        // Zero is not a new intrinsic width: using it switches mode, moves the
        // hovered button and can repeatedly enter/leave the same hover state.
        if (currentWidth > 0) menuWidth = currentWidth;
        const style = getComputedStyle(group);
        // Exclude the compact toggle itself, so changing mode cannot cause oscillation.
        const toolWidth = [...tools.children].filter(e => e.id !== 'toggle-menu')
            .reduce((width, element) => width + outerWidth(element), 0);
        const available = group.clientWidth - (parseFloat(style.paddingLeft) || 0) -
            (parseFloat(style.paddingRight) || 0) - outerWidth(brand) - toolWidth -
            2 * (parseFloat(style.columnGap) || 0);
        const compact = innerWidth <= 768 || !menuWidth || menuWidth + 16 > available;
        nav.classList.toggle('ab-nav-compact', compact);
        nav.classList.toggle('ab-nav-wide', !compact);
        menu.inert = compact;
        menu.setAttribute('aria-hidden', String(compact));
        const toggle = tools.querySelector('#toggle-menu a');
        if (toggle) { toggle.setAttribute('aria-label', '打开主导航');toggle.title = '打开主导航'; }
    };
    const schedule = () => { if (!frame) frame = requestAnimationFrame(measure); };
    const install = () => {
        const next = document.querySelector('#nav-group');
        if (next !== group) {
            observer?.disconnect();group = next;
            if (group && typeof ResizeObserver !== 'undefined') {
                observer = new ResizeObserver(schedule);
                for (const selector of [':scope', '#blog_name', '#menus > .menus_items', '#nav-right']) {
                    const element = selector === ':scope' ? group : group.querySelector(selector);
                    if (element) observer.observe(element);
                }
            }
        }
        schedule();
    };
    window.__abInstallHeaderLayout = install;
    window.addEventListener('resize', schedule, {passive: true});
    document.addEventListener('pjax:complete', install);
    document.fonts?.ready.then(schedule);
    document.fonts?.addEventListener('loadingdone', schedule);
    if (document.readyState === 'loading') document.addEventListener('DOMContentLoaded', install, {once:true});
    else install();
})();
