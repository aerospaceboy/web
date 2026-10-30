"""Motion assertions used by the real-page site-hub browser check."""

import json


def run_motion_checks(browser, base, output):
    snapshot = """(() => {
        const layer=document.querySelector('#ab-ambient-effects');
        const hero=document.querySelector('#ab-space-hero');
        const text=hero?.querySelector('.ab-typewriter-text');
        return {layers:document.querySelectorAll('#ab-ambient-effects').length,
            mode:layer?.dataset.mode,count:layer?.children.length||0,
            pointer:layer ? getComputedStyle(layer).pointerEvents:null,
            text:text?.textContent,typing:!!hero?.querySelector('.ab-typewriter-running'),
            fall:layer?.firstElementChild ? getComputedStyle(layer.firstElementChild).transform:null,
            fallState:layer?.firstElementChild ? getComputedStyle(layer.firstElementChild).animationPlayState:null,
            nebula:getComputedStyle(hero.querySelector('.ab-nebula-image')).transform,
            nebulaAnimation:getComputedStyle(hero.querySelector('.ab-nebula-image')).animationName,
            heroBottom:hero.getBoundingClientRect().bottom,
            choices:[...document.querySelectorAll('[data-ab-ambient]')].map(e=>e.value),
            overflow:document.documentElement.scrollWidth>innerWidth+1};
    })()"""
    def choose(mode):
        browser.evaluate("(() => {const abSelect=document.querySelector('#ab-preferences-card [data-ab-ambient]');"
                         "abSelect.value=" + json.dumps(mode) + ";abSelect.dispatchEvent(new Event('change',{bubbles:true}));return true})()")

    initial = browser.evaluate(snapshot)
    assert initial['layers'] == 1 and initial['count'] == 22 and initial['mode'] == 'sakura', initial
    assert initial['pointer'] == 'none' and initial['typing'] and not initial['overflow'], initial
    assert len(initial['choices']) == 2, initial
    browser.evaluate("new Promise(r=>setTimeout(r,350))", promise=True)
    moving = browser.evaluate(snapshot)
    assert moving['fall'] != initial['fall'] and moving['nebula'] != initial['nebula'], (initial,moving)
    before = browser.evaluate("document.querySelector('.ab-typewriter-text').textContent")
    changed = browser.evaluate("""new Promise(resolve=>{
        const before=""" + json.dumps(before) + """,deadline=performance.now()+4200;
        const poll=()=>{const text=document.querySelector('.ab-typewriter-text').textContent;
            if(text&&text!==before)resolve(true);else if(performance.now()>deadline)resolve(false);else setTimeout(poll,80)};poll();})""", promise=True)
    assert changed, 'The visible subtitle must actually type or erase, not just blink a cursor'
    click_through = browser.evaluate("""(() => {
        const a=document.querySelector('.ab-hero-primary'),r=a.getBoundingClientRect();
        return document.elementFromPoint(r.x+r.width/2,r.y+r.height/2).closest('a')===a;
    })()""")
    assert click_through, 'Particles must not intercept project links'
    browser.screenshot(output.parent / (output.stem + '-sakura.png'))

    choose('fireflies')
    fireflies = browser.evaluate(snapshot)
    assert fireflies['mode'] == 'fireflies' and fireflies['count'] == 22 and set(fireflies['choices']) == {'fireflies'}, fireflies
    assert browser.evaluate("JSON.parse(localStorage.getItem('ab:motion:v1')).ambient") == 'fireflies'
    browser.screenshot(output.parent / (output.stem + '-fireflies.png'))
    choose('off')
    browser.evaluate("document.querySelector('#ab-preferences-card [data-ab-typing]').click()")
    browser.navigate(base + '/')
    off = browser.evaluate(snapshot)
    assert off['layers'] == 0 and not off['typing'] and set(off['choices']) == {'off'}, off
    assert off['text'] == '写代码，也仰望星空。', off
    choose('sakura')
    browser.evaluate("document.querySelector('#ab-preferences-card [data-ab-typing]').click();for(let i=0;i<5;i++)document.dispatchEvent(new Event('pjax:complete'))")
    repeated = browser.evaluate(snapshot)
    assert repeated['layers'] == 1 and repeated['count'] == 22 and repeated['typing'], repeated
    assert browser.evaluate("document.querySelectorAll('.ab-typewriter-text').length") == 1
    assert browser.evaluate("document.querySelectorAll('#ab-preferences-card [data-ab-ambient]').length") == 1

    browser.evaluate("document.querySelector('#ab-preferences-card [data-ab-calm]').click()")
    calm = browser.evaluate(snapshot)
    assert calm['layers'] == 0 and not calm['typing'] and calm['nebulaAnimation'] == 'none', calm
    browser.evaluate("document.querySelector('#ab-preferences-card [data-ab-calm]').click()")
    browser.command('Emulation.setEmulatedMedia', {'features':[{'name':'prefers-reduced-motion','value':'reduce'}]})
    browser.evaluate("new Promise(r=>setTimeout(r,100))", promise=True)
    reduced = browser.evaluate(snapshot)
    assert reduced['layers'] == 0 and not reduced['typing'] and reduced['nebulaAnimation'] == 'none', reduced
    browser.command('Emulation.setEmulatedMedia', {'features':[{'name':'prefers-reduced-motion','value':'no-preference'}]})
    browser.evaluate("new Promise(r=>setTimeout(r,100))", promise=True)
    browser.evaluate("Object.defineProperty(navigator.connection,'saveData',{configurable:true,get:()=>true});navigator.connection.dispatchEvent(new Event('change'))")
    saving = browser.evaluate(snapshot)
    assert saving['layers'] == 0 and not saving['typing'], saving
    browser.evaluate("delete navigator.connection.saveData;navigator.connection.dispatchEvent(new Event('change'))")
    browser.evaluate("Object.defineProperty(document,'hidden',{configurable:true,get:()=>true});document.dispatchEvent(new Event('visibilitychange'))")
    hidden = browser.evaluate(snapshot)
    assert hidden['fallState'] == 'paused' and not hidden['typing'], hidden
    browser.evaluate("delete document.hidden;document.dispatchEvent(new Event('visibilitychange'));scrollTo({top:document.querySelector('#content-inner').getBoundingClientRect().top+scrollY,behavior:'instant'})")
    browser.evaluate("new Promise(r=>setTimeout(r,200))", promise=True)
    offscreen = browser.evaluate(snapshot)
    assert not offscreen['typing'] and offscreen['heroBottom'] <= 0, offscreen
    browser.evaluate("scrollTo({top:0,behavior:'instant'})")
    browser.evaluate("new Promise(r=>setTimeout(r,200))", promise=True)

    browser.command('Emulation.setDeviceMetricsOverride', {'width':390,'height':844,'deviceScaleFactor':1,'mobile':True})
    browser.evaluate("new Promise(r=>setTimeout(r,150))", promise=True)
    mobile = browser.evaluate(snapshot)
    assert mobile['count'] == 10 and not mobile['overflow'], mobile
    browser.screenshot(output.parent / (output.stem + '-motion-mobile.png'))
    browser.command('Emulation.setDeviceMetricsOverride', {'width':1440,'height':1000,'deviceScaleFactor':1,'mobile':False})

    injection = browser.command('Page.addScriptToEvaluateOnNewDocument', {'source':
        "Object.defineProperty(window,'localStorage',{configurable:true,get(){throw new DOMException('Blocked','SecurityError')}})"})
    try:
        browser.navigate(base + '/')
        unavailable = browser.evaluate(snapshot)
        assert unavailable['layers'] == 1 and unavailable['typing'], unavailable
        browser.evaluate("document.querySelector('#ab-preferences-card [data-ab-typing]').click()")
        assert not browser.evaluate(snapshot)['typing']
        assert browser.evaluate("document.querySelector('#ab-preferences-card .ab-motion-note').textContent.includes('无法保存')")
    finally:
        browser.command('Page.removeScriptToEvaluateOnNewDocument', {'identifier':injection['identifier']})
    browser.navigate(base + '/')
    return {'ambient_moves':True,'typewriter_changes':changed,'click_through':click_through,
            'fireflies':fireflies['count'],'persisted_off':off['layers']==0,'pjax_pool':repeated['count'],
            'calm':calm['layers']==0,'system_reduce':reduced['layers']==0,'save_data':saving['layers']==0,
            'synthetic_hidden_pause':hidden['fallState'],'mobile_particles':mobile['count'],'storage_unavailable':True}
