export type BoxStyle = {
  left: `${number}%`;
  top: `${number}%`;
  width: `${number}%`;
  height: `${number}%`;
};

/**
 * Turn a box in image pixels into percentages of the image.
 *
 * The results screen shows the photo in a frame with the photo's own aspect
 * ratio, so a percentage of the image is also a percentage of the frame. That
 * keeps boxes aligned on every screen size without measuring anything.
 */
export function boxToPercent(
  bbox: readonly [number, number, number, number],
  imageWidth: number,
  imageHeight: number,
): BoxStyle {
  if (imageWidth <= 0 || imageHeight <= 0) {
    throw new Error('Image width and height must be positive');
  }
  const clamp = (value: number, max: number) => Math.min(Math.max(value, 0), max);
  const x1 = clamp(bbox[0], imageWidth);
  const y1 = clamp(bbox[1], imageHeight);
  const x2 = clamp(bbox[2], imageWidth);
  const y2 = clamp(bbox[3], imageHeight);

  return {
    left: `${(x1 / imageWidth) * 100}%`,
    top: `${(y1 / imageHeight) * 100}%`,
    width: `${((x2 - x1) / imageWidth) * 100}%`,
    height: `${((y2 - y1) / imageHeight) * 100}%`,
  };
}
