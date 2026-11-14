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

// The results screen shows the photo in a frame with the photo's own shape,
// so there is no letterboxing: a percentage of the image is a percentage of
// the frame. These cases cover the photo shapes a phone produces.

test('portrait photo: boxes scale by the photo, not by the screen', () => {
  assert.deepEqual(boxToPercent([120, 320, 360, 960], 480, 1280), {
    left: '25%',
    top: '25%',
    width: '50%',
    height: '50%',
  });
});

test('square photo', () => {
  assert.deepEqual(boxToPercent([100, 200, 300, 400], 1000, 1000), {
    left: '10%',
    top: '20%',
    width: '20%',
    height: '20%',
  });
});

test('boxes touching each edge of the photo stay inside the frame', () => {
  const [width, height] = [800, 600];
  const edges: [number, number, number, number][] = [
    [0, 100, 200, 300], // left
    [600, 100, 800, 300], // right
    [100, 0, 300, 150], // top
    [100, 450, 300, 600], // bottom
  ];
  for (const box of edges) {
    const style = boxToPercent(box, width, height);
    const left = parseFloat(style.left);
    const top = parseFloat(style.top);
    assert.ok(left >= 0 && left + parseFloat(style.width) <= 100, `${box} leaves the frame sideways`);
    assert.ok(top >= 0 && top + parseFloat(style.height) <= 100, `${box} leaves the frame vertically`);
  }
  assert.equal(boxToPercent([600, 100, 800, 300], width, height).left, '75%');
  assert.equal(boxToPercent([100, 450, 300, 600], width, height).top, '75%');
});

test('a very small box keeps its position and a non-zero size', () => {
  const style = boxToPercent([2000, 1500, 2004, 1503], 4000, 3000);
  assert.equal(style.left, '50%');
  assert.equal(style.top, '50%');
  assert.ok(parseFloat(style.width) > 0 && parseFloat(style.height) > 0);
});

test('the same box gives the same percentages whatever size the photo is shown at', () => {
  // A photo downscaled by the phone before display: half the pixels, same picture.
  assert.deepEqual(boxToPercent([400, 300, 800, 600], 1600, 1200), boxToPercent([200, 150, 400, 300], 800, 600));
});
