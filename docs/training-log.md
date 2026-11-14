# Training log

One entry per training run. Only write numbers that a real run produced. Copy them from the table `train.py` prints, or from the run's `run_info.json`.

No real training run has finished yet.

## Runs

| Date | Run name | Starting weights | Dataset built on | Epochs | Image size | Seed | Split scored | Precision | Recall | mAP@50 | mAP@50-95 |
|---|---|---|---|---|---|---|---|---|---|---|---|
| | | | | | | | | | | | |

## Per-class results

Add one block per run. A good overall score can hide a weak class.

| Run name | Class | Precision | Recall | AP@50 | AP@50-95 |
|---|---|---|---|---|---|
| | paper | | | | |
| | plastic | | | | |
| | metal | | | | |
| | organic | | | | |

## Notes per run

For each run, write down what it gets wrong: which classes it confuses, and which photos it fails on (small items, overlap, poor light, transparent plastic).

## Rules

- Scores from `train.py` are **validation** scores. Use them to compare runs and choose settings.
- The **test** score comes from `python scripts/evaluate.py --split test`. Run it once, on the final model, after the confidence threshold is chosen.
- Never report a training-split score as the model's performance.

## Pipeline check with fake data (not a model result)

On 2026-11-14 the scripts were run end to end on a synthetic dataset of coloured rectangles (`ai-model/tests/make_synthetic_dataset.py`), on a CPU, to prove that they work. That model scored about 0.99 mAP@50 because telling four solid colours apart is trivial. The number says nothing about waste detection and must not be quoted as a result.
