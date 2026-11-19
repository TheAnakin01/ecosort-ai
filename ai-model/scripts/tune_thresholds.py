"""Pick the backend's confidence thresholds from the validation split.

The backend has two settings that decide what the app shows:

- CONFIDENCE_THRESHOLD: boxes below it are not shown at all.
- LOW_CONFIDENCE_THRESHOLD: boxes below it are shown but marked "uncertain".

Both were first guesses (0.35 and 0.5). This script runs the model once at a
very low confidence, then for each candidate threshold counts what the app
would show, using the same matching rules as check_hallucinations.py:

- precision: share of shown boxes that are on a labelled item with the right class
- recall:    share of labelled items that got a correct box
- F1:        the balance of the two
- on nothing: share of shown boxes with no labelled item there (hallucinations)

It recommends:
- CONFIDENCE_THRESHOLD: the threshold with the best F1 among those whose
  "on nothing" share is at most --max-on-nothing (default 5%).
- LOW_CONFIDENCE_THRESHOLD: the lowest threshold at or above that one where
  the boxes shown are at least --sure-precision correct (default 85%).

Validation split only: choosing thresholds on the test split would make the
final test score optimistic. Run from the ai-model/ folder:

    python scripts/tune_thresholds.py --weights weights/best.pt

The result is a recommendation. Set the values in the backend (or render.yaml)
by hand and record them in docs/training-log.md.
"""

import argparse
import json
from datetime import datetime, timezone
from pathlib import Path

from check_hallucinations import IMAGE_SUFFIXES, match_image, read_labels
from dataset_paths import data_root, dataset_dir  # noqa: E402

AI_MODEL_DIR = Path(__file__).resolve().parent.parent
MIN_BOXES = 200  # fewer shown boxes than this and the numbers are noise
DEFAULT_GRID = [round(0.05 * i, 2) for i in range(2, 17)]  # 0.10 .. 0.80

# (class, confidence, box as fractions)
Prediction = tuple[int, float, tuple[float, float, float, float]]


def score_at(images: list[tuple[list[Prediction], list]], threshold: float) -> dict:
    """What the app would show at this threshold, over all images."""
    shown = correct = on_nothing = labelled = 0
    for predictions, labels in images:
        kept = [p for p in predictions if p[1] >= threshold]
        outcomes, _ = match_image(kept, labels)
        shown += len(kept)
        correct += outcomes.count("correct")
        on_nothing += outcomes.count("on nothing")
        labelled += len(labels)
    precision = correct / shown if shown else 0.0
    recall = correct / labelled if labelled else 0.0
    f1 = 2 * precision * recall / (precision + recall) if precision + recall else 0.0
    return {
        "threshold": threshold,
        "shown": shown,
        "correct": correct,
        "precision": round(precision, 4),
        "recall": round(recall, 4),
        "f1": round(f1, 4),
        "share_on_nothing": round(on_nothing / shown, 4) if shown else 0.0,
    }


def recommend(rows: list[dict], max_on_nothing: float, sure_precision: float) -> dict:
    """Choose the two thresholds from a sweep (rows sorted by threshold)."""
    allowed = [r for r in rows if r["shown"] and r["share_on_nothing"] <= max_on_nothing]
    note = None
    if not allowed:
        allowed = [r for r in rows if r["shown"]]
        note = f"no threshold keeps boxes on nothing at or below {max_on_nothing:.0%}; chose best F1 regardless"
    if not allowed:
        return {"confidence_threshold": None, "low_confidence_threshold": None, "note": "the model showed no boxes"}
    best = max(allowed, key=lambda r: (r["f1"], -r["threshold"]))
    sure = next(
        (r for r in rows if r["threshold"] >= best["threshold"] and r["shown"] and r["precision"] >= sure_precision),
        None,
    )
    low = sure["threshold"] if sure else rows[-1]["threshold"]
    if sure is None:
        extra = f"no threshold reaches {sure_precision:.0%} precision; LOW_CONFIDENCE set to the highest tried"
        note = f"{note}; {extra}" if note else extra
    if best["shown"] < MIN_BOXES:
        extra = f"only {best['shown']} boxes shown at the chosen threshold; too few to trust, use the full split"
        note = f"{note}; {extra}" if note else extra
    return {
        "confidence_threshold": best["threshold"],
        "low_confidence_threshold": max(low, best["threshold"]),
        "note": note,
    }


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--weights", type=Path, default=data_root() / "weights" / "best.pt")
    parser.add_argument("--data", type=Path, default=AI_MODEL_DIR / "configs" / "data.yaml")
    parser.add_argument("--iou", type=float, default=0.7, help="the backend's IOU_THRESHOLD")
    parser.add_argument("--imgsz", type=int, default=640)
    parser.add_argument("--limit", type=int, help="use only the first N images, for a quick look")
    parser.add_argument("--max-on-nothing", type=float, default=0.05)
    parser.add_argument("--sure-precision", type=float, default=0.85)
    parser.add_argument("--out", type=Path, help="where to write the JSON report")
    args = parser.parse_args()

    if not args.weights.exists():
        raise SystemExit(f"{args.weights} not found. Pass --weights.")
    dataset = dataset_dir(args.data)
    image_dir, label_dir = dataset / "images" / "val", dataset / "labels" / "val"
    if not image_dir.is_dir():
        raise SystemExit(f"{image_dir} not found. Run scripts/prepare_dataset.py first.")
    paths = sorted(p for p in image_dir.iterdir() if p.suffix.lower() in IMAGE_SUFFIXES)[: args.limit]

    from ultralytics import YOLO  # works with .pt and .onnx; imported late so tests need no PyTorch

    model = YOLO(str(args.weights), task="detect")
    lowest = min(DEFAULT_GRID)
    images = []
    print(f"Running the model on {len(paths)} validation images...", flush=True)
    for start in range(0, len(paths), 32):
        batch = paths[start : start + 32]
        results = model.predict([str(p) for p in batch], conf=lowest, iou=args.iou, imgsz=args.imgsz, verbose=False)
        for path, result in zip(batch, results, strict=True):
            predictions = [
                (int(c), float(s), tuple(b))
                for c, s, b in zip(
                    result.boxes.cls.tolist(), result.boxes.conf.tolist(), result.boxes.xyxyn.tolist(), strict=True
                )
            ]
            images.append((predictions, read_labels(label_dir / (path.stem + ".txt"))))

    rows = [score_at(images, t) for t in DEFAULT_GRID]
    choice = recommend(rows, args.max_on_nothing, args.sure_precision)

    print(f"\n{'conf':>5s} {'shown':>7s} {'precision':>9s} {'recall':>7s} {'F1':>6s} {'on nothing':>10s}")
    for r in rows:
        mark = " <" if r["threshold"] == choice["confidence_threshold"] else ""
        print(
            f"{r['threshold']:5.2f} {r['shown']:7d} {r['precision']:9.3f} {r['recall']:7.3f} "
            f"{r['f1']:6.3f} {r['share_on_nothing']:10.1%}{mark}"
        )
    print(f"\nRecommended CONFIDENCE_THRESHOLD={choice['confidence_threshold']}")
    print(f"Recommended LOW_CONFIDENCE_THRESHOLD={choice['low_confidence_threshold']}")
    if choice["note"]:
        print(f"Note: {choice['note']}")

    out = args.out or args.weights.parent / "threshold_tuning.json"
    report = {
        "checked": datetime.now(timezone.utc).isoformat(timespec="seconds"),
        "weights": str(args.weights),
        "split": "val",
        "images": len(images),
        "iou": args.iou,
        "image_size": args.imgsz,
        "max_on_nothing": args.max_on_nothing,
        "sure_precision": args.sure_precision,
        "sweep": rows,
        "recommendation": choice,
    }
    out.write_text(json.dumps(report, indent=2) + "\n")
    print(f"Report: {out}")


if __name__ == "__main__":
    main()
