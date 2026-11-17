# 10 Production Gap Analysis — EcoSort AI

**Audit date:** 2026-11-17  
**Repository:** `TheAnakin01/ecosort-ai`  
**Branch:** `feature/kaggle-kaggle-notebook-setup`

---

## Gap Summary

| Severity | Count |
|----------|-------|
| Critical | 8 |
| High | 10 |
| Medium | 8 |
| Low | 4 |

---

## Critical Gaps

### GAP-001: CI Lint Failing — Tests Cannot Run in CI

| Field | Value |
|-------|-------|
| Gap ID | GAP-001 |
| Description | `ruff check backend ai-model` fails in GitHub Actions, preventing pytest from executing |
| Current implementation | CI workflow runs lint first; lint failure blocks tests |
| Expected production behavior | Lint passes; tests run on every push and pull request |
| Risk | Cannot merge to main; code quality not verified automatically |
| Dependencies | Python environment; ruff configuration |
| Required work | Diagnose ruff violations (logs inaccessible via API — need log output), fix code, re-run CI |
| Acceptance criteria | `ruff check backend ai-model` exits 0; `pytest` runs in CI |

### GAP-002: No Model Trained on Verified Clean Data

| Field | Value |
|-------|-------|
| Gap ID | GAP-002 |
| Description | Only one training run exists (`ecosort-baseline-2`) with known data quality issues (2 mislabeled container classes, source overlap). No test-split score exists. |
| Current implementation | Validation metrics from `ecosort-baseline-2`: mAP@50-95 0.690; flagged "somewhat optimistic" |
| Expected production behavior | Model trained on clean dataset with pinned versions, confirmed licenses, and test-split evaluation |
| Risk | Deploying a model with unknown real-world performance; potential misclassifications in production |
| Dependencies | Kaggle GPU access; Roboflow credentials; pinned dataset versions; confirmed licenses |
| Required work | 1. Confirm Roboflow dataset versions and licenses. 2. Pin versions in `configs/datasets.yaml`. 3. Fix class mappings (disposable food container, foam food container → drop). 4. Run Kaggle training. 5. Score test split once. 6. Record metrics in `docs/training-log.md` |
| Acceptance criteria | Test-split mAP@50-95 recorded; overtraining verdict recorded; false-detection share recorded; all metrics from a real run |

### GAP-003: No ONNX Export Executed

| Field | Value |
|-------|-------|
| Gap ID | GAP-003 |
| Description | `export_onnx.py` exists but has never been run. Backend cannot serve ONNX model without the exported artifact. |
| Current implementation | Script exists; `best.onnx` not generated; `best.onnx.json` not generated |
| Expected production behavior | `best.onnx` and `best.onnx.json` generated from `best.pt`; provenance recorded |
| Risk | Backend cannot load model for inference |
| Dependencies | Trained model weights (`best.pt`); ultralytics installed |
| Required work | Run `python scripts/export_onnx.py --weights best.pt`; verify ONNX output; record checksum |
| Acceptance criteria | `best.onnx` and `best.onnx.json` exist; ONNX model loads and runs inference |

### GAP-004: Backend Detect Endpoint Not Implemented

| Field | Value |
|-------|-------|
| Gap ID | GAP-004 |
| Description | FastAPI skeleton exists but `POST /api/v1/detect` is not wired to any model. No image upload validation, no inference service, no error handling. |
| Current implementation | `main.py`, `detector.py`, `onnx_detector.py`, `schemas.py`, `errors.py` exist but are not integrated |
| Expected production behavior | `POST /api/v1/detect` accepts multipart image, validates it, runs inference, returns detections with boxes and counts |
| Risk | Mobile app cannot scan; no inference API exists |
| Dependencies | Trained ONNX model; FastAPI; ONNX Runtime or PyTorch |
| Required work | Implement model loading at startup; implement detect endpoint with upload validation; implement coordinate mapping; implement error handling; implement health endpoint |
| Acceptance criteria | Health endpoint returns 200; detect endpoint returns schema-conforming response; invalid images rejected safely; model loads on startup |

### GAP-005: Mobile App Connected to Placeholder API

| Field | Value |
|-------|-------|
| Gap ID | GAP-005 |
| Description | Mobile app `api.ts` uses `https://api.example.com` — no real backend endpoint exists. |
| Current implementation | API client implemented but points to non-existent URL |
| Expected production behavior | Mobile app connects to deployed backend API; scan flow works end-to-end |
| Risk | App cannot perform any scan; completely non-functional for core use case |
| Dependencies | Deployed backend API; correct API URL configuration |
| Required work | Deploy backend; update mobile API URL; test end-to-end on physical device |
| Acceptance criteria | End-to-end scan works on physical Android device; boxes aligned with detections; counts correct |

### GAP-006: Dataset Versions Unpinned and Licenses Unknown

| Field | Value |
|-------|-------|
| Gap ID | GAP-006 |
| Description | All four Roboflow dataset versions are `null` (unpinned). Licenses for 3 of 4 datasets are UNKNOWN. |
| Current implementation | `configs/datasets.yaml` has all versions as `null`; `docs/dataset-card.md` marks 3 licenses UNKNOWN |
| Expected production behavior | Dataset versions pinned and recorded; all licenses confirmed before submission use |
| Risk | Non-reproducible builds; potential license violations; different dataset versions produce different models |
| Dependencies | Roboflow API access; Roboflow license pages |
| Required work | 1. Check each dataset's license on Roboflow. 2. Record actual version numbers. 3. Enter versions in `configs/datasets.yaml`. 4. Update `docs/dataset-card.md` with confirmed licenses |
| Acceptance criteria | All 4 versions pinned in `configs/datasets.yaml`; all 4 licenses confirmed or explicitly marked UNKNOWN with justification |

### GAP-007: No Image Upload Validation (Backend)

| Field | Value |
|-------|-------|
| Gap ID | GAP-007 |
| Description | Backend has no image upload validation — no file size limits, no type validation, no decoded content check, no decompression bomb protection. |
| Current implementation | Not implemented |
| Expected production behavior | Backend validates uploaded images: format, size, dimensions, decoded content |
| Risk | Malicious or oversized images could crash the server or exhaust resources |
| Dependencies | FastAPI; Pillow/OpenCV for validation |
| Required work | Implement upload validation per `SECURITY_PRIVACY.md` section 2 and `BACKEND_API.md` section 5 |
| Acceptance criteria | Oversized images rejected (413); unsupported formats rejected (415); corrupt images rejected (422); decompression bombs blocked |

### GAP-008: No HTTPS / Production Deployment

| Field | Value |
|-------|-------|
| Gap ID | GAP-008 |
| Description | No production deployment exists. No HTTPS, no hosting, no environment separation. |
| Current implementation | Not deployed |
| Expected production behavior | Backend served over HTTPS with environment-based configuration; separate staging/production |
| Risk | No production system to serve users; data transmitted unencrypted if deployed naively |
| Dependencies | Hosting provider; domain; SSL certificate |
| Required work | Choose hosting provider; deploy backend; configure HTTPS; set up environment variables; configure CORS |
| Acceptance criteria | Backend accessible over HTTPS; health endpoint responds; model loads at startup |

---

## High Gaps

### GAP-009: No Test-Split Evaluation

| Field | Value |
|-------|-------|
| Gap ID | GAP-009 |
| Description | Test split (2,156 images) has never been scored. Only validation metrics exist. |
| Risk | Unknown real-world performance; validation scores may be optimistic due to data issues |
| Required work | Run `python scripts/evaluate.py --split test` once on final model |

### GAP-0010: Confidence Threshold Not Tuned

| Field | Value |
|-------|-------|
| Gap ID | GAP-0010 |
| Description | Default confidence threshold (0.35) and IoU threshold (0.7) not validated on held-out data. |
| Risk | Suboptimal false-positive/false-negative trade-off for the app |
| Required work | Run `check_hallucinations.py` at multiple confidence values; choose threshold on validation data only |

### GAP-0011: No Confusion Matrix Review

| Field | Value |
|-------|-------|
| Gap ID | GAP-0011 |
| Description | `confusion_matrix.png` generated by training but not reviewed. |
| Risk | Unknown class-confusion patterns; plastic/metal recall low (0.638/0.675) |
| Required work | Inspect `confusion_matrix.png`; analyze which classes are confused |

### GAP-0012: No Failure Photo Review

| Field | Value |
|-------|-------|
| Gap ID | GAP-0012 |
| Description | `worst_photos/` generated by `check_hallucinations.py` but not reviewed. |
| Risk | Unknown failure modes; boxes on nothing not analyzed |
| Required work | Inspect false-detection photos; determine if boxes on nothing are real label gaps or model faults |

### GAP-0013: No Physical Device Testing

| Field | Value |
|-------|-------|
| Gap ID | GAP-0013 |
| Description | Mobile app not tested on physical Android device. |
| Risk | Camera/gallery permissions, image capture, overlay alignment not verified on real hardware |
| Required work | Install APK on physical device; test full scan flow |

### GAP-0014: No Android Build

| Field | Value |
|-------|-------|
| Gap ID | GAP-0014 |
| Description | No APK/AAB built. EAS Build not configured. |
| Risk | Cannot distribute app to users |
| Required work | Configure EAS Build; build release artifact |

### GAP-0015: No Accessibility Audit

| Field | Value |
|-------|-------|
| Gap ID | GAP-0015 |
| Description | Accessibility documented but not audited against WCAG. |
| Risk | App may not be usable by people with disabilities |
| Required work | WCAG audit; fix contrast, touch targets, screen reader support |

### GAP-0016: No Dependency Vulnerability Scan

| Field | Value |
|-------|-------|
| Gap ID | GAP-0016 |
| Description | No `pip audit` or equivalent run. Dependencies use `~=` specifiers allowing minor updates. |
| Risk | Vulnerable dependencies could be introduced |
| Required work | Run `pip audit` or `safety check`; pin critical dependencies |

### GAP-0017: No Privacy Policy

| Field | Value |
|-------|-------|
| Gap ID | GAP-0017 |
| Description | No privacy policy document exists. |
| Risk | Legal requirement for apps collecting any user data; even scan-only apps need disclosure |
| Required work | Draft privacy policy; publish before release |

### GAP-0018: Git History Not Scanned for Secrets

| Field | Value |
|-------|-------|
| Gap ID | GAP-0018 |
| Description | Git history not scanned for accidentally committed secrets. |
| Risk | If a secret was committed at any point, it remains in history even if deleted |
| Required work | Scan git history; rotate any found secrets |

---

## Medium Gaps

### GAP-0019: No Structured Logging

| Field | Value |
|-------|-------|
| Gap ID | GAP-0019 |
| Description | Backend has no logging implemented. |
| Required work | Add structured logging (no image content) |

### GAP-0020: No Request IDs

| Field | Value |
|-------|-------|
| Gap ID | GAP-0020 |
| Description | No request ID middleware for diagnostics. |
| Required work | Add request ID to all responses |

### GAP-0021: No Request Timeouts

| Field | Value |
|-------|-------|
| Gap ID | GAP-0021 |
| Description | No request timeout configuration. |
| Required work | Configure server and client timeouts |

### GAP-0022: No Rate Limiting

| Field | Value |
|-------|-------|
| Gap ID | GAP-0022 |
| Description | No API rate limiting. |
| Required work | Add rate limits appropriate for deployment |

### GAP-0023: No Mobile E2E Tests

| Field | Value |
|-------|-------|
| Gap ID | GAP-0023 |
| Description | No end-to-end mobile tests. |
| Required work | Add E2E tests for scan flow |

### GAP-0024: No Performance Tests

| Field | Value |
|-------|-------|
| Gap ID | GAP-0024 |
| Description | No performance/load tests for inference latency, memory, throughput. |
| Required work | Measure on target hardware |

### GAP-0025: No Team Photos Added

| Field | Value |
|-------|-------|
| Gap ID | GAP-0025 |
| Description | No photos taken by the team added to dataset. Local conditions (Indian packaging, indoor lighting) may be under-represented. |
| Required work | Collect and annotate representative waste photos |

### GAP-0026: Git History Not Scanned for Secrets

*(Same as GAP-0018, listed at Medium here as well since it's also a security process gap)*

---

## Low Gaps

### GAP-0027: No Model Size Documentation

| Field | Value |
|-------|-------|
| Gap ID | GAP-0027 |
| Description | Model size (`best.pt`) not documented. |
| Required work | Record model file size after training |

### GAP-0028: No Mobile Memory Measurement

| Field | Value |
|-------|-------|
| Gap ID | GAP-0028 |
| Description | Mobile app memory usage not measured. |
| Required work | Measure on device |

### GAP-0029: No iOS Testing

| Field | Value |
|-------|-------|
| Gap ID | GAP-0029 |
| Description | iOS compatibility not tested (Android-first). |
| Required work | Test on iOS if iOS support needed |

### GAP-0030: No Content Review for Learn Screen

| Field | Value |
|-------|-------|
| Gap ID | GAP-0030 |
| Description | Educational content not reviewed by domain expert. |
| Required work | Domain expert review of recycling/disposal guidance |

---

## Acceptance Criteria Summary

Before production release, ALL Critical gaps (GAP-001 through GAP-008) must be resolved, and ALL High gaps (GAP-009 through GAP-0018) must be addressed or explicitly accepted with documented rationale.
