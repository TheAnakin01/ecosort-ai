"""Score trained weights on one split of the dataset.

Run from the ai-model/ folder:

    python scripts/evaluate.py                 # validation split
    python scripts/evaluate.py --split test    # final score, run once at the end

Use the validation split while choosing settings such as the confidence
threshold. The test split is the honest final score, so look at it only once
the model and settings are fixed.
"""

import argparse
import json
from datetime import datetime, timezone
from pathlib import Path

import ultralytics
from ultralytics import YOLO

from dataset_paths import absolute_data_yaml, data_root  # noqa: E402
from train import AI_MODEL_DIR, overall_metrics, per_class_rows, print_metrics


def main() -> None:
    parser = argparse.ArgumentParser(description="Evaluate EcoSort detector weights")
    parser.add_argument("--weights", type=Path, default=data_root() / "weights" / "best.pt")
    parser.add_argument("--data", type=Path, default=AI_MODEL_DIR / "configs" / "data.yaml")
    parser.add_argument("--split", choices=["val", "test"], default="val")
    parser.add_argument("--imgsz", type=int, default=640)
    parser.add_argument("--out", type=Path, help="where to save the results as JSON")
    args = parser.parse_args()

    if not args.weights.exists():
        raise SystemExit(f"{args.weights} not found. Train a model first, or pass --weights.")

    model = YOLO(str(args.weights))
    data = str(absolute_data_yaml(args.data))
    metrics = model.val(data=data, split=args.split, imgsz=args.imgsz, plots=False, verbose=False)
    overall, rows = overall_metrics(metrics), per_class_rows(metrics)
    print_metrics("validation" if args.split == "val" else "test", overall, rows)

    speed = {stage: round(float(ms), 2) for stage, ms in metrics.speed.items()}
    print(f"\nTime per image (ms): {speed}")

    out = args.out or args.weights.with_name(f"{args.weights.stem}_{args.split}_metrics.json")
    out.write_text(
        json.dumps(
            {
                "evaluated": datetime.now(timezone.utc).isoformat(timespec="seconds"),
                "weights": str(args.weights),
                "split": args.split,
                "image_size": args.imgsz,
                "ultralytics_version": ultralytics.__version__,
                "overall": overall,
                "per_class": rows,
                "ms_per_image": speed,
            },
            indent=2,
        )
        + "\n"
    )
    print(f"Saved: {out}")


if __name__ == "__main__":
    main()
