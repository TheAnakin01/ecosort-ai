# AGENTS.md — rules for any AI agent working on EcoSort AI

Read `CLAUDE.md` first. It is authoritative; this file adds the practical rules.

1. **YOLO nano stays the detector.** No model-family change without the product owner's written approval (`docs/decision-log.md`).
2. **Never fake inference.** No hard-coded detections, invented metrics or placeholder success states. A fake detector is allowed only in isolated unit tests.
3. **Verify before integrating.** Code from another agent is a draft. Run the tests, read the diff, compare against the spec.
4. **Report first, then change.** For major changes, state objective, files, plan and risks, and wait for approval.
5. **Keep the API contract stable** (`docs/EcoSort-AI-Agent-Harness/BACKEND_API.md`). The mobile app depends on it.
6. **No secrets, no private images** in the repo. The backend stores no uploads.
7. **Do not format files you are not changing.** CI runs `ruff check` only.
8. **Update `docs/AI-HANDOFF.md`** at the end of every work session, and `docs/decision-log.md` for every decision.

Checks before handing work back:

    ruff check backend ai-model
    cd backend && pytest
    # parity, when weights are available:
    ECOSORT_TEST_WEIGHTS=best.pt ECOSORT_TEST_ONNX=best.onnx pytest tests/test_onnx_parity.py
