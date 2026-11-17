# Phase 0 Plan — Production Blockers

**Repository:** `TheAnakin01/ecosort-ai`  
**Branch:** `feature/kaggle-kaggle-notebook-setup` (source)  
**Working branch:** `feature/phase-0-production-blockers`  
**Plan date:** 2026-11-17  
**Source of truth:** `docs/production-audit/` (01, 03, 07, 08, 10, 11, 12)

---

## Critical Gaps — Complete Inventory (8 total)

The audit identified **8 Critical gaps** (GAP-001 through GAP-008). The roadmap names 5 Phase 0 tasks (P0-01 to P0-05), but this plan covers all 8 Critical findings, explicitly distinguishing which can be addressed in this environment and which require external resources.

| Gap ID | Title | Addressable Here? | Root Cause |
|--------|-------|-------------------|------------|
| GAP-001 | CI Lint Failing — Tests Cannot Run in CI | Partial | `ruff check backend ai-model` fails; root cause unknown (CI logs behind auth) |
| GAP-002 | No Model Trained on Verified Clean Data | No | Requires Kaggle GPU + Roboflow API credentials |
| GAP-003 | No ONNX Export Executed | No | Requires trained `best.pt` weights |
| GAP-004 | Backend Detect Endpoint Not Implemented | Yes (already done) | Code inspection shows `POST /api/v1/detect` IS implemented in `main.py` |
| GAP-005 | Mobile App Connected to Placeholder API | No | Requires deployed backend URL |
| GAP-006 | Dataset Versions Unpinned and Licenses Unknown | No | Requires Roboflow API access to check versions/licenses |
| GAP-007 | No Image Upload Validation (Backend) | Yes (already done) | Code inspection shows validation IS implemented in `main.py` `read_image()` |
| GAP-008 | No HTTPS / Production Deployment | No | Infrastructure/deployment work |

**Note:** GAP-004 and GAP-007 appear already resolved in the current codebase. `main.py` implements the detect endpoint (line 195) and comprehensive image upload validation (lines 142-184: empty file, size limit, decompression bomb, invalid image, format check, dimension check, EXIF transpose, RGB conversion).

---

## Phase 0 Tasks

### P0-01 — Fix CI Lint Failures (GAP-001)

**Root cause:** `ruff check backend ai-model` exits non-zero in GitHub Actions, preventing pytest from running. Specific ruff violations could not be read (CI logs behind authentication — 403 on API).

**Files affected:**
- `backend/app/main.py`
- `backend/app/config.py`
- `backend/app/detector.py`
- `backend/app/onnx_detector.py`
- `backend/app/schemas.py`
- `backend/app/errors.py`
- `backend/tests/test_api.py`
- `backend/tests/test_onnx_detector.py`
- `backend/tests/test_onnx_parity.py`
- `backend/tests/test_real_model.py`
- `ai-model/scripts/*.py`
- `ai-model/tests/*.py`

**Implementation approach:**
1. Inspect all Python files for ruff-selectable violations (rules E, F, I, B per `ruff.toml`):
   - F401: unused imports
   - F841: unused variables
   - E501: line too long (>120 chars)
   - I: import sorting (isort)
   - B: bugbear patterns
2. Fix violations without suppressing legitimate warnings.
3. Do not change import ordering rules — use isort-compatible ordering.

**Dependencies:** Python 3.13, ruff~=0.16.9

**Tests required:** After fixing, `ruff check backend ai-model` must exit 0. `pytest` must run in both `backend/` and `ai-model/`.

**Acceptance criteria:**
- `ruff check backend ai-model` exits 0
- CI lint step passes
- `pytest` runs (not skipped due to lint failure)

**Risks:** Cannot verify ruff fixes without Python/ruff available in this environment. Fixes are based on code inspection only.

---

### P0-02 — Train Model on Verified Clean Data (GAP-002)

**Root cause:** Only one training run exists (`ecosort-baseline-2`) with known data quality issues (2 mislabeled container classes, source overlap). No test-split score exists.

**Addressable here? No.** Requires:
- Kaggle GPU T4 x2 access
- Roboflow API credentials
- Internet access on Kaggle
- ~8-9 hours of training time

**Required work (documented, not implemented here):**
1. Check each dataset's license on Roboflow
2. Record actual version numbers
3. Pin versions in `ai-model/configs/datasets.yaml`
4. Fix class mappings (`disposable food container` → drop, `foam food container` → drop)
5. Run Kaggle training via `ai-model/notebooks/train_ecosort_kaggle.ipynb`
6. Score test split via `python scripts/evaluate.py --split test`
7. Record metrics in `docs/training-log.md`

**Acceptance criteria:** Test-split mAP@50-95 recorded; overtraining verdict recorded; false-detection share recorded; all metrics from a real run.

---

### P0-03 — Export ONNX Model (GAP-003)

**Root cause:** `export_onnx.py` exists but has never been run. Requires trained `best.pt` weights.

**Addressable here? No.** Requires trained model weights from P0-02.

**Required work (documented, not implemented here):**
1. Run `python scripts/export_onnx.py --weights best.pt`
2. Verify ONNX output loads and runs inference
3. Record checksum

**Acceptance criteria:** `best.onnx` and `best.onnx.json` exist; ONNX model loads and runs inference.

---

### P0-04 — Backend Detect Endpoint (GAP-004)

**Status:** Already implemented. Code inspection confirms:
- `POST /api/v1/detect` at `backend/app/main.py:195`
- Image upload validation at `backend/app/main.py:142-184` (empty file, size limit, decompression bomb, invalid image, format check, dimension check)
- Model loading at startup via `lifespan` (line 43-51)
- Error handling via `errors.py` (safe messages, no stack traces)
- Request IDs via middleware (line 73-94)
- CORS configured (line 118-124)
- Health endpoint at line 190-192

**No code changes needed.** This gap appears resolved in the current codebase.

**Verification needed:** Run `pytest` in `backend/` to confirm all API tests pass (requires Python).

---

### P0-05 — Mobile App Connected to Real API (GAP-005)

**Root cause:** Mobile app `api.ts` uses `https://api.example.com` placeholder.

**Addressable here? No.** Requires deployed backend URL.

**Required work (documented, not implemented here):**
1. Deploy backend to hosting provider
2. Update mobile API URL
3. Test end-to-end on physical Android device

**Acceptance criteria:** End-to-end scan works on physical Android device; boxes aligned; counts correct.

---

### GAP-006 — Dataset Versions Unpinned and Licenses Unknown

**Root cause:** All four Roboflow dataset versions are `null` in `configs/datasets.yaml`. Licenses for 3 of 4 datasets are UNKNOWN.

**Addressable here? No.** Requires Roboflow API access.

**Required work (documented, not implemented here):**
1. Check each dataset's license on Roboflow
2. Record actual version numbers
3. Pin versions in `configs/datasets.yaml`
4. Update `docs/dataset-card.md` with confirmed licenses

**Acceptance criteria:** All 4 versions pinned; all licenses confirmed or documented UNKNOWN.

---

### GAP-007 — Image Upload Validation (GAP-007)

**Status:** Already implemented. Code inspection confirms `read_image()` in `backend/app/main.py:142-184` implements:
- Empty file check (line 145-147)
- File size limit (line 147-149) — reads `max_upload_bytes + 1` to detect oversized
- Decompression bomb protection (line 151-156) — `Image.DecompressionBombWarning` treated as error
- Invalid image handling (line 157-161) — broad exception catch for unreadable files
- Format validation (line 164-165) — checks `image.format` against `ALLOWED_FORMATS`
- Dimension validation (line 170-171) — checks `max_image_side` and `max_image_pixels`
- EXIF transpose (line 180-181) — corrects phone photo rotation
- RGB conversion (line 182) — converts grey/transparent images

**No code changes needed.** This gap appears resolved in the current codebase.

---

### GAP-008 — No HTTPS / Production Deployment (GAP-008)

**Root cause:** No production deployment exists.

**Addressable here? No.** Infrastructure work requiring hosting provider, domain, SSL certificate.

**Required work (documented, not implemented here):**
1. Choose hosting provider
2. Deploy backend
3. Configure HTTPS
4. Set up environment variables
5. Configure CORS for production origins

**Acceptance criteria:** Backend accessible over HTTPS; health endpoint responds; model loads at startup.

---

## Immediate Action Items (Can Be Done in This Environment)

| Item | Description | File(s) |
|------|-------------|---------|
| Create PHASE_0_PLAN.md | This document | `docs/implementation/PHASE_0_PLAN.md` |
| Create feature branch | `feature/phase-0-production-blockers` | Git |
| Inspect code for ruff violations | Manual code review | `backend/app/*.py`, `backend/tests/*.py`, `ai-model/scripts/*.py`, `ai-model/tests/*.py` |
| Fix obvious code issues | Based on inspection | As identified |
| Add security tests | Image upload validation tests | `backend/tests/test_api.py` (may already exist) |
| Create PHASE_0_IMPLEMENTATION_REPORT.md | Document all changes | `docs/implementation/PHASE_0_IMPLEMENTATION_REPORT.md` |
| Commit changes | On feature branch | Git |

## What Cannot Be Done Without External Resources

| Item | Reason |
|------|--------|
| Run `ruff check backend ai-model` | Python not available in this environment |
| Run `pytest` | Python not available |
| Access CI logs | GitHub API returns 403 (authentication required) |
| Train model on Kaggle | Requires Kaggle account, GPU, Roboflow credentials |
| Export ONNX | Requires trained `best.pt` weights |
| Deploy backend | Requires hosting provider, domain, SSL |
| Update mobile API URL | Requires deployed backend URL |
| Pin dataset versions | Requires Roboflow API access to check versions |
| Check dataset licenses | Requires Roboflow API access |
