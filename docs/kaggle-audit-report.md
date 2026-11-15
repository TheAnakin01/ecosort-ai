# Kaggle audit report — EcoSort AI training pipeline

**Repository:** `TheAnakin01/ecosort-ai`, branch `feature/kaggle-training-preparation`
**Audited notebook:** `ai-model/notebooks/train_ecosort_kaggle.ipynb` (identical to the copy in `Downloads/`)
**Audited scripts:** all files under `ai-model/scripts/`
**Verdict:** the notebook is structurally ready for Kaggle; no Kaggle run has been executed, so no training success can be claimed.

---

## 1. Repository audit

### Layout (`ai-model/`)

| Path | Purpose |
|------|---------|
| `configs/data.yaml` | Dataset config: 4 classes `paper, plastic, metal, organic`; path `../datasets/ecosort` |
| `configs/class_overrides.yaml` | Manual source-class → EcoSort class overrides |
| `notebooks/train_ecosort_kaggle.ipynb` | Kaggle training notebook (audited below) |
| `notebooks/train_ecosort.ipynb` | Colab version (reference) |
| `scripts/download_datasets.py` | Downloads 4 Roboflow datasets from `ROBOFLOW_API_KEY` env var |
| `scripts/prepare_dataset.py` | Merges sources, maps classes, `--resplit`, `--max-share organic=0.3` |
| `scripts/validate_dataset.py` | Validates merged dataset; exits 1 on errors |
| `scripts/train.py` | Fine-tunes YOLO nano; requires validation report unless `--skip-validation-check` |
| `scripts/overfit_check.py` | Reads `results.csv`; writes `overfit_check.json` |
| `scripts/check_hallucinations.py` | False-detection analysis at app thresholds (conf 0.35) |
| `scripts/export_onnx.py` | Exports `best.pt` → ONNX |
| `scripts/dataset_paths.py` | Resolves dataset paths (absolute `data.yaml`) |
| `scripts/evaluate.py` | Scores weights on val/test split |
| `scripts/predict.py` | Runs detector on one image |
| `tests/` | 5 test files, no PyTorch required |
| `weights/best.onnx` + `weights/best.onnx.json` | Committed ONNX artifact (`.pt` files stay out of Git) |

### Model and dataset configuration (preserved)

- Detector: pretrained **Ultralytics YOLO nano** (`yolo11n.pt`). **Not changed.** No switch to MobileNet/SSD/Faster R-CNN.
- Classes: `0: paper, 1: plastic, 2: metal, 3: organic`.
- Image size: `640`. Batch: `16`. Patience: `10`. Default epochs in `train.py`: `50` (notebook overrides to `30`).
- Class overrides already reviewed: `disposable food container: drop`, `foam food container: drop`, `cardboard: paper`. See `configs/class_overrides.yaml` and `docs/dataset-card.md`.

### Four Roboflow datasets (`download_datasets.py` `DATASETS`)

| Folder | Workspace | Project | Version |
|--------|-----------|---------|---------|
| trash-detection | amongus-o6ilp | trash-detection-1fjjc-ipij8 | Not pinned (config: `null`) |
| trashnet | polygence-project | trashnet-a-set-of-annotated-images-of-trash-that-can-be-used-for-object-detection | Not pinned (config: `null`) |
| neat-now | fyp-gojku | neat-now | Not pinned (config: `null`) |
| garbage-cls-3 | objectdetection-z2zn1 | garbage-classification-3-bjcgp | Not pinned (config: `null`) |

These match the notebook's stated sources exactly. Version configuration is now
centralised in `ai-model/configs/datasets.yaml`. All four versions are
currently unpinned (`null`) because no version numbers could be confirmed
against live Roboflow projects (no credentials, Roboflow pages return 403).
The downloader supports explicit pinning: when a version is set, it downloads
exactly that version and fails with a clear error if unavailable; when unset,
it downloads the newest and prints a reproducibility warning. Selected versions
are recorded in `downloads/download_manifest.json` and propagated into
`datasets/ecosort/dataset_report.json` as `source_versions` by
`prepare_dataset.py`.

### Dependencies (`requirements.txt`)

`ultralytics~=8.4.212`, `roboflow~=1.7.3`, `pyyaml~=6.0.3`, `pillow~=12.3.0`. Dev: `pytest~=9.1.1` + `pyyaml` + `pillow` (no torch).

---

## 2. Notebook audit

`train_ecosort_kaggle.ipynb` is standard, valid `.ipynb` JSON with 14 cells (7 markdown + 7 code) in correct execution order.

| Cell | Step | Matches script/args? |
|------|------|----------------------|
| 1 | GPU check via `nvidia-smi`; `UserSecretsClient` gets `ROBOFLOW_API_KEY` (required) and optional `NTFY_TOPIC`; fails clearly if GPU or key missing | N/A (notebook-specific) |
| 2 | `git clone --depth 1` ecosort-ai → `/tmp`, `git pull`, `pip install -r requirements.txt`, `git log`; `cd` into `ai-model` | N/A |
| 3 | `python scripts/download_datasets.py` | ✓ no args; key from env |
| 4 | `python scripts/prepare_dataset.py <4 sources> --resplit --max-share organic=0.3`; then `python scripts/validate_dataset.py` | ✓ args match `prepare_dataset.py` and `validate_dataset.py` defaults |
| 5 | `python scripts/train.py --epochs 30 --name ecosort-baseline --project /kaggle/working/runs`; background thread reads `results.csv` and ntfy-notifies per epoch | ✓ epochs=30 overrides train.py default of 50; patience/imgsz/batch/model use script defaults (10/640/16/yolo11n.pt) |
| 6 | Copy `dataset_report.json` + `validation_report.json` into run dir; copy `best.pt` → `/kaggle/working/best.pt`; `overfit_check.py <run>`; `check_hallucinations.py --weights best.pt --out <run>/hallucination_check_val`; display `results.png`, `confusion_matrix.png`, worst photos | ✓ all args match |
| 7 | Next-steps markdown | N/A |

### Secret handling

- `ROBOFLOW_API_KEY` is read **only** through `kaggle_secrets.UserSecretsClient` into `os.environ`. It is never printed, hardcoded, or written into a cell. ✓
- `NTFY_TOPIC` is optional; absent → notifications off. ✓
- `download_datasets.py` rejects empty keys and publishable (`rf_...`) keys with a clear message. ✓

### Fail-fast behaviour

- No GPU → `SystemExit("No GPU...")`.
- No `ROBOFLOW_API_KEY` secret → `SystemExit` with setup instructions.
- `git clone`/`pip install`/`download_datasets.py` failure → `run()` notifies (urgent) and raises `SystemExit`, stopping the notebook.
- `validate_dataset.py` errors → `run()` raises `SystemExit`, so training does **not** start on an invalid dataset.
- `train.py` refuses to train unless `validation_report.json` exists and `passed` is true (no `--skip-validation-check` passed by the notebook).

---

## 3. Compatibility findings

| Item | Finding |
|------|---------|
| Accelerator | GPU T4 x2, internet On — set in Kaggle notebook settings |
| GPU detection | `nvidia-smi` in cell 1; clear failure if absent |
| Persistent outputs | `/kaggle/working` (`best.pt`, `runs/`); `/tmp` is ephemeral (code + downloads) |
| Roboflow auth | `UserSecretsClient`; key never in a cell |
| Dependency install | `pip install -r requirements.txt` in a subprocess, so upgrades don't clash with the notebook kernel |
| No local paths | All paths are `/tmp`, `/kaggle/working`, or relative to `ai-model/` |
| Training time | ~8–9 hours per run; Kaggle sessions up to 12 h, ~30 GPU h/week |
| Risk | `pip install -r requirements.txt` may attempt to (re)install `torch` on Kaggle; monitor the install cell |
| Risk | `download_datasets.py` downloads the newest Roboflow version each run — results are not bit-for-bit reproducible across time unless versions are pinned |

No hardcoded API keys, no private images, no model-family change. YOLO nano preserved.

---

## 4. Issues found

1. **`train.py` defaults to `--epochs 50`.** The notebook correctly passes `--epochs 30`, so the 30-epoch cap is enforced at invocation. No code change required; documented here so the default does not surprise a future local run.
2. **Dataset versions are now pinning-capable.** `download_datasets.py` reads `configs/datasets.yaml` where each dataset may pin an explicit version. All four versions are currently `null` (unpinned) because no version numbers could be confirmed against live Roboflow projects. When pinned, the downloader downloads exactly that version and fails clearly if unavailable; when unpinned, it downloads the newest and prints a reproducibility warning. Selected versions are recorded in `downloads/download_manifest.json` and propagated into `dataset_report.json` as `source_versions`. **Action needed:** confirm actual version numbers on Roboflow and enter them in `configs/datasets.yaml` before a submission run.
3. **No Kaggle run has been executed.** This environment has no Python, no GPU, and no Roboflow credentials, so `pytest`, the dataset merge, and training cannot be run here. No metrics in this report are claimed from a Kaggle run.
4. **Local test execution:** `pytest` cannot run in this environment (Python not installed). All 5 test files (now extended with version-pinning and provenance tests) are designed to run without GPU or Roboflow credentials; they must be run on a machine with Python + `pytest`.

---

## 5. Changes made

| File | Change |
|------|--------|
| `ai-model/configs/datasets.yaml` | New — central dataset source config with optional version pinning for all four datasets |
| `ai-model/scripts/download_datasets.py` | Modified — reads configs/datasets.yaml, supports explicit version pinning, fails clearly on unavailable pinned versions, prints reproducibility warning for unpinned downloads, writes `downloads/download_manifest.json` |
| `ai-model/scripts/prepare_dataset.py` | Modified — reads download manifest, records `source_versions` in `dataset_report.json`, adds `--manifest` argument |
| `ai-model/tests/test_download_datasets.py` | Extended — tests for config loading, version pinning, newest fallback, manifest writing, unavailable pinned version |
| `ai-model/tests/test_prepare_dataset.py` | Extended — tests for source_versions in report, empty versions without manifest, missing data.yaml, invalid class override |
| `ai-model/tests/test_training_checks.py` | Extended — tests for empty CSV, single epoch, missing weights, training blocked without validation report, invalid training config |
| `docs/kaggle-audit-report.md` | Updated — reflects version pinning implementation |
| `docs/kaggle-training-guide.md` | Updated — version pinning instructions |
| `docs/dataset-card.md` | Updated — version pinning section, pre-submission license warning |
| `docs/training-log.md` | No change — Kaggle runs section already present, no run executed |

No script, config, weight, or test file was deleted or weakened. The YOLO nano architecture and dataset class mappings are unchanged.

---

## 6. Remaining manual actions (before a Kaggle run)

1. Confirm actual Roboflow dataset versions and enter them in `ai-model/configs/datasets.yaml` (currently all `null`/unpinned).
2. Check each dataset's license on its Roboflow page; update `docs/dataset-card.md` when confirmed.
3. On Kaggle: Create → New Notebook → File → Import Notebook, using the notebook's GitHub link.
4. Notebook settings: Accelerator **GPU T4 x2**, Internet **On**.
5. Add-ons → Secrets: add `ROBOFLOW_API_KEY` (Roboflow Private API key) and optional `NTFY_TOPIC`; tick **Attach** for this notebook.
6. Save Version → Save & Run All (Commit) → Save. Wait ~8–9 h.
7. Open the version → Output tab: download `best.pt` and `runs/`.
8. Record the real metrics from `run_info.json` / `train.py` output into `docs/training-log.md`.
