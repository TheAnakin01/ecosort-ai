# Development Roadmap

## Phase 0 — Repository audit and product baseline
Deliverables:
- Repository audit.
- Confirmed environment/tool versions.
- Agreed architecture and phase plan.
- No destructive rewrites.

Gate: existing work understood and preserved.

## Phase 1 — Foundation
Tasks:
- Establish monorepo or adapt existing structure.
- Create Python virtual environment and backend dependencies.
- Create Expo TypeScript app.
- Add `.gitignore`, `.env.example`, README files and lint/test setup.
- Confirm Android development workflow.

Gate: mobile app launches; backend starts and health endpoint responds.

## Phase 2 — Dataset preparation
Tasks:
- Inspect TACO and other candidate sources.
- Verify license/terms.
- Define label mapping.
- Annotate/review bounding boxes.
- Validate boxes and images.
- Deduplicate and split by scene/source.
- Produce dataset card and class distribution report.

Gate: reproducible dataset with verified annotations and no obvious split leakage.

## Phase 3 — AI baseline
Tasks:
- Load pretrained YOLO nano checkpoint.
- Train/fine-tune on prepared dataset.
- Evaluate on validation set.
- Inspect errors and tune threshold.
- Final held-out test evaluation.
- Save model artifact metadata.

Gate: real model produces detections and honest evaluation results.

## Phase 4 — Backend API
Tasks:
- Implement model lifecycle.
- Add health/model-info/categories endpoints.
- Add validated detect endpoint.
- Implement coordinate mapping and category counts.
- Add unit and API tests.

Gate: documented API contract passes tests with real model integration.

## Phase 5 — Mobile core flow
Tasks:
- Home screen.
- Camera and gallery input.
- Preview and retake.
- API client and loading/error states.
- Results image overlay.
- Category summary and guidance.
- Accessibility and responsive layout.

Gate: end-to-end scan works on a physical Android device.

## Phase 6 — Reliability and user testing
Tasks:
- Test diverse images and difficult conditions.
- Fix box alignment and class mapping errors.
- Measure latency and resource usage.
- Conduct small usability test.
- Improve copy and recovery states.

Gate: MVP acceptance checklist passes.

## Phase 7 — Optional persistence
Only after approval:
- Supabase project and SQL migrations.
- Auth and profile.
- Scan metadata/history.
- RLS and deletion.
- Optional feedback.

Gate: two-user isolation and deletion tests pass.

## Phase 8 — Deployment and release
Tasks:
- Deploy backend.
- Configure HTTPS and environment secrets.
- Build Android APK/AAB using EAS.
- Test production endpoint from physical device.
- Prepare README, demo and known-limitations note.

Gate: release candidate passes deployment checklist.

## Priority rule

Do not build history, gamification, dashboards, advanced animations or offline inference before the end-to-end multi-object scan flow is correct.
