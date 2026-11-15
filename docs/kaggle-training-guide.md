# Kaggle training guide — EcoSort AI detector

Trains the YOLO nano waste detector (`paper`, `plastic`, `metal`, `organic`) on Kaggle GPU T4 x2, unattended, using `Save & Run All (Commit)`. The trained model is `best.pt` in the version's **Output** tab.

This guide covers `ai-model/notebooks/train_ecosort_kaggle.ipynb`. The notebook runs `scripts/download_datasets.py`, `scripts/prepare_dataset.py`, `scripts/validate_dataset.py`, `scripts/train.py`, `scripts/overfit_check.py` and `scripts/check_hallucinations.py` from the `ecosort-ai` repository.

---

## One-time setup

### 1. Kaggle account and phone verification

Sign up at kaggle.com. Under **Settings**, verify your phone number. Kaggle requires this before it enables GPU or internet for a notebook.

### 2. (Recommended before a submission run) Pin dataset versions

Dataset versions are configured in `ai-model/configs/datasets.yaml` in the repository. All four versions are currently unpinned (`null`), meaning each run downloads the newest Roboflow version — results are not bit-for-bit reproducible across runs.

Before a submission run:
1. Run the notebook once and read each dataset's actual version from the cell output (`<folder>: downloading version <id>`) and from `downloads/download_manifest.json`.
2. Enter those version numbers in `configs/datasets.yaml`.
3. Commit the updated config so future runs use the same versions.

Never guess version numbers. A pinned version that is unavailable on Roboflow will cause a clear download failure rather than a silent substitution.

### 3. Import the notebook

On Kaggle: **Create → New Notebook**, then **File → Import Notebook** and enter the notebook from the feature branch:

```
https://github.com/TheAnakin01/ecosort-ai/blob/feature/kaggle-training-preparation/ai-model/notebooks/train_ecosort_kaggle.ipynb
```

The notebook clones the `feature/kaggle-training-preparation` branch automatically (cell 2), so importing from any branch works — the notebook always checks out the correct branch before running.

### 3.5. Branch and commit verification

The notebook verifies its Git state in cell 3:

- It confirms the active branch is `feature/kaggle-training-preparation`.
- It prints the actual commit hash and subject line.
- It fails with a clear message if the wrong branch is checked out.

This ensures the training runs against the exact code you intend. The commit hash is printed in the cell output — record it in `docs/training-log.md` for reproducibility.


### 3. Notebook settings (right panel / ⋮ → Settings)

| Setting | Value |
|---------|-------|
| Accelerator | **GPU T4 x2** |
| Internet | **On** |

### 4. Secrets (Add-ons → Secrets)

Add these secrets and tick **Attach** for this notebook:

| Secret | Value | Required |
|--------|-------|----------|
| `ROBOFLOW_API_KEY` | Your Roboflow **Private** API key (Roboflow → Settings → API Keys) | Yes |
| `NTFY_TOPIC` | Your ntfy topic name for phone notifications | Optional |

The notebook reads `ROBOFLOW_API_KEY` only through Kaggle's `UserSecretsClient`. The key is never typed into a cell, never printed, and never committed.

---

## Every run

**Save Version → Save & Run All (Commit) → Save.** Kaggle runs every cell in the background; you can close the browser.

When it finishes, open the version and go to **Output**:
- Trained model: `best.pt`
- Full run: `runs/` (includes `results.png`, `confusion_matrix.csv/png`, `run_info.json`)

Before committing, you may run the first cell interactively to confirm GPU, internet and secrets are configured.

---

## What the notebook does, cell by cell

1. **Check the settings** — verifies an NVIDIA GPU (`nvidia-smi`), loads `ROBOFLOW_API_KEY` from Kaggle Secrets (fails with a clear message if missing), loads optional `NTFY_TOPIC`.
2. **Get the code and libraries** — clones `ecosort-ai` into `/tmp`, `git pull`s, `pip install -r requirements.txt`, records the code version.
3. **Download the four Roboflow datasets** — Trash Detection, TrashNet, Neat Now, GARBAGE CLASSIFICATION 3 (`objectdetection-z2zn1` copy) into `downloads/`.
4. **Build and check the merged dataset** — `prepare_dataset.py ... --resplit --max-share organic=0.3`, then `validate_dataset.py`. Training does not start if validation fails.
5. **Train** — `train.py --epochs 30 --name ecosort-baseline --project /kaggle/working/runs`. Stops early after 10 epochs without improvement (`best.pt` is the best epoch). An ntfy notification is sent after every epoch if a topic is set.
6. **Check for overtraining and false detections** — copies dataset and validation reports into the run folder, saves `best.pt` to `/kaggle/working/best.pt`, runs `overfit_check.py` and `check_hallucinations.py` (confidence 0.35), and displays `results.png`, `confusion_matrix.png` and the worst false-positive photos.
7. **Next steps** — download `best.pt` and `runs/`, record metrics in `docs/training-log.md`, optionally export ONNX with `python scripts/export_onnx.py --weights best.pt`.

---

## Outputs available from the Output tab

- `best.pt` — best validation checkpoint
- `runs/ecosort-baseline*/results.csv` — per-epoch metrics
- `runs/ecosort-baseline*/results.png`, `confusion_matrix.png`
- `runs/ecosort-baseline*/run_info.json` — settings, versions, seed, validation metrics
- `runs/ecosort-baseline*/overfit_check.json` — overtraining verdict
- `runs/ecosort-baseline*/hallucination_check_val/report.json` + `worst_photos/` — false-detection analysis
- `runs/ecosort-baseline*/dataset_report.json`, `validation_report.json`

---

## Troubleshooting

| Symptom | Cause / fix |
|---------|-------------|
| `No GPU. ... set Accelerator to 'GPU T4 x2'` | Set Accelerator to **GPU T4 x2** and Internet **On** in notebook settings, then re-run. |
| `No ROBOFLOW_API_KEY secret` | Add `ROBOFLOW_API_KEY` in Add-ons → Secrets, paste the **Private** (not publishable `rf_...`) key, tick **Attach**, re-run. |
| `Roboflow rejected the key` | You pasted the publishable key (`rf_...`) or a wrong key. Use the Private API Key from Roboflow → Settings → API Keys. |
| A `run(...) / step failed` message | Read the cell output above it. Common causes: no internet (clone/pip/download fail), invalid Roboflow key, or dataset validation errors. |
| `pip install` cell is slow or reinstalls torch | Kaggle pre-installs torch; `ultralytics` should not replace it. If the install cell takes very long, let it finish; do not interrupt. |
| Training stops before 30 epochs | Expected: early stopping patience = 10. `best.pt` remains the best epoch. |
| Notifications stop | If you set `NTFY_TOPIC` and notifications stop for ~40 min, open the notebook page and check the log. |
| `Expected branch 'feature/kaggle-training-preparation', but got ...` | The notebook checked out the wrong branch. Check that the feature branch exists on GitHub and that you have internet access. Re-run the notebook. |
| `git clone ... failed` or `git pull origin ... failed` | No internet access or the branch does not exist on GitHub. Verify Internet is **On** in notebook settings and that `feature/kaggle-training-preparation` has been pushed to the repository. |

---

## After the run

1. Download `best.pt` and the `runs/` folder from the version's **Output** tab.
2. Copy the validation table, overtraining verdict and false-detection table into `docs/training-log.md` from a **real** run only — never invent metrics.
3. For deployment, convert with `python scripts/export_onnx.py --weights best.pt` (backend serves ONNX).
4. Do not run a test-split evaluation yet; that is the final score, run once after the confidence threshold is chosen on the validation split.
