"""Check a finished training run for overtraining. Needs no PyTorch.

Reads the run's results.csv, which Ultralytics writes after every epoch, and
answers three questions:

- Which epoch scored best on the validation split? best.pt is that epoch.
- Did validation loss start rising while training loss kept falling? That is
  the sign of overtraining: the model memorising the training photos.
- Was the model still improving when training stopped? Then a longer run may help.

Run from the ai-model/ folder on any finished run, old or new:

    python scripts/overfit_check.py /content/drive/MyDrive/ecosort/runs/ecosort-baseline-2

train.py runs this check by itself at the end of training.
"""

import argparse
import csv
import json
from pathlib import Path

MAP_COLUMN = "metrics/mAP50-95(B)"
# Validation loss must rise at least this much above its lowest value to count.
LOSS_RISE = 0.03
# A gain smaller than this over the last epochs counts as no gain.
MIN_GAIN = 0.003
RECENT = 5  # how many final epochs to look at


def read_results(results_csv: Path) -> list[dict[str, float]]:
    with results_csv.open(newline="") as f:
        rows = [{key.strip(): float(value) for key, value in row.items() if value.strip()} for row in csv.DictReader(f)]
    if not rows:
        raise SystemExit(f"{results_csv} has no epochs in it.")
    if MAP_COLUMN not in rows[0]:
        raise SystemExit(f"{results_csv} has no {MAP_COLUMN} column. Is this a detection run?")
    return rows


def total_loss(row: dict[str, float], prefix: str) -> float:
    return sum(value for key, value in row.items() if key.startswith(prefix) and key.endswith("_loss"))


def check(rows: list[dict[str, float]]) -> dict:
    """Judge one run. rows is results.csv, one dict per epoch, in order."""
    scores = [row[MAP_COLUMN] for row in rows]
    val_loss = [total_loss(row, "val/") for row in rows]
    train_loss = [total_loss(row, "train/") for row in rows]
    epochs = len(rows)

    best = max(range(epochs), key=lambda i: scores[i])
    lowest_val = min(range(epochs), key=lambda i: val_loss[i])
    val_rise = (val_loss[-1] - val_loss[lowest_val]) / val_loss[lowest_val] if val_loss[lowest_val] else 0.0
    train_fell = train_loss[-1] < train_loss[lowest_val]
    window_start = max(0, epochs - 1 - RECENT)
    recent_gain = scores[-1] - scores[window_start]

    if lowest_val < epochs - 1 and val_rise >= LOSS_RISE and train_fell:
        verdict = "overtraining"
        advice = (
            f"Validation loss is {val_rise:.0%} above its lowest point (epoch {lowest_val + 1}) while training "
            "loss kept falling. best.pt is still the best epoch, but more epochs will not help. "
            "Next time train fewer epochs, or lower --patience."
        )
    elif best >= epochs - 2 and recent_gain > MIN_GAIN:
        verdict = "still improving"
        advice = (
            f"mAP@50-95 rose {recent_gain:.3f} over the last {epochs - 1 - window_start} epochs and the best "
            "epoch is one of the "
            "last two. A longer run would probably gain a little."
        )
    else:
        verdict = "levelled off"
        advice = "Scores stopped improving and validation loss did not rise. The epoch count was about right."

    return {
        "epochs_run": epochs,
        "best_epoch": best + 1,
        "best_map50_95": round(scores[best], 4),
        "last_map50_95": round(scores[-1], 4),
        "lowest_val_loss_epoch": lowest_val + 1,
        "val_loss_rise_since_lowest": round(val_rise, 4),
        "train_loss_fell_since_then": train_fell,
        "verdict": verdict,
        "advice": advice,
    }


def print_report(report: dict) -> None:
    print("\nOvertraining check")
    print(f"  Epochs run:            {report['epochs_run']}")
    print(f"  Best epoch (best.pt):  {report['best_epoch']}  (mAP@50-95 {report['best_map50_95']:.3f})")
    print(f"  Lowest val loss at:    epoch {report['lowest_val_loss_epoch']}")
    print(f"  Verdict:               {report['verdict'].upper()}")
    print(f"  {report['advice']}")


def main() -> None:
    parser = argparse.ArgumentParser(description="Check a training run for overtraining")
    parser.add_argument("run", type=Path, help="run folder (the one with results.csv in it)")
    args = parser.parse_args()
    results = args.run / "results.csv"
    if not results.exists():
        raise SystemExit(f"{results} not found.")
    report = check(read_results(results))
    print_report(report)
    (args.run / "overfit_check.json").write_text(json.dumps(report, indent=2) + "\n")


if __name__ == "__main__":
    main()
