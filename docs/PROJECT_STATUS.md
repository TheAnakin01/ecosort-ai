# Project status

Last updated: 2026-11-20. Decisions and their reasons are in [decision-log.md](decision-log.md); limitations in [KNOWN_LIMITATIONS.md](KNOWN_LIMITATIONS.md).

EcoSort AI detects several waste items in one photo and labels each as paper, plastic, metal or organic, with boxes, confidence and sorting tips. Parts: `ai-model/` (data and training), `backend/` (FastAPI), `mobile/` (Expo app, also published as a web page).

## Live

| What | Where |
|---|---|
| Backend API | `https://ecosort-ai-srujan26.onrender.com` (Render free tier; `/health` to wake it) |
| Web app | https://theanakin01.github.io/ecosort-ai/ |
| Android APK | Release `apk-latest` on GitHub, built by the "Build Android APK" workflow |

## Done

- **Dataset pipeline:** four Roboflow datasets merged, mapped to four classes, de-duplicated, split 70/20/10 by photo group, validated for leakage (`ai-model/scripts/`, Colab and Kaggle notebooks).
- **Model:** YOLO11n fine-tuned. Run 2 (Kaggle, 2026-11-16) beats run 1 on 7,501 shared validation photos: mAP@50-95 0.550 vs 0.386, recall 0.622 vs 0.466. The model in `ai-model/weights/best.onnx` is run 2. Details in [training-log.md](training-log.md).
- **Backend:** all endpoints in the API spec, upload validation, consistent errors, request IDs, rate limit (60 scans/minute per client), runs the model with ONNX Runtime in under 512 MB. Hosted on Render from `backend/Dockerfile` via `render.yaml`.
- **Mobile app:** Home, Scan (camera and gallery), Results with boxes and counts, History (on the device only), Learn. Works as a web page and as an Android APK.
- **End to end:** a scan from the APK on an Android phone against the hosted backend worked on 2026-11-18.
- **Automation:** GitHub Actions run lint and tests, deploy the web app, and build the APK.

## Open

1. **Detection quality.** Real photos show many missed items (recall 0.62 on validation; glass has no class). Next steps: tune the confidence threshold with `ai-model/scripts/tune_thresholds.py` on the validation split, score the test split once with `evaluate.py --split test`, then a third training run with the team's own annotated phone photos.
2. **Web app scan** on the hosted backend not yet confirmed by hand.
3. **Licences:** confirm three dataset licences; choose a LICENSE for the repo (Ultralytics is AGPL-3.0).
4. **Free hosting limits:** the server sleeps after about 15 minutes idle (first scan up to a minute) and has little CPU.

## Technical notes

- Two inference paths, chosen by the `MODEL_PATH` extension: `.onnx` (default, ONNX Runtime, no PyTorch) and `.pt` (Ultralytics). The ONNX path matches PyTorch's detections because it letterboxes the image exactly like Ultralytics.
- Re-export after retraining: `python ai-model/scripts/export_onnx.py --weights path/to/best.pt`, then replace `ai-model/weights/best.onnx` and `best.onnx.json`.
- Memory on a 512 MB limit: about 176 MB idle, 360 MB peak for a 12 MP photo; uploads are capped at 12 MP on Render.
- The rate limit uses the last `X-Forwarded-For` entry on Render. If many users get "Too many scans" together, set `RATE_LIMIT_PER_MINUTE=0` in the Render dashboard.
- The app wakes a sleeping server and retries a scan once when there is no answer.
