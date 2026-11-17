# 12 Production Checklist — EcoSort AI

**Audit date:** 2026-11-17  
**Repository:** `TheAnakin01/ecosort-ai`

**Status key:** [x] Completed | [ ] Not started | [~] Blocked / Needs verification

---

## Phase 0 — Critical Blockers

| ID | Checklist Item | Status | Evidence Needed |
|----|---------------|--------|-----------------|
| P0-01 | CI lint passes (`ruff check backend ai-model`) | [ ] | CI log showing lint pass |
| P0-02 | CI tests run (`pytest` in backend and ai-model) | [ ] | CI log showing test results |
| P0-03 | Model trained on Kaggle with pinned dataset versions | [ ] | Kaggle run output; `docs/training-log.md` updated |
| P0-04 | Test-split evaluation completed once | [ ] | `scripts/evaluate.py --split test` output |
| P0-05 | ONNX model exported with provenance JSON | [ ] | `best.onnx` and `best.onnx.json` files |
| P0-06 | Backend `POST /api/v1/detect` implemented | [ ] | Backend code; API test results |
| P0-07 | Backend health endpoint (`GET /health`) implemented | [ ] | Backend code; curl test |
| P0-08 | Image upload validation implemented | [ ] | Test results for invalid/oversized/corrupt images |
| P0-09 | Mobile app connected to real backend | [ ] | Mobile code; end-to-end test |
| P0-10 | End-to-end scan works on physical Android device | [ ] | Device test results |

---

## Phase 1 — Core Application

| ID | Checklist Item | Status | Evidence Needed |
|----|---------------|--------|-----------------|
| P1-01 | Confidence threshold tuned on validation data | [ ] | `check_hallucinations.py` output at multiple thresholds |
| P1-02 | Confusion matrix reviewed | [ ] | Review notes in `docs/training-log.md` |
| P1-03 | False-detection photos reviewed | [ ] | Review notes in `docs/training-log.md` |
| P1-04 | Backend deployed over HTTPS | [ ] | HTTPS URL; certificate valid |
| P1-05 | Android APK/AAB built | [ ] | Build artifact |
| P1-06 | Accessibility audit completed | [ ] | WCAG audit results |
| P1-07 | Dependency vulnerability scan completed | [ ] | `pip audit` or equivalent output |

---

## Phase 2 — AI/ML Productionization

| ID | Checklist Item | Status | Evidence Needed |
|----|---------------|--------|-----------------|
| P2-01 | All 4 dataset versions pinned in `configs/datasets.yaml` | [ ] | Config file with version numbers |
| P2-02 | All 4 dataset licenses confirmed or documented UNKNOWN | [ ] | `docs/dataset-card.md` updated |
| P2-03 | Team photos collected and annotated (optional) | [ ] | New dataset source added |
| P2-04 | Inference latency measured on target hardware | [ ] | Benchmark results |
| P2-05 | Plastic/metal recall investigation completed | [ ] | Findings documented |
| P2-06 | Model artifact store established | [ ] | Artifact storage with version tags |
| P2-07 | Model size documented | [ ] | File size in `docs/training-log.md` |

---

## Phase 3 — Reliability and Testing

| ID | Checklist Item | Status | Evidence Needed |
|----|---------------|--------|-----------------|
| P3-01 | Mobile E2E tests implemented | [ ] | Test code; test results |
| P3-02 | Security tests implemented (upload, CORS, path traversal) | [ ] | Test code; test results |
| P3-03 | Performance tests implemented | [ ] | Benchmark results |
| P3-04 | Structured logging implemented | [ ] | Log output sample |
| P3-05 | Physical device testing on multiple devices | [ ] | Device test matrix |
| P3-06 | Git history scanned for secrets | [ ] | Scan results |

---

## Phase 4 — Deployment

| ID | Checklist Item | Status | Evidence Needed |
|----|---------------|--------|-----------------|
| P4-01 | Production backend deployed over HTTPS | [ ] | Production URL; SSL certificate |
| P4-02 | Staging environment configured | [ ] | Staging URL; separate credentials |
| P4-03 | Model artifact backup strategy | [ ] | Backup procedure; restore test |
| P4-04 | Monitoring and alerting configured | [ ] | Monitoring dashboard; alert rules |
| P4-05 | Automated deployment on merge to main | [ ] | CI/CD pipeline |
| P4-06 | Release notes template completed | [ ] | Release notes document |

---

## Phase 5 — Post-Launch

| ID | Checklist Item | Status | Evidence Needed |
|----|---------------|--------|-----------------|
| P5-01 | User feedback mechanism | [ ] | Feedback channel |
| P5-02 | Model drift monitoring | [ ] | Monitoring setup |
| P5-03 | Iterative improvement process | [ ] | Retraining procedure |
| P5-04 | Database added (if history/accounts approved) | [ ] | Supabase/Postgres with RLS |
| P5-05 | Privacy policy published | [ ] | Privacy policy URL |

---

## Security Checklist (Pre-Release)

| ID | Checklist Item | Status | Evidence Needed |
|----|---------------|--------|-----------------|
| S-01 | No secrets in repository or app bundle | [x] | Scanned; `.gitignore` protects `.env` |
| S-02 | No raw image retention by default | [x] | Backend stateless by design |
| S-03 | Camera/gallery permission copy is clear | [x] | Mobile UI explains permissions |
| S-04 | Upload validation and limits tested | [ ] | Test results |
| S-05 | HTTPS enabled in production | [ ] | Production URL with valid cert |
| S-06 | CORS configured | [ ] | CORS headers |
| S-07 | Rate limiting configured | [ ] | Rate limit headers |
| S-08 | Request timeouts configured | [ ] | Timeout configuration |
| S-09 | Structured logging (no image content) | [ ] | Log output sample |
| S-10 | Git history scanned for secrets | [ ] | Scan results |

---

## Launch Approval Criteria

**ALL of the following must be true before production release:**

1. [ ] CI lint passes and tests run on every push
2. [ ] Model trained on clean dataset with pinned versions
3. [ ] Test-split score recorded in `docs/training-log.md` (no fabricated metrics)
4. [ ] ONNX model exported with provenance
5. [ ] Backend deployed over HTTPS with health endpoint
6. [ ] Detect endpoint implemented with upload validation
7. [ ] Mobile app connected to real backend
8. [ ] End-to-end scan verified on physical Android device
9. [ ] Android APK/AAB built
10. [ ] Privacy policy published
11. [ ] All Critical gaps resolved
12. [ ] All High gaps addressed or explicitly accepted with documented rationale

**Launch approval:** Product owner + engineering lead sign-off required.

**No-GO conditions:** Any Critical gap unresolved; test-split score missing; model metrics fabricated; secrets found in repository.
