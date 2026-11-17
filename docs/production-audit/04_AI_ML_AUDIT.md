# 04 AI/ML Audit — EcoSort AI

**Audit date:** 2026-11-17  
**Repository:** `TheAnakin01/ecosort-ai`  
**Branch:** `feature/kaggle-kaggle-notebook-setup`

---

## Existing Model Architecture

| Attribute | Value | Source |
|-----------|-------|--------|
| Model family | Ultralytics YOLO nano object detector | `train.py` line 91: `--model default="yolo11n.pt"` |
| Model variant | YOLO11n | `train.py`, CLAUDE.md |
| Framework | PyTorch + Ultralytics | `ai-model/requirements.txt` |
| Task | Multi-object object detection (bounding boxes) | `docs/EcoSort-AI-Agent-Harness/AI_MODEL.md` |
| Classes | 4: paper (0), plastic (1), metal (2), organic (3) | `configs/data.yaml` |
| Input size | 640 px | `train.py` default `--imgsz 640` |
| Batch size | 16 | `train.py` default `--batch 16` |
| Epochs (max) | 50 (default), 30 (Kaggle notebook override) | `train.py` line 93; notebook cell 5 |
| Early stopping patience | 10 | `train.py` line 99 |
| Random seed | 0 (default, recorded) | `train.py` line 102 |
| Transfer learning | From pretrained `yolo11n.pt` | `train.py` line 118 |
| ONNX export | Opset 17, dynamic shape, FP32, no NMS in graph | `export_onnx.py` |

**Constraint confirmed:** YOLO nano is the approved detector. CLAUDE.md explicitly prohibits replacing with MobileNet, SSD, Faster R-CNN, or any other model family. The audit preserves this constraint.

---

## Dataset Audit

### Sources (4 Roboflow datasets)

| Folder | Workspace | Project | Version | License |
|--------|-----------|---------|---------|---------|
| trash-detection | amongus-o6ilp | trash-detection-1fjjc-ipij8 | Not pinned (null) | UNKNOWN — not checked |
| trashnet | polygence-project | trashnet-a-set-of-annotated-images-of-trash-that-can-be-used-for-object-detection | Not pinned (null) | CC BY 4.0 (confirmed 2026-11-14) |
| neat-now | fyp-gojku | neat-now | Not pinned (null) | UNKNOWN — not checked |
| garbage-cls-3 | objectdetection-z2zn1 | garbage-classification-3-bjcgp | 5 (documented, not confirmed live) | UNKNOWN for this copy; original is CC BY 4.0 |

**Critical issue:** All four dataset versions are unpinned (`version: null` in `configs/datasets.yaml`). Each training run downloads the newest Roboflow version — results are **not bit-for-bit reproducible**. Version pinning is supported by the downloader but not yet configured.

**Critical issue:** Licenses for 3 of 4 datasets are UNKNOWN and must be checked on Roboflow before any submission use. A copied dataset does not automatically inherit the original's license.

### Dataset Size and Class Distribution

Documented in `docs/dataset-card.md` from the first build (2026-11-15):

| Split | Images | paper | plastic | metal | organic |
|-------|--------|-------|---------|---------|---------|
| train | 15,518 | 9,793 | 10,669 | 8,646 | 5,574 |
| val | 4,525 | 2,764 | 3,051 | 2,461 | 1,962 |
| test | 2,156 | 1,342 | 1,145 | 1,233 | 745 |
| **all** | **22,199** | **13,899** | **14,865** | **12,340** | **8,281** |

- Total labelled boxes: 49,385
- Share of boxes: paper 28%, plastic 30%, metal 25%, organic 17%
- Organic is the smallest class but not rare (17%)

### Class Mapping

Source classes mapped to 4 EcoSort classes by keyword matching, with manual overrides in `configs/class_overrides.yaml`:

| Override | Target | Reason |
|----------|--------|--------|
| cardboard | paper | TrashNet has separate cardboard/paper; both are paper |
| disposable food container | drop | Container, not food waste |
| foam food container | drop | Container, not food waste |

**Known data quality issue (documented):** The first real training run (`ecosort-baseline-2`) had two mislabeled classes — "Disposable food container" and "Foam food container" were taught as organic because the keyword "food" matched them. Fixed for the next run (both now excluded).

### Dataset Preparation Pipeline

| Step | Script | Status |
|------|--------|--------|
| Download from Roboflow | `download_datasets.py` | Complete; version pinning supported; manifest written |
| Merge sources | `prepare_dataset.py` | Complete; class mapping, dedupe, invalid box removal |
| Resplit 70/20/10 | `prepare_dataset.py --resplit` | Complete; copy-aware splitting |
| Organic cap (30%) | `prepare_dataset.py --max-share organic=0.3` | Complete |
| Validate | `validate_dataset.py` | Complete; fails fast on errors |
| Provenance recording | `prepare_dataset.py` + manifest | Complete; `source_versions` in `dataset_report.json` |

### Data Quality Safeguards (Implemented)

- Identical image files removed (596 removed in first build)
- Same-named photos across sources preserved with source prefix (`trashnet__a.jpg`, `neat__a.jpg`)
- Invalid boxes removed (boxes outside image, empty boxes, non-numeric values, odd polygon counts)
- Duplicate boxes removed (same box listed twice)
- Split leakage prevented (copies of one original photo kept in same split)
- Photos with all items dropped are excluded entirely
- Augmentation-level overlap cannot be detected (documented limitation)

---

## Training Pipeline

### Configuration (preserved, not changed)

| Parameter | Value | Source |
|-----------|-------|--------|
| Model | `yolo11n.pt` | `train.py` default |
| Data | `configs/data.yaml` | `train.py` default |
| Epochs | 50 (default), 30 (notebook) | `train.py` / notebook |
| Image size | 640 | `train.py` default |
| Batch | 16 | `train.py` default |
| Patience | 10 | `train.py` default |
| Seed | 0 | `train.py` default |
| Validation gate | Required (no `--skip-validation-check`) | `train.py` `require_validated()` |
| Best checkpoint | Saved as `best.pt` | `train.py` line 132 |
| Test split | Never used during training | `train.py` line 11-12 comment |

### Training Runs Executed

**Only one real training run on waste data has been completed** (Google Colab, Tesla T4):

| Metric | Value | Source |
|--------|-------|--------|
| Run name | `ecosort-baseline-2` | `docs/training-log.md` |
| Dataset built | 2026-11-15T07:30:44+00:00 | `docs/training-log.md` |
| Epochs | 30 | `docs/training-log.md` |
| Image size | 640 | `docs/training-log.md` |
| Seed | 0 | `docs/training-log.md` |
| Precision (val) | 0.810 | `docs/training-log.md` |
| Recall (val) | 0.703 | `docs/training-log.md` |
| mAP@50 (val) | 0.788 | `docs/training-log.md` |
| mAP@50-95 (val) | 0.690 | `docs/training-log.md` |
| Device | Tesla T4 (Colab) | `docs/training-log.md` |
| Batch | 16 | `docs/training-log.md` |
| Ultralytics | 8.4.213 | `docs/training-log.md` |
| PyTorch | 2.14.1+cu130 | `docs/training-log.md` |
| Duration | ~2 hours 45 minutes | `docs/training-log.md` |

**Caveats documented in training log:**
- Two container classes were labelled organic by mistake (fixed for next run)
- Source overlap cannot be fully detected — scores may be "somewhat optimistic"
- Still improving when it stopped (mAP@50 rose over epochs 26-29)
- No test-split score
- No confusion matrix review
- No failure photo review
- Confidence thresholds still at untuned defaults

### Per-Class Results (validation split, `ecosort-baseline-2`)

| Class | Precision | Recall | AP@50 | AP@50-95 |
|-------|-----------|--------|-------|----------|
| paper | 0.845 | 0.768 | 0.860 | 0.797 |
| plastic | 0.730 | 0.638 | 0.694 | 0.595 |
| metal | 0.800 | 0.675 | 0.764 | 0.644 |
| organic | 0.866 | 0.729 | 0.836 | 0.725 |

**Weakest class:** plastic (recall 0.638 — misses more than a third of labelled plastic items). Metal recall also low (0.675).

---

## Overtraining Detection

`overfit_check.py` analyzes `results.csv` and produces a verdict:

| Verdict | Condition |
|---------|-----------|
| overtraining | Val loss rose ≥3% above lowest while train loss kept falling |
| still improving | Best epoch is one of last 2 AND recent gain > 0.003 |
| levelled off | Scores stopped improving and val loss did not rise |

For `ecosort-baseline-2`: mAP@50 went 0.775, 0.787, 0.784, 0.788 over epochs 26-29 — "still improving" when stopped.

---

## False-Detection Analysis

`check_hallucinations.py` runs the model at app thresholds (conf 0.35, IoU 0.7) and categorizes each detection:

| Category | Meaning |
|----------|---------|
| correct | On a labelled item, right class |
| wrong class | On a labelled item, wrong class |
| duplicate | Second box on an item already claimed |
| poor box | Touches a labelled item but doesn't cover well |
| on nothing | No labelled item there (hallucination) |

Outputs: `report.json` + `worst_photos/` (annotated images with red=on nothing, yellow=other mistakes, green=correct, white=labels).

**Not yet executed on a real trained model.**

---

## Inference Pipeline (Backend)

**Not implemented.** The backend skeleton (`backend/app/`) has:

- `detector.py` — detector service interface (not connected to model)
- `onnx_detector.py` — ONNX-based detector (not integrated)
- `main.py` — FastAPI app skeleton (no detect endpoint wired)

The mobile app points to `https://api.example.com` (placeholder). No real inference pipeline exists.

### Backend Configuration (planned, not implemented)

| Setting | Value | Source |
|---------|-------|--------|
| Confidence threshold | 0.35 (app default) | `check_hallucinations.py` default; `predict.py` default |
| IoU threshold | 0.7 | `check_hallucinations.py` default |
| Image size | 640 | `train.py` default |
| Max detections | Not specified | `AI_MODEL.md` section 6 |
| Device | cpu/cuda | `AI_MODEL.md` section 6 |

---

## Verified Performance Metrics

**Only validation-split metrics from one run exist.** No test-split metrics. No CPU/GPU latency on target hardware. No mobile inference measurements.

| Metric | Value | Caveat |
|--------|-------|--------|
| mAP@50-95 (val) | 0.690 | From `ecosort-baseline-2`; data quality issues documented |
| mAP@50 (val) | 0.788 | From `ecosort-baseline-2` |
| Precision (val) | 0.810 | From `ecosort-baseline-2` |
| Recall (val) | 0.703 | From `ecosort-baseline-2` |
| Inference latency (CPU) | ~70 ms per 1280x960 image | From training log; not measured on target |
| Memory (CPU) | ~760 MB with model loaded | From training log; not measured on device |

**No test-split score exists.** The test split (2,156 images) has never been scored.

---

## Model Deployment Requirements

| Requirement | Status |
|-------------|--------|
| Model weights file (`best.pt`) | Not committed to Git; must be exported from training run |
| ONNX export (`best.onnx`) | `export_onnx.py` exists; not executed |
| ONNX provenance JSON (`best.onnx.json`) | Script generates it; not executed |
| Backend model loading | Not implemented |
| Model version tracking | `run_info.json` records versions; no model registry |
| Artifact storage | Not established (weights not in Git) |

---

## Known Limitations (Documented)

1. **Overlapping source photos.** Identical and look-alike copies exist across sources. Augmentation-level overlap (flipped in one source, rotated in another) cannot be detected. Validation/test scores may be somewhat optimistic.
2. **Wrong labels in first training data.** Two container classes mislabeled as organic. Fixed for next run but not yet re-trained.
3. **Mixed materials.** Paper cups, drink cartons, blister packs counted as one material.
4. **Local conditions.** None of the photos taken by the team. Indian packaging, mixed household waste, indoor lighting may be under-represented.
5. **Excluded items stay in photos.** Glass and general litter appear with no box. Model taught to ignore them — intended, but app says nothing about them.
6. **No own photos added.** Team has not contributed any annotated photos.
7. **No test-split evaluation.** Final honest score not yet obtained.
8. **Confidence thresholds untuned.** Defaults (0.35 conf, 0.7 IoU) not validated on held-out data.

---

## Required ML Improvements (Before Production)

| Priority | Issue | Required Work |
|----------|-------|---------------|
| Critical | Train model on clean dataset with fixed class mappings | Re-run Kaggle training with pinned versions and corrected overrides |
| Critical | Score test split once on final model | `python scripts/evaluate.py --split test` |
| Critical | Export ONNX for backend serving | `python scripts/export_onnx.py --weights best.pt` |
| High | Tune confidence threshold on validation data | Run `check_hallucinations.py` at multiple conf values |
| High | Review confusion matrix and failure photos | Inspect `confusion_matrix.png` and `worst_photos/` |
| High | Confirm dataset licenses | Check all 4 datasets on Roboflow |
| High | Pin dataset versions | Enter confirmed versions in `configs/datasets.yaml` |
| Medium | Add team's own photos for local conditions | Collect and annotate representative waste photos |
| Medium | Measure inference latency on target hardware | CPU and mobile measurements |
| Medium | Evaluate plastic/metal recall improvement | Investigate low recall for plastic (0.638) and metal (0.675) |
