"""Fine-tune a pretrained YOLO nano detector on the 4-class waste dataset.

Run from the ai-model/ folder (Colab or a laptop with a GPU), after
prepare_dataset.py and validate_dataset.py:

    python scripts/train.py --epochs 50

The best checkpoint is saved to <run folder>/weights/best.pt, chosen on the
validation split. Copy it to ai-model/weights/best.pt so the backend can load it.

This script never touches the test split. Score the final model on it once,
with scripts/evaluate.py --split test, after all tuning is done.
"""

import argparse
import json
from datetime import datetime, timezone
from pathlib import Path

import torch
import ultralytics
import yaml
from ultralytics import YOLO

AI_MODEL_DIR = Path(__file__).resolve().parent.parent


def dataset_dir(data_yaml: Path) -> Path:
    """The dataset folder a data.yaml points at."""
    path = Path(yaml.safe_load(data_yaml.read_text())["path"])
    return path if path.is_absolute() else (data_yaml.parent / path).resolve()


def require_validated(dataset: Path) -> dict:
    """Stop unless validate_dataset.py has passed on this dataset."""
    report_path = dataset / "validation_report.json"
    if not report_path.exists():
        raise SystemExit(
            f"{report_path} not found. Run scripts/validate_dataset.py first, "
            "or pass --skip-validation-check to train anyway."
        )
    report = json.loads(report_path.read_text())
    if not report.get("passed"):
        raise SystemExit(
            "The dataset has validation errors. Fix them and run scripts/validate_dataset.py again, "
            "or pass --skip-validation-check to train anyway."
        )
    return report


def per_class_rows(metrics) -> list[dict]:
    """Precision, recall and AP for each class that has validation boxes."""
    rows = []
    for position, class_id in enumerate(metrics.box.ap_class_index):
        precision, recall, ap50, ap = metrics.box.class_result(position)
        rows.append(
            {
                "class": metrics.names[int(class_id)],
                "precision": round(float(precision), 4),
                "recall": round(float(recall), 4),
                "ap50": round(float(ap50), 4),
                "ap50_95": round(float(ap), 4),
            }
        )
    return rows


def print_metrics(split: str, overall: dict, rows: list[dict]) -> None:
    print(f"\nResults on the {split} split")
    print(f"{'class':10s} {'precision':>9s} {'recall':>7s} {'AP@50':>7s} {'AP@50-95':>9s}")
    for row in rows:
        print(
            f"{row['class']:10s} {row['precision']:9.3f} {row['recall']:7.3f} "
            f"{row['ap50']:7.3f} {row['ap50_95']:9.3f}"
        )
    print(
        f"{'all':10s} {overall['precision']:9.3f} {overall['recall']:7.3f} "
        f"{overall['map50']:7.3f} {overall['map50_95']:9.3f}"
    )


def overall_metrics(metrics) -> dict:
    return {
        "precision": round(float(metrics.box.mp), 4),
        "recall": round(float(metrics.box.mr), 4),
        "map50": round(float(metrics.box.map50), 4),
        "map50_95": round(float(metrics.box.map), 4),
    }


def main() -> None:
    parser = argparse.ArgumentParser(description="Train the EcoSort detector")
    parser.add_argument("--model", default="yolo11n.pt", help="pretrained YOLO nano weights to start from")
    parser.add_argument("--data", type=Path, default=AI_MODEL_DIR / "configs" / "data.yaml")
    parser.add_argument("--epochs", type=int, default=50)
    parser.add_argument("--imgsz", type=int, default=640)
    parser.add_argument("--batch", type=int, default=16)
    parser.add_argument("--seed", type=int, default=0, help="random seed, recorded so a run can be repeated")
    parser.add_argument("--name", default="ecosort-baseline", help="name of this training run")
    parser.add_argument("--project", default=str(AI_MODEL_DIR / "runs"), help="folder to save runs in")
    parser.add_argument(
        "--skip-validation-check",
        action="store_true",
        help="train even if validate_dataset.py has not passed on the dataset",
    )
    args = parser.parse_args()

    dataset = dataset_dir(args.data)
    validation = None if args.skip_validation_check else require_validated(dataset)

    # Transfer learning: start from weights that already know general shapes
    # and edges, then teach them our four waste classes.
    model = YOLO(args.model)
    model.train(
        data=str(args.data),
        epochs=args.epochs,
        imgsz=args.imgsz,
        batch=args.batch,
        seed=args.seed,
        name=args.name,
        project=args.project,
        patience=15,  # stop early if validation stops improving
    )
    run_dir = Path(model.trainer.save_dir)

    # Score the best checkpoint on the validation split.
    best = YOLO(str(run_dir / "weights" / "best.pt"))
    metrics = best.val(data=str(args.data), split="val", imgsz=args.imgsz, plots=False, verbose=False)
    overall, rows = overall_metrics(metrics), per_class_rows(metrics)
    print_metrics("validation", overall, rows)

    # Everything needed to repeat or describe this run.
    build_record = dataset / "dataset_report.json"
    run_info = {
        "finished": datetime.now(timezone.utc).isoformat(timespec="seconds"),
        "run_name": args.name,
        "starting_weights": args.model,
        "epochs_requested": args.epochs,
        "image_size": args.imgsz,
        "batch_size": args.batch,
        "seed": args.seed,
        "ultralytics_version": ultralytics.__version__,
        "torch_version": torch.__version__,
        "device": "cuda" if torch.cuda.is_available() else "cpu",
        "dataset": str(dataset),
        "dataset_built": json.loads(build_record.read_text()).get("created") if build_record.exists() else None,
        "dataset_validated": validation is not None,
        "validation_metrics": {"overall": overall, "per_class": rows},
    }
    (run_dir / "run_info.json").write_text(json.dumps(run_info, indent=2) + "\n")

    print(f"\nBest model: {run_dir / 'weights' / 'best.pt'}")
    print(f"Run record: {run_dir / 'run_info.json'}")
    print("Copy the numbers above into docs/training-log.md.")
    print("These are validation scores. Use scripts/evaluate.py --split test once, at the very end.")


if __name__ == "__main__":
    main()
