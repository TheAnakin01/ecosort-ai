# Backend

A FastAPI server. The app uploads a photo and gets back the detections as JSON.

## Run it

```
cd backend
pip install -r requirements.txt
uvicorn app.main:app --reload
```

`requirements.txt` installs Ultralytics and PyTorch, which is a large download. The three requirement files:

| File | Installs |
|---|---|
| `requirements-base.txt` | The API itself |
| `requirements.txt` | The API plus Ultralytics, for real inference |
| `requirements-dev.txt` | The API plus test tools, without Ultralytics |

Open http://127.0.0.1:8000/docs to try every endpoint in the browser.

The server starts without a trained model, but `/api/v1/detect` answers with error 503 until `ai-model/weights/best.pt` exists.

To test from a phone on the same Wi-Fi, start it with `--host 0.0.0.0` and use your laptop's IP address in the app.

## Endpoints

| Endpoint | Method | Purpose |
|---|---|---|
| `/health` | GET | Is the server up, and is a model loaded |
| `/api/v1/detect` | POST | Upload an image (form field `file`), get detections |
| `/api/v1/categories` | GET | The four categories, with ids and guidance links |
| `/api/v1/guidance/{category}` | GET | Bin and sorting tips |
| `/api/v1/model-info` | GET | Model name, version, classes and thresholds |

### A successful scan

```json
{
  "success": true,
  "image_width": 1280,
  "image_height": 960,
  "total_objects": 1,
  "counts": {"paper": 0, "plastic": 1, "metal": 0, "organic": 0},
  "detections": [
    {"id": 1, "category": "plastic", "confidence": 0.91, "low_confidence": false, "bbox": [120, 80, 250, 390]}
  ],
  "model_version": "baseline",
  "message": null
}
```

This shows the shape only. The numbers are not a real prediction.

- `bbox` is `[x1, y1, x2, y2]` in pixels of the upright image, measured from its top-left corner. `image_width` and `image_height` describe that same upright image, so the app scales boxes against those values.
- Detections come highest confidence first. `total_objects` equals the number of detections and the sum of `counts`.
- A photo with nothing in it is a success with an empty `detections` list, not an error.
- `low_confidence` and `message` are additions to the documented contract. `message` carries the "nothing detected" and "treat as estimates" notes.

### Errors

Every failure has the same shape, and the same `X-Request-ID` header as the body:

```json
{"success": false, "error": {"code": "UNSUPPORTED_IMAGE", "message": "Please upload a JPEG, PNG or WebP image."}, "request_id": "..."}
```

| Status | Code | When |
|---|---|---|
| 400 | `EMPTY_FILE`, `MALFORMED_REQUEST` | Empty upload, or no `file` field |
| 404 | `UNKNOWN_CATEGORY`, `NOT_FOUND` | Unknown category or address |
| 413 | `UPLOAD_TOO_LARGE` | File over `MAX_UPLOAD_MB` |
| 415 | `UNSUPPORTED_IMAGE` | A real image, but not JPEG, PNG or WebP |
| 422 | `INVALID_IMAGE`, `IMAGE_DIMENSIONS` | Not readable as an image, or too many pixels |
| 500 | `INFERENCE_FAILED`, `INTERNAL_ERROR` | The model or the server failed |
| 503 | `MODEL_UNAVAILABLE` | No model is loaded |
| 504 | `INFERENCE_TIMEOUT` | The model took longer than `INFERENCE_TIMEOUT_SECONDS` |

Messages are written for the person using the app. Stack traces and file paths go to the server log only.

## How it behaves

- **The model loads once, when the server starts.** If the weights are missing, unreadable, or trained for other classes, the server still starts, `/health` reports `"model_loaded": false`, and scans return 503. It never returns made-up detections.
- **Uploads are checked by content,** not by file name: size in bytes first, then the real format, then the pixel dimensions before decoding, so a small file that expands into a huge image is refused cheaply.
- **Nothing is stored.** Images are processed in memory and never written to disk or logged. The log has one line per request: method, path, status, duration and request id.
- **One inference at a time,** in a worker thread, so the server stays responsive.
- **Only listed websites may call the API from a browser** (`CORS_ORIGINS`). Phone apps are not affected.

Not implemented: rate limiting. Add it before the backend is opened to the public for more than a demo.

## Settings

Set as environment variables. To keep them in a file, copy `.env.example` to `.env` and start the server with `uvicorn app.main:app --env-file .env`. The file lists every setting with its default. The server refuses to start if a value is out of range.

The two confidence thresholds (0.35 and 0.5) are first guesses. Choose them on the validation split once a model is trained.

## Tests

```
pip install -r requirements-dev.txt
pytest
```

The tests use a fake detector, so they run without PyTorch or a trained model.

`tests/test_real_model.py` checks the API against a real YOLO model: that detections land on the labelled objects, that boxes follow a photo stored sideways, and that the model is loaded once. It is skipped unless you set two environment variables; the file's first lines explain how. It has been run against a model trained on synthetic coloured shapes, which proves the plumbing. It has not been run against a waste model, because none exists yet.

They also run automatically on GitHub for every push (`.github/workflows/tests.yml`), together with `ruff check backend ai-model` for lint.
