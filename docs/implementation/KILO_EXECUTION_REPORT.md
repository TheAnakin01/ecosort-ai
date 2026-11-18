# KILO EXECUTION REPORT — EcoSort AI Production Readiness

**Repository:** `C:\Users\lenovo\OneDrive\Desktop\ecosort-ai`
**Branch:** `feature/production-readiness-roadmap` (up to date with `origin/feature/production-readiness-roadmap`)
**Working branch retained:** no switch to `main`, no push, no merge.
**Agent:** Kilo (lead ML / CV / backend implementation)

---

## 1. Original problem

The deployed YOLO11n detector (`ai-model/weights/best.onnx`, exported from run `ecosort-baseline-2`) fails on real mixed-waste photos:
- a banana/bags/food/plastic photo produced ONE `paper` detection, confidence ~0.4973, with a box covering almost the entire image (`[12, 81, 1076, 1022]`-like);
- raw top predictions were multiple highly overlapping `paper` boxes;
- at confidence 0.10 → 10 predictions, 0.20 → 8, 0.35 → 5, 0.50 → 0;
- a blank image correctly yields zero detections.

Lowering the confidence threshold does not fix poor localization — the failure is in what the model predicts, not the threshold.

Separately, the backend configuration defaulted `MODEL_PATH` to `best.pt`, but no `.pt` artifact exists locally (only `best.onnx`), so the backend could not load its model and `/health` reported `model_loaded=false`.

---

## 2. Root cause findings

**Reproduced with the actual ONNX artifact** using ONNX Runtime on `waste_detection_result.jpg` (1080×1080):

- Model loads cleanly. Input `images` (1,3,640,640), output `output0` (1,8,8400) = 4 box coords + 4 class scores. Classes: paper, plastic, metal, organic. Stride 32, imgsz 640. NMS disabled in graph.
- Raw top predictions are ALL `paper`, with boxes spanning ~600×530 px in the 640² letterboxed canvas (centre ~314,331) — i.e. covering most of the image. Max confidence ≈ 0.216 on this run; nothing clears the 0.35 threshold.
- After class-aware NMS (iou 0.7) at conf 0.35 → 0 detections.

Conclusion: the failure is a **model-quality / training-data problem**, not a threshold, preprocessing, export, or post-processing bug. The letterbox, coordinate conversion, class-aware NMS, and blank-image handling all behave correctly. The model was trained to emit huge low-confidence `paper` boxes, consistent with the known data-quality issues in the source dataset (see dataset card: two container classes were taught as `organic`, source overlap, 585 duplicate images with conflicting labels, classes not validated by a person).

The model cannot be judged improved merely because training ran; it needs a rebuilt, validated dataset and a retrained YOLO11n, then comparable val/test evaluation.

**Verified config bug (fixed):** `backend/app/config.py` defaulted `MODEL_PATH` to `ai-model/weights/best.pt`, which does not exist. Only `best.onnx` is committed. Changed the default (and `.env.example`) to `best.onnx`. The backend now loads the ONNX model via `OnnxDetector` (onnxruntime, CPUExecutionProvider), reports `model_loaded=true`, `image_size=640`.

---

## 3. Environment (correction to existing docs)

`docs/implementation/MASTER_EXECUTION_PLAN.md` and `PHASE_0_IMPLEMENTATION_REPORT.md` state "Python is not installed in this environment." That is stale. A virtual environment exists at `.venv`:
- Python 3.13.17
- onnxruntime 1.32.0, opencv-python-headless, pillow, numpy, pyyaml, fastapi, pytest 9.1.1, ruff 0.17.5
- **torch and ultralytics are NOT installed** (no local PyTorch training possible)
- CUDA is not available locally (no GPU)
- `download.pytorch.org` is blocked per `docs/AI-HANDOFF.md`; PyPI works

All baseline checks were executed successfully with `.venv\Scripts\python.exe`.

---

## 4. Files changed

| File | Change | Reason |
|------|--------|--------|
| `backend/app/config.py:82` | Default `MODEL_PATH` `best.pt` → `best.onnx` | Backend could not load its model; only `best.onnx` exists locally |
| `backend/.env.example:11` | `MODEL_PATH` example `best.pt` → `best.onnx` (uncommented) | Match the deployed ONNX artifact; avoid confusion |

No other source files changed. No model artifacts deleted or overwritten. `best.onnx` backed up in place (still present, sha256 `0e38fc74c6f5f6d1cc1fb67314191f4a4124fba4874b4310c24375177e7dc687`).

---

## 5. Dataset sources and versions (from docs/dataset-card.md, decision-log.md)

All four versions are currently **unpinned** (`version: null`) in `ai-model/configs/datasets.yaml`. None confirmed against live Roboflow (no credentials, Roboflow pages return 403 in this environment).

| Folder | Workspace | Project | Version | License |
|--------|-----------|---------|---------|---------|
| trash-detection | amongus-o6ilp | trash-detection-1fjjc-ipij8 | null (unpinned) | UNKNOWN |
| trashnet | polygence-project | trashnet-...-object-detection | null (unpinned) | CC BY 4.0 (confirmed 2026-11-14) |
| neat-now | fyp-gojku | neat-now | null (unpinned) | UNKNOWN |
| garbage-cls-3 | objectdetection-z2zn1 | garbage-classification-3-bjcgp | 5 (per decision log) | UNKNOWN for the copy |

The training run `ecosort-baseline-2` was built from the first **three** sources (trash-detection, trashnet, neat-now); GARBAGE CLASSIFICATION 3 was added for the *next* build and is **not** in `ecosort-baseline-2`'s dataset.

Known class-mapping fixes already in `class_overrides.yaml`:
- `disposable food container: drop` (was wrongly `organic`)
- `foam food container: drop` (was wrongly `organic`)
- `cardboard: paper`
- Suggested but undecided: `food can: metal`, `pop tab: metal`, `pizza box: paper`, `toilet tube: paper`, `single-use carrier bag: plastic`, `polypropylene bag: plastic`, `foam cup: plastic`
- Worth second look: `paper cup`, `drink carton`, `aluminium blister pack` (currently included, mixed materials)

Historical dataset stats (from `ecosort-baseline-2` build, NOT recomputed locally): 22,199 images, 49,385 boxes; train 15,518 / val 4,525 / test 2,156; paper 13,899 / plastic 14,865 / metal 12,340 / organic 8,281; 47,366 boxes dropped; 18,408 images skipped; 596 identical removed; 585 duplicates with differing labels (first copy kept); 7 repeated boxes; 1 invalid box.

---

## 6. Dataset statistics

Could not be recomputed locally: no `datasets/` or `downloads/` directory exists, and the four Roboflow sources cannot be downloaded without a Roboflow API key. The historical figures above are from the `ecosort-baseline-2` build and are recorded as such, not claimed as current.

---

## 7. Training configuration (existing run `ecosort-baseline-2`, the only recorded run)

| Item | Value |
|------|-------|
| Date | 2026-11-15 |
| Environment | Google Colab, Tesla T4 |
| Framework | Ultralytics 8.4.213, PyTorch 2.14.1+cu130 |
| Starting weights | `yolo11n.pt` |
| Epochs | 30 (early stopping patience 10) |
| Image size | 640 |
| Batch | 16 |
| Seed | 0 |
| Dataset | 3 sources (trash-detection, trashnet, neat-now), `--resplit`, `--max-share organic=0.3` |
| Split scored | validation |

Validation metrics (from `docs/training-log.md`):
- Precision 0.810, Recall 0.703, mAP@50 0.788, mAP@50-95 0.690
- Per-class AP@50: paper 0.860, plastic 0.694, metal 0.764, organic 0.836
- Weakest class: plastic (AP@50 0.694, recall 0.638)

Notes from the run: still improving when stopped (mAP@50 0.775→0.788 over epochs 26–29); no test-split score; no confusion-matrix review; thresholds untuned (0.35 / 0.50); two container classes mislabeled as organic in the training data.

No `best.pt`, `results.csv`, `args.yaml`, `events.out.tfevents*`, or run logs exist locally — only the exported `best.onnx` and its JSON provenance. Provenance beyond `docs/training-log.md`/`dataset-card.md` cannot be recovered locally.

---

## 8. Training results

Only the historical `ecosort-baseline-2` validation results above exist. **No new training was performed** (see blockers, section 13). No new metrics can be claimed.

---

## 9. Validation results

As section 8: historical validation only (`ecosort-baseline-2`). No held-out test score was ever recorded. The test split (2,156 images) remains untouched.

---

## 10. Final test results

None. The held-out test split has not been scored for any model. Cannot be produced without a trained checkpoint.

---

## 11. ONNX parity results

The existing `best.onnx` was verified to load and run (input/output shapes correct, classes correct, blank image → 0 detections, real image → low-conf huge `paper` boxes). **PyTorch/ONNX parity could NOT be measured** because no `best.pt` exists locally and torch/ultralytics are not installed. The parity test (`backend/tests/test_onnx_parity.py`) is skipped unless `ECOSORT_TEST_WEIGHTS` and `ECOSORT_TEST_ONNX` are both provided.

---

## 12. Backend integration results

**Fixed and verified.** `backend/app/config.py` now defaults `MODEL_PATH` to `ai-model/weights/best.onnx`.

Verification (executed):
- `config.settings.model_path` → `.../ai-model/weights/best.onnx`, `exists = True`
- `load_detector(settings)` → detector loaded = True, `image_size = 640`
- `/health` would report `model_loaded = true`

Regression checks (executed, `.venv`):
- `python -m pytest backend/tests -q` → **52 passed, 6 skipped** (6 skips are model-dependent tests needing `ECOSORT_TEST_WEIGHTS`)
- `python -m pytest ai-model/tests -q` → **109 passed**
- `ruff check backend/ ai-model/` → All checks passed
- `python -m pip check` → No broken requirements found

Baseline (pre-change) was 52 passed + 6 skipped backend, 109 passed ai-model — unchanged. No regressions.

The application now clearly reports model availability via `/health` and `/api/v1/model-info` (model_name, model_version, model_loaded, classes, thresholds, image_size).

---

## 13. Remaining limitations and blockers

| Phase | Work | Blocker | Required user action |
|-------|------|---------|----------------------|
| 2 / 4 | Dataset audit + rebuild (pin versions, confirm licenses, apply overrides, resplit, validate) | No Roboflow API key; `downloads/` and `datasets/` do not exist locally; `roboflow` package not installed | Provide Roboflow API key (Private API key) so the four pinned dataset versions can be downloaded and versions/licenses confirmed |
| 5 | YOLO11n retraining (free GPU: Colab T4 or Kaggle T4) | No torch/ultralytics locally; no GPU locally; Colab/Kaggle are external user accounts | Confirm Kaggle or Colab GPU access is available and the user will run `ai-model/notebooks/train_ecosort_kaggle.ipynb` (or Colab equivalent) with `ROBOFLOW_API_KEY` secret |
| 7 | ONNX export + PyTorch/ONNX parity | No trained `best.pt` locally | Follows successful retraining |
| 8 | ONNX-backed deployment | Resolved (config fix above) | — |
| 9 / 10 | Full regression + docs finalization | Depends on phases above | — |

Per the engineering rules: no metrics are fabricated, no synthetic results are presented as waste-detection performance, no validation score is reported as test performance, and YOLO11n is preserved.

---

## 14. Exact commands for reproducing the workflow

Baseline verification (already run, passes):
```
# from repo root, using the venv
.venv\Scripts\python.exe -m pytest backend/tests -q
.venv\Scripts\python.exe -m pytest ai-model/tests -q
.venv\Scripts\ruff.exe check backend/ ai-model/
.venv\Scripts\python.exe -m pip check
```

Dataset download + rebuild (blocked — needs Roboflow API key, `ROBOFLOW_API_KEY` env var):
```
# requires pip install roboflow pyyaml pillow (roboflow not installed locally)
set ROBOFLOW_API_KEY=<private key>
python scripts/download_datasets.py
python scripts/prepare_dataset.py downloads/trash-detection downloads/trashnet downloads/neat-now downloads/garbage-cls-3 --resplit --max-share organic=0.3
python scripts/validate_dataset.py datasets/ecosort
```

Training (blocked — needs Colab T4 or Kaggle T4 GPU; run by user in that environment):
```
python scripts/train.py --epochs 30 --name ecosort-baseline --project <run-dir>
python scripts/overfit_check.py <run>
python scripts/check_hallucinations.py --weights <run>/weights/best.pt --out <run>/hallucination_check_val
python scripts/evaluate.py --split test          # held-out test, once
python scripts/export_onnx.py --weights <run>/weights/best.pt
```

Backend (works now after config fix):
```
.venv\Scripts\python.exe -m pytest backend/tests -q
# then start server: uvicorn app.main:app --env-file backend/.env  (from backend/)
```

---

**Next step (awaiting user action):** provide a Roboflow Private API key so the dataset can be downloaded, version-pinned, audited, and rebuilt; and confirm whether Kaggle T4 or Colab T4 GPU training can be run by the user so the YOLO11n model can be retrained, evaluated, exported to ONNX, and integrated.
