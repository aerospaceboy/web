const {test} = require('node:test');
const assert = require('node:assert/strict');
const {simulate, DEFAULTS} = require('../customization/pid-lab.js');

test('zero gains keep the undisturbed zero state and report full end error', () => {
    const result = simulate({kp:0,ki:0,kd:0});
    assert.ok(result.points.every(point => point.y===0 && point.u===0));
    assert.equal(result.error,1);assert.equal(result.overshoot,0);
});

test('P response agrees with the closed-form second order solution', () => {
    const result = simulate({kp:2,ki:0,kd:0});
    for (const point of result.points) {
        const expected = 2/3*(1-Math.exp(-point.t)*(Math.cos(Math.sqrt(2)*point.t)+Math.sin(Math.sqrt(2)*point.t)/Math.sqrt(2)));
        assert.ok(Math.abs(point.y-expected)<2e-8, `P at ${point.t}`);
    }
    assert.ok(Math.abs(result.end-2/3)<1e-8);
});

test('default PID agrees with its analytic triple-pole response', () => {
    const result = simulate(DEFAULTS);
    for (const point of result.points) {
        const expected = 1 + Math.exp(-point.t)*(-1-point.t+point.t*point.t/2);
        assert.ok(Math.abs(point.y-expected)<2e-8, `PID at ${point.t}`);
    }
    assert.ok(Math.abs(result.overshoot-300*Math.exp(-4))<1e-6);
    assert.equal(result.limitedFraction,0);
});

test('load disturbance has the analytic P offset and no effect before t=10', () => {
    const plain = simulate({kp:2,ki:0,kd:0});
    const loaded = simulate({kp:2,ki:0,kd:0},{disturbance:true});
    for (let i=0;i<=1000;i++) assert.equal(plain.points[i].y,loaded.points[i].y);
    assert.ok(Math.abs(loaded.end-(2-.3)/3)<1e-5);
    assert.ok(simulate(DEFAULTS,{disturbance:true}).error < .002);
});

test('gain range corners stay finite, respect actuator limits and converge under step refinement', () => {
    for (const kp of [0,12]) for (const ki of [0,6]) for (const kd of [0,6]) {
        const gains = {kp,ki,kd}, coarse = simulate(gains,{disturbance:true}), fine = simulate(gains,{dt:.005,disturbance:true});
        assert.ok(coarse.points.every(point => Number.isFinite(point.y) && Math.abs(point.u)<=3));
        assert.ok(Math.abs(coarse.end-fine.end)<.02, JSON.stringify(gains));
        assert.ok(Math.abs(coarse.overshoot-fine.overshoot)<1, JSON.stringify(gains));
    }
    assert.ok(simulate({kp:12,ki:6,kd:0}).limitedFraction>0);
});

test('invalid gains or unbounded integration options are rejected', () => {
    for (const kp of [-1,13,Infinity,NaN,'2']) assert.throws(()=>simulate({kp,ki:1,kd:1}),RangeError);
    for (const options of [{dt:0},{dt:.1},{dt:.013},{duration:Infinity}]) assert.throws(()=>simulate(DEFAULTS,options),RangeError);
});
