import assert from 'node:assert/strict';
import { test } from 'node:test';

import { MAX_HISTORY, addRecord, formatWhen, parseHistory, removeRecord, summarize } from './history.ts';
import type { ScanRecord } from './types.ts';

function record(id: string, counts: Partial<Record<'paper' | 'plastic' | 'metal' | 'organic', number>> = {}): ScanRecord {
  const full = { paper: 0, plastic: 0, metal: 0, organic: 0, ...counts };
  const total = full.paper + full.plastic + full.metal + full.organic;
  return {
    id,
    createdAt: '2026-11-14T10:00:00.000Z',
    photoUri: `file:///${id}.jpg`,
    response: {
      success: true,
      image_width: 100,
      image_height: 100,
      total_objects: total,
      counts: full,
      detections: [],
      message: null,
    },
    guidance: [],
  };
}

test('addRecord puts the newest scan first', () => {
  const { history, removed } = addRecord([record('a')], record('b'));
  assert.deepEqual(history.map((r) => r.id), ['b', 'a']);
  assert.deepEqual(removed, []);
});

test('addRecord drops the oldest scans past the limit and reports them', () => {
  const full = Array.from({ length: MAX_HISTORY }, (_, i) => record(`old${i}`));
  const { history, removed } = addRecord(full, record('new'));
  assert.equal(history.length, MAX_HISTORY);
  assert.equal(history[0].id, 'new');
  assert.deepEqual(removed.map((r) => r.id), [`old${MAX_HISTORY - 1}`]);
});

test('removeRecord removes only the matching scan', () => {
  assert.deepEqual(removeRecord([record('a'), record('b')], 'a').map((r) => r.id), ['b']);
});

test('summarize totals scans, items and the top category', () => {
  const summary = summarize([record('a', { plastic: 2, paper: 1 }), record('b', { plastic: 1, organic: 2 })]);
  assert.equal(summary.scans, 2);
  assert.equal(summary.items, 6);
  assert.deepEqual(summary.counts, { paper: 1, plastic: 3, metal: 0, organic: 2 });
  assert.equal(summary.topCategory, 'plastic');
});

test('summarize of an empty history has no top category', () => {
  assert.deepEqual(summarize([]), {
    scans: 0,
    items: 0,
    counts: { paper: 0, plastic: 0, metal: 0, organic: 0 },
    topCategory: null,
  });
});

test('formatWhen gives relative labels then a date', () => {
  const now = new Date('2026-11-14T12:00:00.000Z');
  assert.equal(formatWhen('2026-11-14T11:59:40.000Z', now), 'Just now');
  assert.equal(formatWhen('2026-11-14T11:55:00.000Z', now), '5 min ago');
  assert.equal(formatWhen('2026-11-14T09:00:00.000Z', now), '3 h ago');
  assert.equal(formatWhen('2026-11-13T10:00:00.000Z', now), 'Yesterday');
  assert.match(formatWhen('2026-10-01T10:00:00.000Z', now), /^\d{1,2} (Sep|Oct) 2026$/);
  assert.equal(formatWhen('not a date', now), '');
});

test('parseHistory ignores broken or unexpected data', () => {
  assert.deepEqual(parseHistory(null), []);
  assert.deepEqual(parseHistory('not json'), []);
  assert.deepEqual(parseHistory('{"a":1}'), []);
  const good = record('a');
  assert.deepEqual(parseHistory(JSON.stringify([good, { id: 5 }, null])), [good]);
});
