# Training log

One entry per training run. Only write numbers that a real run produced. Copy them from the table `train.py` prints, or from the run's `run_info.json`.

## Runs

| Date | Run name | Starting weights | Dataset built on | Epochs | Image size | Seed | Split scored | Precision | Recall | mAP@50 | mAP@50-95 |
|---|---|---|---|---|---|---|---|---|---|---|---|
| 2026-11-15 | ecosort-baseline-2 | yolo11n.pt | 2026-11-15T07:30:44+00:00 | 30 | 640 | 0 | validation | 0.810 | 0.703 | 0.788 | 0.690 |
| 2026-11-16 | ecosort-baseline (Kaggle, "run 2") | yolo11n.pt | four sources, `--max-share organic=0.3` | 30 | 640 | 0 | validation (its own, larger split) | 0.776 | 0.633 | 0.721 | 0.564 |

## Per-class results

A good overall score can hide a weak class.

| Run name | Class | Precision | Recall | AP@50 | AP@50-95 |
|---|---|---|---|---|---|
| ecosort-baseline-2 | paper | 0.845 | 0.768 | 0.860 | 0.797 |
| ecosort-baseline-2 | plastic | 0.730 | 0.638 | 0.694 | 0.595 |
| ecosort-baseline-2 | metal | 0.800 | 0.675 | 0.764 | 0.644 |
| ecosort-baseline-2 | organic | 0.866 | 0.729 | 0.836 | 0.725 |

## Notes per run

### ecosort-baseline-2 (2026-11-15)

- **Setup:** Google Colab, Tesla T4, Ultralytics 8.4.213, PyTorch 2.14.1+cu130, batch 16. 15,518 training images, 4,525 validation images with 10,238 boxes. About 5.5 minutes per epoch, roughly 2 hours 45 minutes in total.
- **What the scores mean:** on the validation split, about 81% of the model's detections were correct (precision) and it found about 70% of the labelled items (recall). These are not "accuracy".
- **Weakest class: plastic** (AP@50 0.694, recall 0.638). It misses more than a third of labelled plastic items. Metal recall is also low (0.675).
- **Strongest: paper and organic** (AP@50 0.860 and 0.836).
- **Still improving when it stopped.** mAP@50 went 0.775, 0.787, 0.784, 0.788 over epochs 26 to 29. A longer run would probably gain a little.
- **Known problems with this run's data:** two container classes were labelled organic by mistake, and the sources overlap in ways that cannot be fully detected. See [dataset-card.md](dataset-card.md). Treat the scores as somewhat optimistic.
- **Not done yet:** no test-split score, no confusion matrix review, no look at failure photos, no check on the team's own photos. The confidence thresholds are still the untuned defaults.
- **Speed, measured on a 2-core CPU:** about 70 ms per 1280x960 image after the first request, and about 760 MB of memory with the model loaded.

### Run 2: ecosort-baseline on Kaggle (2026-11-16)

- **Source of these numbers:** the `train_metrics` and `train_results` stored inside the run's `best.pt`, read without loading the model. The file is `best.zip` at the top of the repo (merged in PR #6) (SHA-256 `e57748e9bdcab9d4d41bda3c0e6b502d5dada0946dc0403c3abf1f74491f6669`). Ultralytics 8.4.214, finished 2026-11-16 00:49 UTC.
- **Data:** four sources (adds GARBAGE CLASSIFICATION 3), organic capped at 30% of boxes.
- **Speed:** about 5.4 minutes per epoch on Kaggle, 2.7 hours in total (Colab took about 17 minutes per epoch on this dataset).
- **Overtraining check: none.** Validation loss fell every epoch and the best epoch was the last (30). Verdict "still improving", but only just: mAP@50-95 rose 0.005 over the last 5 epochs.
- **Not comparable with run 1 as it stands.** Each run was scored on its own validation split, and run 2's is larger and harder (crowded produce piles, and the container classes run 1 wrongly called organic are gone). `notebooks/compare_models_kaggle.ipynb` scores both models on the same photos that neither trained on. Until that has run, do not call either model better.
- **Missing:** per-class scores and the false-detection report. They are in the Kaggle run's Output (`runs/ecosort-baseline/`), not in the repo yet.

## Rules

- Record the **overtraining check** verdict (from `train.py` or `overfit_check.py`) for every run.
- Record the **false-detection check** (`check_hallucinations.py`, validation split, app thresholds): the share of boxes on nothing, per class. A run with a better mAP but more boxes on nothing is not automatically better for the app.

- Scores from `train.py` are **validation** scores. Use them to compare runs and choose settings.
- The **test** score comes from `python scripts/evaluate.py --split test`. Run it once, on the final model, after the confidence threshold is chosen.
- Never report a training-split score as the model's performance.

## Pipeline check with fake data (not a model result)

On 2026-11-14 the scripts were run end to end on a synthetic dataset of coloured rectangles (`ai-model/tests/make_synthetic_dataset.py`), on a CPU, to prove that they work. That model scored about 0.99 mAP@50 because telling four solid colours apart is trivial. The number says nothing about waste detection and must not be quoted as a result.

## Kaggle runs

Run 2 (2026-11-16) is recorded in the Runs table above. Metrics may only be recorded from a real Kaggle run, copied from the run's `run_info.json`, from `train.py`'s printed validation table, or from the metrics stored in its `best.pt`. Do not fabricate training or validation results.

To record a Kaggle run:

| Date | Run name | Starting weights | Epochs | Image size | Seed | Best epoch | Precision | Recall | mAP@50 | mAP@50-95 | Overtraining verdict | Boxes on nothing |
|------|----------|------------------|--------|------------|------|------------|-----------|--------|--------|-----------|----------------------|------------------|

- Run name comes from `run_info.json["run_name"]` (e.g. `ecosort-baseline`).
- Best epoch, overtraining verdict and `best_map50_95` come from `overfit_check.json`.
- Boxes on nothing (`share_on_nothing`) comes from `hallucination_check_val/report.json`.
- Per-class precision/recall/AP come from `run_info.json["validation_metrics"]`.
