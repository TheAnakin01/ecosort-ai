# Master Execution Plan — EcoSort AI Production Readiness

**Repository:** `TheAnakin01/ecosort-ai`  
**Working branch:** `feature/production-readiness-roadmap` (to be created from `feature/phase-0-production-blockers`)  
**Base branch for PR:** `main`  
**Plan date:** 2026-11-17  
**Source of truth:** `docs/production-audit/` (13 reports), `docs/implementation/PHASE_0_PLAN.md`, `docs/implementation/PHASE_0_IMPLEMENTATION_REPORT.md`

---

## Current State (verified by source code inspection)

### What is already implemented

| Component | Status | Evidence |
|-----------|--------|----------|
| Backend API | **Fully implemented** | `backend/app/main.py`: `POST /api/v1/detect` (line 195), `GET /health` (line 190), `GET /api/v1/categories` (line 249), `GET /api/v1/guidance/{category}` (line 259), `GET /api/v1/model-info` (line 267). Model loading via `lifespan` (line 43-51). Image validation via `read_image()` (line 142-184). Request ID middleware (line 73-94). CORS (line 118-124). Secure errors via `errors.py`. |
| Backend tests | **Written** | `backend/tests/test_api.py`: 29 tests using fake detector (no PyTorch/weights needed). |
| AI/ML pipeline | **Complete scripts** | `ai-model/scripts/`: download_datasets, prepare_dataset, validate_dataset, train, overfit_check, check_hallucinations, export_onnx, evaluate, predict, dataset_paths. All reference scripts present. |
| AI/ML tests | **Written** | `ai-model/tests/`: 5 test files (download, prepare, validate, dataset_paths, training_checks). No PyTorch needed. |
| Mobile app | **Complete** | Expo/React Native: scan, results, home, learn, history screens; API client; detection overlay; state management; tests. |
| Kaggle notebook | **Complete** | `ai-model/notebooks/train_ecosort_kaggle.ipynb`: unattended training, fail-fast, branch verification, secrets via UserSecretsClient. |
| Documentation | **Extensive** | `docs/production-audit/` (13 reports), `docs/EcoSort-AI-Agent-Harness/` (PRD, architecture, etc.), `docs/kaggle-*`, `docs/dataset-card.md`, `docs/training-log.md`. |

### What is missing / blocked

| Gap | Title | Blocker |
|-----|-------|---------|
| GAP-001 | CI lint failing (`ruff check backend ai-model`) | Cannot verify without Python/ruff (not installed in this environment) |
| GAP-002 | No model trained on verified clean data | Requires Kaggle GPU T4 x2 + Roboflow API credentials |
| GAP-003 | No ONNX export executed | Requires trained `best.pt` weights |
| GAP-005 | Mobile connected to placeholder API | Defaults to `http://localhost:8000`; requires deployed backend URL via `EXPO_PUBLIC_API_URL` |
| GAP-006 | Dataset versions unpinned, licenses unknown | Requires Roboflow API access to check versions/licenses |
| GAP-008 | No HTTPS/production deployment | Infrastructure work |

**Already resolved (verified by code inspection):** GAP-004 (detect endpoint), GAP-007 (image upload validation).

### Environment constraint

Python is NOT installed in this environment (only 0-byte Windows Store stubs). Therefore:
- `ruff check backend ai-model` cannot be executed
- `pytest` cannot be executed in `backend/` or `ai-model/`
- `npm`/Expo mobile commands cannot be verified
- Kaggle training, ONNX export, backend deployment cannot be performed

All verification in this execution is based on **source code inspection only**.

---

## Execution Sequence

The roadmap phases (from the master prompt) map to the repository as follows:

| Master Prompt Phase | Repository Equivalent | Can Execute Here? | Primary Blocker |
|---------------------|----------------------|-------------------|-----------------|
| Phase 1 — Foundation and Environment | Already done (env files, lint config, CI) | Partial (no Python to verify) | Python not installed |
| Phase 2 — Dataset Preparation | Scripts complete; versions unpinned | Partial (config support ready) | Roboflow API access |
| Phase 3 — AI Model Training and Evaluation | Scripts complete; no trained weights | Blocked | Kaggle GPU + Roboflow credentials |
| Phase 4 — Backend API Productionization | Already implemented | Verified by inspection | Cannot run tests without Python |
| Phase 5 — Mobile Application Integration | Already implemented | Verified by inspection | Cannot run mobile build without Node/Expo |
| Phase 6 — Reliability and User Testing | Tests written; cannot run | Blocked | Python/Node not installed |
| Phase 7 — Optional Persistence | Explicitly deferred | Not implemented (approval-gated) | User approval needed |
| Phase 8 — Deployment and Release Preparation | Documentation exists; not deployed | Blocked | No deployment performed |

---

## Dependencies

| Dependency | Purpose | Available Here? |
|------------|---------|-----------------|
| Python 3.13 | Backend tests, AI/ML scripts, ruff lint | No |
| ruff~=0.16.9 | Python linting | No |
| Node.js 22 + npm | Mobile typecheck, lint, test | Not checked |
| Expo CLI | Mobile build | Not checked |
| Kaggle GPU T4 x2 | Model training | No |
| Roboflow API key | Dataset download | No |
| Hosting provider | Backend deployment | No |

---

## Blockers

1. **No Python installation** — Cannot run `ruff`, `pytest`, `train.py`, `evaluate.py`, `export_onnx.py`.
2. **No Kaggle/Roboflow credentials** — Cannot train model, cannot pin dataset versions, cannot confirm licenses.
3. **No hosting provider** — Cannot deploy backend, cannot provide production API URL for mobile app.
4. **No physical Android device** — Cannot perform end-to-end mobile testing.

---

## Acceptance Criteria (for this execution)

1. `docs/implementation/MASTER_EXECUTION_PLAN.md` exists and is accurate.
2. `docs/implementation/EXECUTION_TRACKER.md` exists and tracks every task.
3. All Phase 0 work is preserved (no regressions).
4. `feature/production-readiness-roadmap` branch is created from `feature/phase-0-production-blockers`.
5. All changes are committed on the feature branch (not pushed to main).
6. A DRAFT Pull Request is prepared (or exact commands provided if push unavailable).
7. No source code was unnecessarily changed.
8. YOLO11n architecture is preserved.
9. No fabricated test results or model metrics.
10. PR remains OPEN and UNMERGED.

---

## External Resources Required

| Resource | Purpose | Who Provides |
|----------|---------|--------------|
| Python 3.13 installation | Run ruff, pytest, training scripts | User / environment |
| Kaggle account + GPU | Train model on waste data | User |
| Roboflow API key | Download datasets, check versions/licenses | User |
| Hosting provider (Railway/Render/Fly.io) | Deploy backend over HTTPS | User |
| Physical Android device | End-to-end mobile testing | User |
| GitHub authentication | Push branch, create PR | User / environment |

---

## Estimated Effort

| Task | Effort | Can Do Here? |
|------|--------|--------------|
| Master execution plan | 1 hour | Yes |
| Execution tracker | 1 hour | Yes |
| Branch creation + commit | 30 min | Yes |
| CI lint fix verification | 2-4 hours | No (no Python) |
| Model training (Kaggle) | 8-12 hours | No (no credentials) |
| ONNX export | 1-2 hours | No (no weights) |
| Backend deployment | 4-8 hours | No (no hosting) |
| Mobile E2E testing | 1-2 days | No (no device) |
| Draft PR creation | 30 min | Partial (push may be blocked) |
