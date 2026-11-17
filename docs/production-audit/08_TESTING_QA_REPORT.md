# 08 Testing and QA Report — EcoSort AI

**Audit date:** 2026-11-17  
**Repository:** `TheAnakin01/ecosort-ai`  
**Branch:** `feature/kaggle-kaggle-notebook-setup`

---

## Test Execution Status

**Python is not available in this audit environment** (only 0-byte Windows Store stubs at `C:\Users\lenovo\AppData\Local\Microsoft\WindowsApps\`). Therefore:

- `pytest` **could not be executed** for either `ai-model/` or `backend/`
- No test results are reported as "passed" or "failed" based on execution
- All test status below is based on **source code inspection only**

---

## Test Infrastructure

### ai-model/ Tests

| Test File | Purpose | Dependencies | Can Run Without PyTorch? | Status |
|-----------|---------|--------------|---------------------------|--------|
| `test_download_datasets.py` | Version pinning, config loading, key checks, dataset alias | pytest, pyyaml, yaml | Yes | Inspected only |
| `test_prepare_dataset.py` | Class mapping, merge, dedupe, max-share, provenance, invalid boxes | pytest, pyyaml, yaml | Yes | Inspected only |
| `test_validate_dataset.py` | Dataset validation logic | pytest, pyyaml | Yes | Inspected only |
| `test_dataset_paths.py` | Path resolution (absolute data.yaml) | pytest, pyyaml | Yes | Inspected only |
| `test_training_checks.py` | Overtraining, hallucinations, training blocks, missing weights | pytest | Partially (some need torch) | Inspected only |
| `make_synthetic_dataset.py` | Coloured-rectangle smoke test (not waste data) | pillow | Yes | Inspected only |

**Command to run:** `cd ai-model && pip install -r requirements-dev.txt && pytest`

### backend/ Tests

| Test File | Purpose | Dependencies | Can Run Without Model Weights? | Status |
|-----------|---------|--------------|--------------------------------|--------|
| `test_api.py` | API endpoint tests | FastAPI test client | Yes | Inspected only |
| `test_onnx_detector.py` | ONNX detector tests | ONNX Runtime | No (needs weights) | Inspected only |
| `test_onnx_parity.py` | PyTorch vs ONNX parity | PyTorch, ONNX, weights | No (needs weights) | Inspected only |
| `test_real_model.py` | Real model test | PyTorch, weights | No (needs weights) | Inspected only |

**Command to run:** `cd backend && pip install -r requirements-dev.txt && pytest`

### mobile/ Tests

| Test File | Purpose | Dependencies | Status |
|-----------|---------|--------------|--------|
| `boxes.test.ts` | Box utility tests | Jest/React Native testing | Inspected only |
| `history.test.ts` | History tests | Jest/React Native testing | Inspected only |

**Command to run:** `cd mobile && npm test` (or equivalent per package.json)

---

## ai-model/ Test Coverage Analysis

### Covered (with tests)

| Area | Test Coverage | Evidence |
|------|---------------|----------|
| Version number selection (newest vs pinned) | `test_download_datasets.py` | `test_newest_version_is_picked_by_number_not_text`, `test_find_version_picks_requested_version`, `test_find_version_picks_newest_when_none_requested`, `test_find_version_fails_clear_when_requested_version_unavailable` |
| API key validation | `test_download_datasets.py` | `test_key_checks`, `test_missing_key_stops_with_a_clear_message` |
| Dataset download skip when present | `test_download_datasets.py` | `test_needs_no_key_or_network_when_everything_is_downloaded` |
| Dataset sources match Colab notebook | `test_download_datasets.py` | `test_same_datasets_as_the_colab_notebook` |
| Config loading from YAML | `test_download_datasets.py` | `test_load_dataset_config_returns_all_four_datasets`, `test_load_dataset_config_reads_yaml_config`, `test_load_dataset_config_fails_on_empty_config` |
| DATASETS/FALLBACK_DATASETS alias | `test_download_datasets.py` | `test_fallback_datasets_match_dataets_alias` |
| Class mapping by keyword | `test_prepare_dataset.py` | `test_map_class_by_keyword`, `test_garbage_classification_3_classes`, `test_overrides_win_over_keywords` |
| Polygon-to-box conversion | `test_prepare_dataset.py` | `test_polygon_label_becomes_box` |
| Invalid box clipping/rejection | `test_prepare_dataset.py` | `test_invalid_boxes_are_clipped_or_rejected` |
| Source key grouping (Roboflow copies) | `test_prepare_dataset.py` | `test_source_key_groups_roboflow_copies` |
| Split keeps copies together | `test_prepare_dataset.py` | `test_fallback_split_keeps_copies_of_one_photo_together` |
| Multi-source merge | `test_prepare_dataset.py` | `test_merges_two_sources_into_ecosort_layout` |
| Invalid source boxes removed | `test_prepare_dataset.py` | `test_invalid_source_boxes_are_removed_and_counted` |
| Dry run copies nothing | `test_prepare_dataset.py` | `test_dry_run_copies_nothing` |
| Identical files deduped | `test_prepare_dataset.py` | `test_identical_files_are_kept_once_even_across_sources` |
| Duplicate box kept once | `test_prepare_dataset.py` | `test_a_box_listed_twice_is_kept_once` |
| Same filename in different folders | `test_prepare_dataset.py` | `test_same_file_name_in_two_folders_of_a_source_is_not_overwritten` |
| Max-share organic cap | `test_prepare_dataset.py` | `test_max_share_leaves_out_the_most_crowded_single_class_photos`, `test_max_share_stops_as_soon_as_the_share_is_reached`, `test_max_share_rejects_bad_values` |
| Source versions in report | `test_prepare_dataset.py` | `test_dataset_report_records_source_versions_from_manifest`, `test_dataset_report_has_empty_source_versions_without_manifest` |
| Missing data.yaml fails | `test_prepare_dataset.py` | `test_missing_data_yaml_fails_with_clear_message` |
| Invalid class override rejected | `test_prepare_dataset.py` | `test_invalid_class_override_is_rejected` |
| Path resolution | `test_dataset_paths.py` | `test_repo_config_points_at_the_dataset_folder_inside_ai_model`, `test_relative_path_is_resolved_from_the_config_file_not_the_current_folder`, `test_absolute_path_is_kept`, `test_missing_dataset_folder_gives_a_clear_message` |
| Overtraining detection | `test_training_checks.py` | `test_rising_validation_loss_is_overtraining`, `test_scores_still_rising_at_the_end`, `test_flat_scores_have_levelled_off`, `test_read_results_handles_ultralytics_padding`, `test_read_results_raises_on_empty_csv`, `test_check_single_epoch` |
| IoU calculation | `test_training_checks.py` | `test_iou` |
| Detection outcome sorting | `test_training_checks.py` | `test_each_kind_of_detection_is_sorted_correctly`, `test_most_confident_box_claims_the_item`, `test_unfound_items_and_empty_photos` |
| Summary counts hallucinations | `test_training_checks.py` | `test_summary_counts_hallucinations_per_class` |
| Missing weights fails fast | `test_training_checks.py` | `test_check_hallucinations_missing_weights` |
| Training blocked without validation | `test_training_checks.py` | `test_train_blocked_without_validation_report` |
| Invalid training config rejected | `test_training_checks.py` | `test_invalid_training_config_rejected` |

### Not Covered (Missing Tests)

| Area | Gap |
|------|-----|
| `validate_dataset.py` unit tests | `test_validate_dataset.py` exists but was not read in full; coverage unknown |
| Backend API unit tests | `test_api.py` exists but not executed |
| ONNX detector tests | `test_onnx_detector.py` needs weights |
| ONNX parity tests | `test_onnx_parity.py` needs weights |
| Real model tests | `test_real_model.py` needs weights |
| Mobile E2E tests | None |
| Mobile physical device tests | None |
| Security tests | None |
| Performance tests | None |

---

## Backend Test Coverage Analysis

| Area | Test Coverage | Evidence |
|------|---------------|----------|
| API endpoints | `test_api.py` exists | Not executed |
| ONNX detector | `test_onnx_detector.py` exists | Needs weights |
| ONNX/PyTorch parity | `test_onnx_parity.py` exists | Needs weights |
| Real model integration | `test_real_model.py` exists | Needs weights |

---

## CI/CD Testing

| Workflow | Status | Tests Run |
|----------|--------|-----------|
| `.github/workflows/tests.yml` | Lint failing | `ruff check backend ai-model` (failing), then `pytest` (skipped due to lint failure) |

**Critical issue:** CI lint step fails, so tests never run in CI. The `ruff check backend ai-model` command fails. Root cause not determined (logs inaccessible via API — 403).

---

## Linting and Formatting

| Tool | Config | Status |
|------|--------|--------|
| Ruff | `ruff.toml` | `ruff check backend ai-model` — **failing in CI** |
| Format | Not configured | AGENTS.md: "Do not format files you are not changing. CI runs `ruff check` only." |

---

## Test Quality Assessment

| Criterion | Assessment |
|-----------|------------|
| Tests are not weakened/skipped | ✅ All tests present and intact |
| Tests don't require GPU | ✅ ai-model tests need no GPU |
| Tests don't require Roboflow credentials | ✅ ai-model tests need no network |
| Tests don't require model weights | Partial (backend tests need weights) |
| Synthetic data used for smoke testing | ✅ `make_synthetic_dataset.py` |
| Tests run on every push | ✅ CI workflow configured |
| Test results documented honestly | ✅ No fabricated results |

---

## Missing Test Coverage (Priority Order)

| Priority | Gap | Required Work |
|----------|-----|---------------|
| Critical | CI lint failing (tests never run in CI) | Fix `ruff check backend ai-model` |
| Critical | No test-split model evaluation | Execute `scripts/evaluate.py --split test` on real model |
| Critical | No backend integration tests against real model | Implement and run backend tests with real weights |
| High | No mobile E2E tests | Add mobile end-to-end tests |
| High | No physical device testing | Test on physical Android device |
| High | No security tests | Add upload validation, CORS, path traversal tests |
| Medium | No performance tests | Measure inference latency, memory, throughput |
| Medium | No `validate_dataset.py` unit test review | Verify test coverage of validation script |
| Medium | Dependency vulnerability scan | Run `pip audit` or equivalent |

---

## Recommended Test Strategy

1. **Fix CI lint** so `pytest` runs on every push
2. **Run ai-model tests** on a machine with Python: `cd ai-model && pip install -r requirements-dev.txt && pytest`
3. **Train a real model** on Kaggle, then run `scripts/evaluate.py --split test`
4. **Export ONNX** and run backend parity tests: `ECOSORT_TEST_WEIGHTS=best.pt ECOSORT_TEST_ONNX=best.onnx pytest tests/test_onnx_parity.py`
5. **Connect mobile to real backend** and run E2E tests on physical device
6. **Add security tests** for image upload validation, CORS, path traversal
7. **Add performance tests** for inference latency and memory
