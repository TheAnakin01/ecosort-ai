import assert from 'node:assert/strict';
import { test } from 'node:test';

import { boxToPercent } from './boxes.ts';

test('converts pixels to percentages of the image', () => {
  assert.deepEqual(boxToPercent([320, 240, 960, 720], 1280, 960), {
    left: '25%',
    top: '25%',
    width: '50%',
    height: '50%',
  });
});

test('a box covering the whole image fills the frame', () => {
  assert.deepEqual(boxToPercent([0, 0, 480, 640], 480, 640), {
    left: '0%',
    top: '0%',
    width: '100%',
    height: '100%',
  });
});

test('boxes that spill outside the image are clipped to it', () => {
  assert.deepEqual(boxToPercent([-50, 900, 500, 1200], 1000, 1000), {
    left: '0%',
    top: '90%',
    width: '50%',
    height: '10%',
  });
});

test('rejects an image with no size', () => {
  assert.throws(() => boxToPercent([0, 0, 1, 1], 0, 100));
});
