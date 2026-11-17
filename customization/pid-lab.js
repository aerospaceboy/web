/* Normalized teaching model, evaluated only when its article is opened or edited. */
(() => {
    const DEFAULTS = Object.freeze({kp:2, ki:1, kd:1});
    const LIMITS = Object.freeze({kp:12, ki:6, kd:6});
    const clamp = value => Math.max(-3, Math.min(3, value));
    const simulate = (gains, {dt = .01, duration = 20, disturbance = false} = {}) => {
        for (const key of Object.keys(LIMITS)) {
            if (!Number.isFinite(gains[key]) || gains[key] < 0 || gains[key] > LIMITS[key]) throw new RangeError('Invalid PID gain');
        }
        if (!Number.isFinite(dt) || dt < .001 || dt > .02 || duration !== 20) throw new RangeError('Invalid integration window');
        const steps = Math.round(duration / dt);
        if (Math.abs(steps * dt - duration) > 1e-9) throw new RangeError('Step must divide the time window');
        const {kp,ki,kd} = gains;
        const rawControl = state => kp * (1 - state[0]) + ki * state[2] - kd * state[1];
        const derivative = (state, load) => {
            const error = 1 - state[0], raw = rawControl(state);
            const blocked = (raw >= 3 && error > 0) || (raw <= -3 && error < 0);
            return [state[1], clamp(raw) + load - 2 * state[1] - state[0], ki && !blocked ? error : 0];
        };
        const add = (state, slope, scale) => state.map((value, index) => value + slope[index] * scale);
        let state = [0,0,0], limited = 0;
        const points = [];
        for (let index = 0; index <= steps; index++) {
            const t = index * dt, raw = rawControl(state);
            points.push({t, y:state[0], u:clamp(raw)});
            if (index === steps) break;
            if (Math.abs(raw) >= 3) limited++;
            // The load is held constant for each step; the event is aligned at t=10.
            const load = disturbance && t >= 10 - 1e-9 ? -.3 : 0;
            const a = derivative(state, load), b = derivative(add(state,a,dt/2), load);
            const c = derivative(add(state,b,dt/2), load), d = derivative(add(state,c,dt), load);
            state = state.map((value,j) => value + dt * (a[j] + 2*b[j] + 2*c[j] + d[j]) / 6);
            if (!state.every(Number.isFinite)) throw new RangeError('Non-finite model state');
        }
        const end = points[points.length-1].y;
        const peak = points.reduce((value, point) => Math.max(value,point.y), 0);
        return {points, end, error:Math.abs(1-end), overshoot:Math.max(0,peak-1)*100, limitedFraction:limited/steps};
    };
    if (typeof module !== 'undefined' && module.exports) { module.exports = {simulate, DEFAULTS, LIMITS};return; }
    if (window.__abInstallPidLab) { window.__abInstallPidLab();return; }
    const install = () => {
        if (location.pathname.replace(/\/$/, '') !== '/archives/pid-control-intro') return;
        const article = document.querySelector('#post #article-container');
        if (!article || article.querySelector('#ab-pid-lab')) return;
        const panel = document.createElement('section');
        panel.id = 'ab-pid-lab';panel.dataset.abNoCount = '';panel.setAttribute('aria-labelledby','ab-pid-title');
        panel.innerHTML = `
            <div class="ab-pid-heading"><div><span class="ab-pid-eyebrow">CONTROL LAB / 01</span><p id="ab-pid-title">亲手调一条响应曲线</p></div><span class="ab-pid-badge">教学数值模拟</span></div>
            <p class="ab-pid-intro">拖动参数，对照同一对象的响应。先试 P，再加入 I 与 D，看看曲线如何改变。</p>
            <div class="ab-pid-presets" role="group" aria-label="PID 教学预设">
                <button type="button" data-preset="p">只用 P</button><button type="button" data-preset="pi">加入 I</button><button type="button" data-preset="pid">加入 D</button><button type="button" class="ab-pid-reset">恢复默认</button>
            </div>
            <div class="ab-pid-controls"></div>
            <label class="ab-pid-load"><input type="checkbox">在 t = 10 时加入 −0.3 恒定输入扰动</label>
            <div class="ab-pid-legend"><span class="ab-pid-current">当前参数</span><span class="ab-pid-baseline">P 基线（2, 0, 0）</span><span class="ab-pid-target">目标 = 1</span></div>
            <div class="ab-pid-chart"><div class="ab-pid-y" aria-hidden="true"><span></span><span></span><span></span></div><div class="ab-pid-plot"><svg viewBox="0 0 600 240" preserveAspectRatio="none" role="img" aria-label="单位阶跃响应对比图，数值摘要见下方" aria-describedby="ab-pid-results">
                <path class="ab-pid-grid" d="M0 0H600M0 120H600M0 240H600M150 0V240M300 0V240M450 0V240"></path>
                <path class="ab-pid-reference"></path><path class="ab-pid-p"></path><path class="ab-pid-response"></path>
            </svg><div class="ab-pid-x" aria-hidden="true"><span>0</span><span>5</span><span>10</span><span>15</span><span>20</span></div></div></div>
            <p class="ab-pid-axis">横轴：归一化时间 t　纵轴：输出 y</p>
            <div id="ab-pid-results" class="ab-pid-results"><div>时窗末值<strong data-result="end"></strong></div><div>最大超调<strong data-result="overshoot"></strong></div><div>末端绝对误差<strong data-result="error"></strong></div></div>
            <p class="ab-pid-status" role="status" aria-live="polite"></p>
            <details class="ab-pid-model"><summary>模型、算法与结果边界</summary><div>
                <p>归一化对象：y″ + 2y′ + y = u + d；零初值，目标 r = 1，观察 t = 0…20。参数没有对应具体设备单位。</p>
                <p>控制律：u = clip(Kp(1 − y) + Ki·I − Kd·y′, −3, 3)。微分作用于输出，避免目标阶跃的微分冲击；理想模型直接使用 y′，未模拟传感器噪声或微分滤波。限幅且误差继续推向饱和时暂停积分，否则 I′ = 1 − y；Ki = 0 时冻结积分。</p>
                <p>连续闭环模型采用 RK4 数值积分，步长 0.01；不是原文离散伪代码的逐行运行。勾选扰动后，d 在 t = 10 从 0 变为 −0.3，两条曲线使用相同扰动。基线固定为 Kp = 2、Ki = Kd = 0。</p>
                <p>最大超调 = max(0, max(y) − 1) × 100%；末端误差只描述 t = 20，不能证明已经稳定。预设仅用于此模型，不是硬件调参建议，也不代表比赛实测。</p>
                <p>基础概念参考 <a href="https://ctms.engin.umich.edu/CTMS/index.php?example=Introduction&amp;section=ControlPID" target="_blank" rel="noopener noreferrer">密歇根大学 CTMS：PID Controller Design</a>；本页模型和预设为本站教学示例。</p>
            </div></details>`;
        for (const [key,label] of Object.entries({kp:'P · 比例',ki:'I · 积分',kd:'D · 微分'})) {
            const row = document.createElement('label');row.className = 'ab-pid-control';
            row.innerHTML = `<span>${label}<output for="ab-pid-${key}"></output></span><input id="ab-pid-${key}" type="range" min="0" max="${LIMITS[key]}" step="0.1" value="${DEFAULTS[key]}">`;
            panel.querySelector('.ab-pid-controls').append(row);
        }
        const inputs = Object.fromEntries(Object.keys(DEFAULTS).map(key => [key,panel.querySelector('#ab-pid-'+key)]));
        const loadInput = panel.querySelector('.ab-pid-load input');
        let baseline, baselineLoad;
        const render = (announce = false) => {
            const gains = Object.fromEntries(Object.entries(inputs).map(([key,input]) => [key,Number(input.value)]));
            for (const input of Object.values(inputs)) input.parentElement.querySelector('output').value = Number(input.value).toFixed(1);
            const result = simulate(gains, {disturbance:loadInput.checked});
            if (!baseline || baselineLoad !== loadInput.checked) { baseline = simulate({kp:2,ki:0,kd:0},{disturbance:loadInput.checked});baselineLoad = loadInput.checked; }
            const all = result.points.concat(baseline.points);
            const low = Math.min(0,...all.map(point => point.y)), high = Math.max(1,...all.map(point => point.y));
            const padding = Math.max(.08,(high-low)*.08), bottom = low-padding, top = high+padding;
            const y = value => 240 * (top-value)/(top-bottom);
            const path = points => points.filter((point,index) => index%4===0 || index===points.length-1).map((point,index) => (index?'L':'M')+(point.t*30).toFixed(2)+' '+y(point.y).toFixed(2)).join('');
            panel.querySelector('.ab-pid-response').setAttribute('d',path(result.points));
            panel.querySelector('.ab-pid-p').setAttribute('d',path(baseline.points));
            panel.querySelector('.ab-pid-reference').setAttribute('d',`M0 ${y(1).toFixed(2)}H600`);
            [top,(top+bottom)/2,bottom].forEach((value,index) => panel.querySelectorAll('.ab-pid-y span')[index].textContent = value.toFixed(2));
            const errorText = result.error > 0 && result.error < .001 ? '< 0.001' : result.error.toFixed(3);
            for (const [key,value] of Object.entries({end:result.end.toFixed(3),overshoot:result.overshoot.toFixed(1)+'%',error:errorText})) panel.querySelector('[data-result="'+key+'"]').textContent = value;
            for (const button of panel.querySelectorAll('[data-preset]')) {
                const preset = {p:{kp:2,ki:0,kd:0},pi:{kp:2,ki:1,kd:0},pid:DEFAULTS}[button.dataset.preset];
                button.setAttribute('aria-pressed',String(Object.keys(preset).every(key => preset[key] === gains[key])));
            }
            const message = `t = 20 时，输出 ${result.end.toFixed(3)}，绝对误差 ${errorText}。控制输出限幅占比 ${(result.limitedFraction*100).toFixed(1)}%。`;
            if (announce || !panel.querySelector('.ab-pid-status').textContent) panel.querySelector('.ab-pid-status').textContent = message;
        };
        for (const input of Object.values(inputs)) {
            input.addEventListener('input',() => render());input.addEventListener('change',() => render(true));
        }
        loadInput.addEventListener('change',() => render(true));
        const setPreset = preset => { for (const key of Object.keys(inputs)) inputs[key].value = preset[key];render(true); };
        for (const button of panel.querySelectorAll('[data-preset]')) button.addEventListener('click',() => setPreset({p:{kp:2,ki:0,kd:0},pi:{kp:2,ki:1,kd:0},pid:DEFAULTS}[button.dataset.preset]));
        panel.querySelector('.ab-pid-reset').addEventListener('click',() => { loadInput.checked = false;setPreset(DEFAULTS); });
        article.insertBefore(panel,article.querySelector('h2') || article.firstChild);
        render();
    };
    window.__abInstallPidLab = install;
    document.addEventListener('pjax:complete',install);
    if (document.readyState === 'loading') document.addEventListener('DOMContentLoaded',install,{once:true});
    else install();
})();
