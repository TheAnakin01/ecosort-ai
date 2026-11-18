# AI handoff — backend

Last updated: 2026-11-15. Read `CLAUDE.md`, `AGENTS.md` and `docs/decision-log.md` first.

## State

- Backend (FastAPI) is complete against the API spec and tested: `/health`, `/api/v1/detect`, `/categories`, `/guidance/{category}`, `/model-info`.
- Detector: trained YOLO11n (`ecosort-baseline-2`, val mAP@50 0.789, mAP@50-95 0.690; test split not yet scored).
- Two inference paths, chosen by `MODEL_PATH` extension: `.pt` (Ultralytics, `requirements.txt`) and `.onnx` (onnxruntime, `requirements-onnx.txt`, no PyTorch). Details and measurements: decision log, 2026-11-15.
- ONNX export: `python ai-model/scripts/export_onnx.py --weights ai-model/weights/best.pt` writes `best.onnx` and `best.onnx.json` (size, SHA-256, source checkpoint hash). Dynamic input shape; the backend letterboxes like Ultralytics, which is what makes detections match.
- Current ONNX artifact: 11,696,862 bytes, sha256 `0e38fc74...c687`, from `best.pt` sha256 `f2e7a74a...ef20`, Ultralytics 8.4.213.
- Backend config: `MODEL_PATH` now defaults to `ai-model/weights/best.onnx` (previously defaulted to the missing `best.pt`). Verified the backend loads the ONNX model via onnxruntime (`image_size=640`, classes `paper/plastic/metal/organic`) and `/health` reports `model_loaded=true`. `.pt` path remains available via `MODEL_PATH` override.
- Tests: 52 pass, 6 skip without model files (backend/). The parity test passes when given both files.
- CI lint fix: `ai-model/tests/test_download_datasets.py` and `test_training_checks.py` are Ruff-clean; focused dataset tests pass 26/26, full AI tests pass 109/109, and backend tests pass 52/52 with 6 model-dependent skips.

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
