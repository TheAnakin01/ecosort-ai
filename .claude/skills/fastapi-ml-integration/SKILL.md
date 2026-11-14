---
name: fastapi-ml-integration
description: Integrate EcoSort AI's trained object detector into a reliable FastAPI service with image validation, preprocessing, inference, and typed responses.
---

# FastAPI ML Integration

## Goal

Serve the approved detector through a small, reliable API. The initial architecture expects backend inference unless the product owner approves a change.

## Suggested API surface

Align with the repository's current API specification before changing routes. Candidate endpoints:
- `GET /health`
- `GET /api/v1/model-info`
- `GET /api/v1/categories`
- `POST /api/v1/detect`

## Detection response

Use a versioned, documented response schema. A detection should include:
- Stable class ID and canonical class name
- Confidence score in a documented range
- Bounding box in the agreed coordinate convention
- Optional display metadata only when genuinely available

Include original image dimensions and model/version metadata where useful. Keep class mapping consistent with training and mobile code.

## Upload validation

- Restrict accepted image MIME types and verify actual decodability.
- Enforce upload byte and pixel/dimension limits.
- Handle malformed, truncated, and decompression-bomb-like inputs safely.
- Correct orientation before inference and document the behavior.
- Do not trust filename extensions or client-supplied dimensions.
- Avoid logging image bytes or personal image content.
- Do not persist uploads by default.

## Inference lifecycle

Load the model once per worker/process using a controlled startup lifecycle. Avoid reloading weights for every request. Consider concurrency, CPU/GPU availability, worker count, memory, timeouts, and model thread safety.

Do not return placeholder detections when model loading or inference fails. Return a clear error status and log diagnostic details without leaking secrets.

## Performance and observability

Measure preprocessing, inference, postprocessing, and total request latency separately. Add health/readiness behavior that distinguishes service availability from model readiness. Avoid logging sensitive payloads.

## Testing

Cover:
- Valid image with multiple objects
- Valid image with no detections
- Invalid MIME/content
- Oversized payload and dimensions
- Corrupt image
- Model unavailable
- Inference exception
- Stable schema and coordinate mapping

Use a fake model only in isolated unit tests, never as production inference.
