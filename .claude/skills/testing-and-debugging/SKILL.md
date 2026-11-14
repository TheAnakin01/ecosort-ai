---
name: testing-and-debugging
description: Plan and execute unit, integration, model, API, mobile, and regression tests for EcoSort AI. Use when diagnosing bugs or validating changes.
---

# Testing and Debugging

## Goal

Make changes safe, reproducible, and verifiable across the ML, API, and mobile layers.

## Workflow

1. Reproduce the problem and capture the exact error/steps.
2. Inspect relevant code, configuration, dependency versions, and Git diff.
3. Form a testable hypothesis.
4. Add or identify a focused regression test.
5. Make the smallest appropriate change.
6. Run focused tests, then broader checks.
7. Report evidence and remaining risk.

## Test layers

### Dataset and model
- Annotation parser and class mapping
- Bounding-box validity and transforms
- Dataset split integrity
- Preprocessing consistency
- Inference output schema
- Evaluation reproducibility

### API
- Request validation
- Valid, invalid, corrupt, and oversized images
- Multiple detections and empty detections
- Model load and inference failures
- Response schema and coordinate convention

### Mobile
- Camera/gallery permissions
- Image selection and orientation
- Upload progress, timeout, retry, and server errors
- Multiple overlays and counts
- No-detection and invalid-response states
- Accessibility and layout regression

## Quality gates

Run only commands supported by the repository's actual setup. Common examples may include:
- Python: `pytest`, `ruff`, `mypy` or `pyright`
- TypeScript: package scripts for lint, typecheck, and tests
- Mobile: Expo/platform build checks and device/simulator smoke tests

Inspect package scripts before assuming command names.

## Debugging rules

- Do not suppress exceptions just to make tests pass.
- Do not weaken assertions without explaining why.
- Do not delete failing tests to hide regressions.
- Do not claim a test passed unless it was executed successfully.
- Separate environment/tooling failures from product-code failures.
- Record untested platforms and unavailable hardware.

## Final report

List changed files, tests run, exact results, unresolved failures, and reproduction steps for any remaining bug.
