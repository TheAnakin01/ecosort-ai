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
| `/health` | GET | Is the server up |
| `/api/v1/detect` | POST | Upload an image (form field `file`), get detections |
| `/api/v1/categories` | GET | The four categories |
| `/api/v1/guidance/{category}` | GET | Bin and sorting tips |
| `/api/v1/model-info` | GET | Model version and thresholds |

Each detection has `category`, `confidence`, `low_confidence` and `bbox` as `[x1, y1, x2, y2]` in pixels of the upright image. `image_width` and `image_height` describe that same upright image, so the app should scale boxes against those values.

## Settings

Set as environment variables. Defaults are in `app/config.py`. To keep them in a file, copy `.env.example` to `.env` and start the server with `uvicorn app.main:app --env-file .env`.

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

`tests/test_real_model.py` checks the API against a real YOLO model: that detections land on the labelled objects, that boxes follow a photo stored sideways, and that the model is loaded once. It is skipped unless you set two environment variables; the file's first lines explain how. It has been run against a model trained on synthetic coloured shapes, which proves the plumbing. It has not been run against a waste model, because none exists yet.

They also run automatically on GitHub for every push (`.github/workflows/tests.yml`), together with `ruff check backend ai-model` for lint.
