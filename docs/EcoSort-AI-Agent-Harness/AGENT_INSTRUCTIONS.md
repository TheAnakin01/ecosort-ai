# Agent Instructions — EcoSort AI

## 1. Mission

Build EcoSort AI as a reliable, understandable mobile product that identifies multiple visible waste objects in a single image, labels each object by material category, and presents cautious sorting guidance.

The goal is a working, testable end-to-end MVP — not a polished mockup that pretends to perform AI inference.

## 2. First action: repository reconnaissance

Before writing or modifying code:

1. Inspect the complete repository tree.
2. Identify existing apps, packages, scripts, assets, tests, model files, environment files and documentation.
3. Read the existing README and package manifests.
4. Run existing tests/build/lint commands where practical.
5. Identify the current branch and uncommitted changes. Never overwrite or discard user work.
6. Produce a concise audit: what exists, what works, what is incomplete, risks, and recommended next step.
7. Reconcile the repository with this specification. Preserve working code unless there is a demonstrated reason to change it.

Do not assume the repository is empty. Do not regenerate an existing project from scratch.

## 3. Source-of-truth hierarchy

When instructions conflict, use this order:

1. The user's latest explicit decision.
2. This documentation pack.
3. Existing implementation, if it is demonstrably working and does not violate an explicit requirement.
4. Agent assumptions — these must be labelled and surfaced for approval.

Do not silently change the four-class taxonomy, model family, mobile framework, API contract, or data-retention behavior.

## 4. Product and technical constraints

- The app must detect **multiple objects** in one image. Whole-image classification alone does not satisfy the requirement.
- Each detection must have a category, confidence score, and bounding box.
- Initial categories are exactly `paper`, `plastic`, `metal`, and `organic`.
- Use a pretrained YOLO nano detector as the first baseline; fine-tune only after dataset inspection and label validation.
- Use FastAPI for the inference API.
- Use React Native + Expo + TypeScript for the mobile app.
- Run inference on the backend for the first MVP. Do not add on-device inference unless the product owner approves it.
- Keep database/auth/history out of the critical path until the core scan flow works. Supabase is a later optional integration.
- Never fabricate model metrics, test results, data sources, or completed functionality.
- Do not make absolute claims such as “this item is recyclable” from appearance alone. Communicate uncertainty and local-rule limitations.

## 5. Required implementation workflow

Work in small, reviewable phases:

### Phase 0 — Audit and plan
- Audit repo and environment.
- Confirm tool versions and run existing tests.
- Produce an implementation plan tied to actual files.
- Do not begin a large rewrite before reporting findings.

### Phase 1 — Project foundation
- Establish or preserve a monorepo structure.
- Add clear READMEs, dependency manifests, environment examples and `.gitignore`.
- Add formatting/linting and basic automated checks.
- Ensure secrets, datasets and large checkpoints are excluded from Git.

### Phase 2 — Dataset and model baseline
- Inspect candidate datasets and licenses.
- Build an explicit mapping from source labels to the four product classes.
- Review bounding boxes and class mapping; do not assume TACO categories map cleanly.
- Create reproducible train/validation/test splits with source-scene grouping to avoid leakage.
- Train/evaluate a baseline only after dataset integrity checks.
- Record the exact dataset version, model weights, configuration, random seed, metrics and limitations.

### Phase 3 — Backend inference
- Implement model loading once per process, image validation, inference, post-processing and stable JSON responses.
- Add health and model-info endpoints.
- Add unit and API tests, including malformed images and no detections.
- Never reload model weights on every request.

### Phase 4 — Mobile scan flow
- Build camera/gallery selection, preview, submit/loading, results, and failure states.
- Render boxes accurately over the displayed image.
- Implement category counts and cautious guidance.
- Test on a physical Android device.

### Phase 5 — Integration hardening
- Verify image orientation, aspect ratio, resize/letterbox transforms and bounding-box mapping.
- Test poor lighting, clutter, overlapping objects, tiny objects and network failure.
- Measure end-to-end latency on documented hardware/network conditions.
- Fix correctness before adding decorative features.

### Phase 6 — Optional persistence and release
- Add Supabase only after explicit approval of the data model and privacy behavior.
- Add history/auth only if included in the agreed release scope.
- Prepare Android build and deployment only after acceptance gates pass.

## 6. Engineering standards

- Prefer simple, modular, typed code over premature abstractions.
- Keep UI, API client, inference service, schemas and domain logic separated.
- Use explicit configuration through environment variables; validate required settings at startup.
- Pin or constrain dependencies and document supported versions.
- Add tests for meaningful logic; do not delete or weaken tests to make a build pass.
- Handle errors explicitly. Do not swallow exceptions or return fake success responses.
- Keep API responses deterministic and versioned.
- Use accessible labels, adequate contrast, touch targets and loading/error feedback.
- Avoid logging image bytes, personal data, tokens or full request payloads.
- Do not add analytics, advertising, user tracking or image retention without approval.

## 7. UI integrity rules

- Do not create fake detections or hard-coded result screens in the production flow.
- If model/API is unavailable, show a clear unavailable/error state or a clearly marked demo mode.
- Do not display confidence as “accuracy”.
- Show “possible material” or “model estimate” where appropriate.
- The overlay must remain aligned after image resizing, cropping, rotation and letterboxing.
- Provide a useful empty state when no objects are detected.

## 8. AI and dataset integrity rules

- Detection boxes must be trained/validated against real bounding-box annotations.
- Keep train, validation and test data separate.
- Avoid near-duplicate leakage across splits.
- Report per-class performance, not only an overall metric.
- Do not tune on the test set.
- Do not claim the model recognizes an item’s exact composition, contamination, resin code or recyclability unless a separately validated capability supports that claim.
- Keep unknown/ambiguous cases uncertain rather than forcing a confident material label.

## 9. Database and privacy rules

- Database persistence is not required for the first scan-only MVP.
- If Supabase is added, use least-privilege Row Level Security policies and migrations.
- Do not store raw images by default.
- If history is enabled, obtain clear user consent and document retention/deletion behavior.
- Never put service-role keys or backend secrets in the mobile app or Git.

## 10. Agent reporting format

At the end of every work session, report:

1. **Inspected:** important files and existing behavior reviewed.
2. **Changed:** files created/modified/deleted and why.
3. **Implemented:** user-visible and technical behavior now working.
4. **Verification:** exact commands run and pass/fail results.
5. **Known issues:** bugs, limitations, risks and unverified assumptions.
6. **Next step:** one recommended next task.
7. **Documentation:** docs updated to match implementation.

Never say “complete” unless the relevant acceptance criteria are verified.

## 11. Git safety

- Do not force-push.
- Do not rewrite shared history.
- Do not commit `.env`, secrets, private images, raw datasets or large model weights unless explicitly requested and appropriate.
- Do not change branches or push without the user's instruction.
- Preserve existing uncommitted work.
