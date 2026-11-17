# 11 Production Roadmap — EcoSort AI

**Audit date:** 2026-11-17  
**Repository:** `TheAnakin01/ecosort-ai`  
**Branch:** `feature/kaggle-kaggle-notebook-setup`

---

## Phase 0 — Critical Blockers

Must be completed before any other work. These block merging to main and any production use.

| Task ID | Priority | Dependencies | Estimated Effort | Expected Outcome | Acceptance Criteria |
|---------|----------|--------------|------------------|------------------|---------------------|
| P0-01 | Critical | Python environment; ruff | 2-4 hours | CI lint passes; tests run | `ruff check backend ai-model` exits 0; `pytest` runs in CI |
| P0-02 | Critical | Roboflow API access; Kaggle GPU | 8-12 hours (Kaggle run) | Model trained on clean dataset; versions pinned | Test-split mAP@50-95 recorded; overtraining verdict recorded; false-detection share recorded |
| P0-03 | Critical | Trained `best.pt`; ultralytics | 1-2 hours | ONNX model exported with provenance | `best.onnx` and `best.onnx.json` exist; ONNX loads and runs |
| P0-04 | Critical | FastAPI; ONNX Runtime or PyTorch | 1-2 days | `POST /api/v1/detect` implemented; image validation; error handling | Health endpoint 200; detect returns schema-conforming response; invalid images rejected safely |
| P0-05 | Critical | Deployed backend; mobile app | 4-8 hours | Mobile app connected to real API | End-to-end scan works on physical Android device |

---

## Phase 1 — Core Application Completion

| Task ID | Priority | Dependencies | Estimated Effort | Expected Outcome | Acceptance Criteria |
|---------|----------|--------------|------------------|------------------|---------------------|
| P1-01 | High | Trained model; ONNX export | 4-8 hours | Confidence threshold tuned on validation data | Threshold recorded; false-detection share acceptable |
| P1-02 | High | Trained model; confusion matrix | 2-4 hours | Confusion matrix reviewed; class confusions documented | Review notes in `docs/training-log.md` |
| P1-03 | High | False-detection photos | 2-4 hours | Worst photos reviewed; label gaps vs model faults distinguished | Review notes in `docs/training-log.md` |
| P1-04 | High | Backend; deployment target | 4-8 hours | Backend deployed over HTTPS; CORS configured | Backend accessible over HTTPS; health responds |
| P1-05 | High | Mobile app; deployed backend | 2-4 hours | Android APK/AAB built; installed on device | App installs; scan works on physical device |
| P1-06 | High | Mobile app | 2-4 hours | Accessibility audit completed; WCAG issues fixed | WCAG AA where feasible; touch targets 44-48 dp |
| P1-07 | Medium | Python environment | 1-2 hours | Dependency vulnerability scan completed | `pip audit` or equivalent run; critical vulnerabilities addressed |

---

## Phase 2 — AI/ML Productionization

| Task ID | Priority | Dependencies | Estimated Effort | Expected Outcome | Acceptance Criteria |
|---------|----------|--------------|------------------|------------------|---------------------|
| P2-01 | High | Roboflow access | 2-4 hours | Dataset versions pinned; licenses confirmed | All 4 versions in `configs/datasets.yaml`; all licenses confirmed or documented UNKNOWN |
| P2-02 | Medium | Team capacity | 1-2 weeks | Team photos collected and annotated | Representative waste photos added as dataset source |
| P2-03 | Medium | Trained model; target hardware | 4-8 hours | Inference latency and memory measured on target | Latency and memory documented |
| P2-04 | Medium | Trained model; plastic/metal recall low | 1-2 days | Investigation of plastic/metal recall issues | Documented findings; optional model improvements |
| P2-05 | Medium | Model registry need | 1-2 days | Model artifact store established (outside Git) | `best.pt` and `best.onnx` stored with version tags |
| P2-06 | Low | Model size | 30 minutes | Model size documented | File size recorded in `docs/training-log.md` |

---

## Phase 3 — Reliability and Testing

| Task ID | Priority | Dependencies | Estimated Effort | Expected Outcome | Acceptance Criteria |
|---------|----------|--------------|------------------|------------------|---------------------|
| P3-01 | High | Mobile app; backend | 1-2 days | Mobile E2E tests implemented and passing | Scan flow tested end-to-end |
| P3-02 | High | Backend | 4-8 hours | Security tests implemented (upload validation, CORS, path traversal) | Security tests pass |
| P3-03 | Medium | Backend; target hardware | 4-8 hours | Performance tests implemented | Latency, memory, throughput baselines recorded |
| P3-04 | Medium | Backend | 2-4 hours | Structured logging implemented; no image content logged | Logs safe for production |
| P3-05 | Medium | Mobile app | 1-2 days | Physical device testing on multiple devices | App works on different screen sizes and Android versions |
| P3-06 | Low | Git history | 1-2 hours | Git history scanned for secrets | No secrets found; or secrets rotated |

---

## Phase 4 — Deployment

| Task ID | Priority | Dependencies | Estimated Effort | Expected Outcome | Acceptance Criteria |
|---------|----------|--------------|------------------|------------------|---------------------|
| P4-01 | High | Hosting provider selected | 1-2 days | Production backend deployed; HTTPS configured | Backend accessible over HTTPS with valid certificate |
| P4-02 | High | Staging environment | 1 day | Staging environment configured with separate credentials | Staging isolated from production |
| P4-03 | Medium | Model artifacts | 4 hours | Backup strategy for model artifacts | Model artifacts backed up; restore tested |
| P4-04 | Medium | Monitoring | 1 day | Monitoring and alerting configured | Uptime monitoring; error alerts |
| P4-05 | Medium | CI/CD | 1 day | Automated deployment on merge to main | Deploys triggered by CI |
| P4-06 | Low | Release process | 4 hours | Release notes template; version recording | Release notes include model version, classes, limitations |

---

## Phase 5 — Post-Launch

| Task ID | Priority | Dependencies | Estimated Effort | Expected Outcome | Acceptance Criteria |
|---------|----------|--------------|------------------|------------------|---------------------|
| P5-01 | Medium | Launched app | Ongoing | User feedback collected | Feedback mechanism in place |
| P5-02 | Medium | Launched model | Ongoing | Model drift monitoring | Performance degradation detected |
| P5-03 | Medium | User feedback | Ongoing | Iterative model improvements | Model retrained with new data as needed |
| P5-04 | Low | Database decision | N/A | Supabase/Postgres added if history/accounts approved | Database implemented with RLS |
| P5-05 | Low | Privacy requirements | N/A | Privacy policy published; consent mechanism | Privacy policy live; user consent obtained |

---

## Definition of Done (MVP Release)

All of the following must be true before MVP release:

- [ ] CI lint passes; tests run on every push
- [ ] Model trained on clean dataset with pinned versions
- [ ] Test-split score recorded in `docs/training-log.md`
- [ ] ONNX model exported with provenance
- [ ] Backend detect endpoint implemented and tested
- [ ] Backend deployed over HTTPS
- [ ] Mobile app connected to real backend
- [ ] End-to-end scan works on physical Android device
- [ ] Android APK/AAB built
- [ ] Privacy policy published
- [ ] All Critical gaps (P0-01 to P0-05) resolved
- [ ] All High gaps addressed or explicitly accepted
