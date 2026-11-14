# Backend and API Specification

## 1. Service

- Python + FastAPI + Uvicorn.
- Model loaded once per process.
- Pydantic request/response schemas.
- OpenAPI docs available in development.
- Versioned routes under `/api/v1`.

## 2. Proposed endpoints

### `GET /health`
Returns service liveness/readiness information. Do not expose secrets or internal infrastructure details.

Example:
```json
{
  "status": "ok",
  "model_loaded": true
}
```

### `GET /api/v1/model-info`
Returns safe model metadata:
```json
{
  "model_name": "yolo-nano-waste-detector",
  "model_version": "0.1.0",
  "classes": ["paper", "plastic", "metal", "organic"]
}
```
Values above are examples; implementation must return actual configured metadata.

### `GET /api/v1/categories`
Returns canonical category IDs, labels and general guidance identifiers.

### `POST /api/v1/detect`
Accept one image as `multipart/form-data`, field name `file`.

Illustrative success response:
```json
{
  "success": true,
  "image_width": 1280,
  "image_height": 960,
  "total_objects": 2,
  "counts": {
    "paper": 1,
    "plastic": 1,
    "metal": 0,
    "organic": 0
  },
  "detections": [
    {
      "id": 1,
      "category": "plastic",
      "confidence": 0.91,
      "bbox": [120, 80, 250, 390]
    },
    {
      "id": 2,
      "category": "paper",
      "confidence": 0.84,
      "bbox": [400, 150, 700, 620]
    }
  ],
  "model_version": "0.1.0"
}
```
This is a schema example, not a prediction or performance claim.

## 3. Response contract

- `image_width`, `image_height`: dimensions after consistent EXIF orientation handling.
- `total_objects`: equals `detections.length`.
- `counts`: include all four categories; sum equals total detections.
- `detections[].id`: unique within response.
- `category`: one of the four canonical strings.
- `confidence`: float in `[0,1]`.
- `bbox`: `[x1,y1,x2,y2]`, original oriented image pixel coordinates.
- `model_version`: actual deployed model version.

## 4. Error contract

Use consistent error responses, for example:
```json
{
  "success": false,
  "error": {
    "code": "UNSUPPORTED_IMAGE",
    "message": "Please upload a supported image file."
  },
  "request_id": "generated-request-id"
}
```

Suggested status codes:
- `400` malformed request.
- `413` upload too large.
- `415` unsupported media/decoded format.
- `422` image cannot be decoded or invalid dimensions.
- `429` rate limit exceeded, if rate limiting is configured.
- `500` unexpected server error.
- `503` model unavailable/not ready.
- `504` inference timeout, where applicable.

Do not expose stack traces or filesystem paths to clients.

## 5. Validation

- Allow only approved raster formats (e.g. JPEG, PNG, WebP if supported).
- Validate decoded content, not only filename extension or client MIME type.
- Configure maximum upload size and maximum pixel dimensions.
- Reject empty, corrupt or decompression-bomb-like images.
- Apply EXIF orientation consistently.
- Handle grayscale/RGBA inputs safely.
- Avoid writing uploads to disk unless required; clean temporary files.
- Do not log image bytes.

## 6. Inference service design

- Load model once at application startup/lifespan.
- Isolate model invocation behind a service class/function.
- Keep thresholds and image size in validated configuration.
- Return typed internal detection objects.
- Convert all boxes to original oriented-image coordinates.
- Catch expected inference errors and return safe API errors.
- Do not return mock detections when model loading fails.

## 7. Performance and concurrency

Measure before optimizing. Avoid blocking the event loop with long CPU inference; use an appropriate thread/process strategy after testing the selected runtime. Limit concurrent large uploads. Set request timeout and server resource limits. Document CPU/GPU runtime assumptions.

## 8. CORS and environment

- Restrict CORS origins to known development/production clients where applicable.
- Use environment variables for API configuration.
- Never ship backend secrets in the mobile bundle.
- Separate local, staging and production settings.

## 9. Testing

- Valid image returns schema-conforming response.
- Multiple detections are supported.
- Empty detections return zero counts.
- Counts match detections.
- Boxes are valid and bounded.
- Invalid/corrupt/oversized images fail safely.
- Model unavailable returns 503, not fabricated output.
- API tests do not depend on downloading model weights at test runtime; use dependency injection or controlled fixtures for unit tests, while keeping integration tests for actual inference.
