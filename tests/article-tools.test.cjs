const test = require('node:test');
const assert = require('node:assert/strict');
const {fragment, claimId, publicUrl} = require('../customization/article-tools.js');

test('encoded CMS IDs survive one fragment decoding step', () => {
    const id = '%E5%8F%8C%E7%BD%91';
    const hash = fragment(id);
    assert.equal(decodeURIComponent(hash.slice(1)), id);
    assert.equal(new URL(publicUrl('https://aerospaceboy.site/archives/demo', 'https://aerospaceboy.site/archives/demo', id)).hash, hash);
});
test('new heading IDs are stable across unrelated insertions and avoid collisions', () => {
    const first = claimId('', '三项分别做什么', new Set());
    const occupied = new Set(['outside-id']);
    claimId('', '另一个标题', occupied);
    assert.equal(claimId('', '三项分别做什么', occupied), first);
    assert.equal(claimId('', '三项分别做什么', occupied), first + '-2');
    assert.notEqual(claimId('outside-id', '三项分别做什么', occupied), 'outside-id');
});
test('existing unique heading IDs stay unchanged', () => {
    const occupied = new Set();
    assert.equal(claimId('original-anchor', 'Title', occupied), 'original-anchor');
    assert.notEqual(claimId('original-anchor', 'Title', occupied), 'original-anchor');
});
test('copied article URL excludes tracking and stale section fragments', () => {
    assert.equal(publicUrl('https://aerospaceboy.site/archives/demo', 'https://aerospaceboy.site/archives/demo?utm_source=test#old'), 'https://aerospaceboy.site/archives/demo');
});
test('another origin or article cannot become the copied canonical', () => {
    for (const canonical of ['https://example.com/archives/demo', 'https://aerospaceboy.site/archives/other', 'javascript:alert(1)']) {
        assert.equal(publicUrl(canonical, 'https://aerospaceboy.site/archives/demo'), 'https://aerospaceboy.site/archives/demo');
    }
});
