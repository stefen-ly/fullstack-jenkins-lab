import test from 'node:test';
import assert from 'node:assert/strict';
import { normalizeTitle, taskStats } from './taskHelpers.js';

test('trims whitespace around task titles', () => {
  assert.equal(normalizeTitle('  Learn Jenkins  '), 'Learn Jenkins');
});

test('calculates completion statistics', () => {
  assert.deepEqual(taskStats([
    { completed: false }, { completed: true }, { completed: false }
  ]), { total: 3, complete: 1, remaining: 2 });
});
