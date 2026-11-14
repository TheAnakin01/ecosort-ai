# Backend

A FastAPI server. The app uploads a photo and gets back the detections as JSON.

## Run it

```
cd backend
pip install -r requirements.txt
uvicorn app.main:app --reload
```

Open http://127.0.0.1:8000/docs to try every endpoint in the browser.

The server starts without a trained model, but `/api/v1/detect` answers with error 503 until `ai-model/weights/best.pt` exists.

To test from a phone on the same Wi-Fi, start it with `--host 0.0.0.0` and use your laptop's IP address in the app.

## Endpoints

| Endpoint | Method | Purpose |
|---|---|---|
| `/health` | GET | Is the server up |
| `/api/v1/detect` | POST | Upload an image (form field `file`), get detections |
| `/api/v1/categories` | GET | The four categories |
| `/api/v1/guidance/{category}` | GET | Bin and sorting tips |
| `/api/v1/model-info` | GET | Model version and thresholds |

Each detection has `category`, `confidence`, `low_confidence` and `bbox` as `[x1, y1, x2, y2]` in pixels of the upright image. `image_width` and `image_height` describe that same upright image, so the app should scale boxes against those values.

## Settings

Set as environment variables. Defaults are in `app/config.py`.

| Variable | Default | Meaning |
|---|---|---|
| `MODEL_PATH` | `ai-model/weights/best.pt` | Trained weights file |
| `CONFIDENCE_THRESHOLD` | `0.35` | Detections below this are dropped |
| `LOW_CONFIDENCE_THRESHOLD` | `0.5` | Detections below this are flagged as uncertain |
| `MAX_UPLOAD_MB` | `10` | Largest accepted upload |

Tune the two thresholds on validation photos once the model is trained.

## Tests

```
pip install -r requirements-dev.txt
pytest
```

The tests use a fake detector, so they run without PyTorch or a trained model.
