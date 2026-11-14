---
name: image-bounding-box-overlay
description: Implement accurate, responsive bounding-box overlays and detection labels for EcoSort AI scan results.
---

# Image Bounding-Box Overlay

## Goal

Draw each detector result over the exact image that was analyzed. Coordinate errors can make otherwise correct predictions unusable.

## Define one API coordinate contract

Prefer a documented convention such as `[x1, y1, x2, y2]` in original oriented-image pixel coordinates. Confirm the backend and model use this exact convention. Include image width/height and any required orientation metadata.

Never mix:
- normalized coordinates (0–1)
- resized model-input coordinates
- letterboxed coordinates
- original-image pixel coordinates

Convert explicitly at the API or UI boundary.

## Fit calculations

For an image of size `W × H` displayed in a container `Cw × Ch` using `contain`:
- `scale = min(Cw / W, Ch / H)`
- `renderedWidth = W * scale`
- `renderedHeight = H * scale`
- `offsetX = (Cw - renderedWidth) / 2`
- `offsetY = (Ch - renderedHeight) / 2`

For an original-image point `(x, y)`:
- `screenX = offsetX + x * scale`
- `screenY = offsetY + y * scale`

For boxes, transform both corners and derive positive width/height. Adapt the formula if the image is cropped, stretched, rotated, or rendered with a different content mode.

## UI requirements

- Draw all valid detections, including multiple boxes of the same class.
- Use consistent class colors and a readable legend.
- Keep labels inside the visible area where possible.
- Prevent labels from obscuring important image content more than necessary.
- Support small screens and different aspect ratios.
- Provide an accessible textual list of detections; do not rely on color alone.
- Handle zero detections, invalid boxes, and overlapping boxes gracefully.

## Tests

Test portrait, landscape, square, EXIF-rotated, letterboxed, and differently sized images. Use known synthetic coordinates and verify overlay positions at multiple container sizes. Include tests for clipping and edge-touching boxes.

## Do not

- Guess offsets.
- Scale x and y independently when using `contain`.
- assume detector boxes already match the rendered image.
- silently drop valid detections.
