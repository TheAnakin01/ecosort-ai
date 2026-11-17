# AI handoff — whole project

Last updated: 2026-11-17. Read `CLAUDE.md`, `AGENTS.md` and `docs/decision-log.md` first.

## Project overview (read this first)

EcoSort AI detects several waste items in one photo and labels each as paper, plastic, metal or organic, with boxes, confidence and sorting tips. Parts: `ai-model/` (data + training), `backend/` (FastAPI), `mobile/` (Expo app, also published as a web page).

### Done
- Dataset pipeline: Roboflow datasets merged, class-mapped, de-duplicated, grouped split, leakage-validated (`ai-model/scripts/`, Colab and Kaggle notebooks). A fourth source (GARBAGE CLASSIFICATION 3) was added by Exit0Hero, with dataset version pinning and `--max-share` to cap organic at 30%.
- Run 1 (Colab, 2026-11-15): val mAP@50 0.789 on its own split; old mapping flaw. Run 2 (Kaggle, 2026-11-16, four sources, mapping fixed, 30 epochs): on 7,501 photos neither run trained on, run 2 beats run 1 (mAP@50-95 0.550 vs 0.386; recall 0.622 vs 0.466; every class better). Organic false detections rose (4.0% to 7.6%). Details: `docs/training-log.md`.
- **The model in the repo (`ai-model/weights/best.onnx`) is run 2** (11,125,532 bytes, sha256 `089400a8...9d8b`, from `best.zip`, Ultralytics 8.4.214), merged in PR #10. Backend ONNX and PyTorch detectors agree on 24 real photos (555/555 boxes).
- Backend complete against the API spec; runs `.pt` or `.onnx`. Mobile app: Home, Scan, Results (boxes), History (on-device), Learn; web build on GitHub Pages (last deployed 2026-11-14; later commits did not touch `mobile/`). CI passing on `main` as of 2026-11-16.

### Not done (in priority order)
1. **Host the backend over HTTPS** (`render.yaml` is ready: Render dashboard, New, Blueprint, pick this repo; then copy the service URL into repo variable `API_URL`) (laptop + tunnel for the demo, or a free host), then set repo variable `API_URL` and re-run "Deploy web app". Nothing is hosted as far as this file knows; the web link cannot scan until then. `backend/Dockerfile` has never been built.
2. Test run 2 on your own phone photos (my 3-stock-image test on run 1 labelled almost everything plastic; not re-run on run 2).
3. Possible run 3: 50-100 own annotated photos; check the licences of the remaining datasets.
4. Tune confidence thresholds on validation; score the test split once.
5. Build the Android APK (Expo EAS, needs the https backend) and test on a physical phone.
6. Rate limiting, LICENSE (Ultralytics is AGPL-3.0), municipal check of sorting tips.

### Backend details

## State

- Backend (FastAPI) is complete against the API spec and tested: `/health`, `/api/v1/detect`, `/categories`, `/guidance/{category}`, `/model-info`.
- Detector: trained YOLO11n, run 2 (see overview). Test split not yet scored.
- Two inference paths, chosen by `MODEL_PATH` extension: `.pt` (Ultralytics, `requirements.txt`) and `.onnx` (onnxruntime, `requirements-onnx.txt`, no PyTorch). Details and measurements: decision log, 2026-11-15.
- ONNX export: `python ai-model/scripts/export_onnx.py --weights ai-model/weights/best.pt` writes `best.onnx` and `best.onnx.json` (size, SHA-256, source checkpoint hash). Dynamic input shape; the backend letterboxes like Ultralytics, which is what makes detections match.
- Current ONNX artifact: see `ai-model/weights/best.onnx.json` (size, SHA-256, source checkpoint).
- Tests: 52 pass, 6 skip without model files (backend/). The parity test passes when given both files.

## Not done / open

1. **Hosting.** No host chosen. `backend/Dockerfile` is written but was never built (Docker Hub was blocked in the sandbox). Build and run it once before relying on it.
2. **Model file in the repo.** `ai-model/weights/best.onnx` (11.7 MB) and its record are committed; `.pt` files stay out of Git. Replace both when the model is retrained.
3. **Free-tier CPU.** Free hosts give 0.1 vCPU; expect far slower inference than the 75-290 ms measured here. Measure on the real host. Free instances sleep after about 15 min idle.
4. **Memory.** Peak 479 MB RSS for a 24 MP photo, 360 MB for 12 MP, so two concurrent large uploads could exceed 512 MB. On a 512 MB host consider `MAX_IMAGE_MEGAPIXELS=12` and a single worker, or have the app downscale before upload.
5. **Parity on real waste photos** has not been checked; the only images available were the Ultralytics samples.
6. Confidence thresholds (0.35 / 0.5) are untuned; no rate limiting; the model still carries the old mapping flaw (retrain planned).
7. After hosting: set the repo variable `API_URL`, re-run "Deploy web app", then build the Android APK.

## Environment notes

- Sandbox: PyPI works; download.pytorch.org and Docker Hub are blocked (403).
- Memory was measured with a cgroup v1 limit of 512 MB around the uvicorn process.
