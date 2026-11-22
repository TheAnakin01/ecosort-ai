"""Fine-tune a pretrained YOLO nano detector on the 4-class waste dataset.

Run from the ai-model/ folder (Colab or a laptop with a GPU), after
prepare_dataset.py and validate_dataset.py:

    python scripts/train.py --epochs 50
    python scripts/train.py --resume --epochs 60   # resume from last.pt

The best checkpoint is saved to <run folder>/weights/best.pt, chosen on the
validation split. Copy it to ai-model/weights/best.pt so the backend can load it.

This script never touches the test split. Score the final model on it once,
with scripts/evaluate.py --split test, after all tuning is done.
"""

import argparse
import hashlib
import json
from datetime import datetime, timezone
from pathlib import Path

import torch
import ultralytics
from ultralytics import YOLO

from dataset_paths import AI_MODEL_DIR, absolute_data_yaml, data_root, dataset_dir
from overfit_check import check as check_overtraining
from overfit_check import print_report as print_overtraining_report
from overfit_check import read_results


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


def compute_sha256(path: Path) -> str:
    """Compute SHA-256 hash of a file for provenance tracking."""
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(8192), b""):
            h.update(chunk)
    return h.hexdigest()


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
    parser.add_argument(
        "--resume",
        action="store_true",
        help="resume training from last.pt using Ultralytics resume=True",
    )
    parser.add_argument("--data", type=Path, default=AI_MODEL_DIR / "configs" / "data.yaml")
    parser.add_argument("--epochs", type=int, default=60)
    parser.add_argument("--imgsz", type=int, default=640)
    parser.add_argument("--batch", type=int, default=8)
    parser.add_argument(
        "--patience",
        type=int,
        default=10,
        help="stop when validation mAP has not improved for this many epochs, so the model does not overtrain",
    )
    parser.add_argument("--seed", type=int, default=0, help="random seed, recorded so a run can be repeated")
    parser.add_argument("--name", default="ecosort-baseline", help="name of this training run")
    parser.add_argument("--project", default=str(data_root() / "runs"), help="folder to save runs in")
    parser.add_argument(
        "--skip-validation-check",
        action="store_true",
        help="train even if validate_dataset.py has not passed on the dataset",
    )
    parser.add_argument(
        "--device",
        type=int,
        default=0,
        help="CUDA device index (0 for single GPU). Only one GPU is used.",
    )
    args = parser.parse_args()

    # Verify CUDA is available before training
    if not torch.cuda.is_available():
        raise SystemExit("CUDA is not available. Training requires a GPU.")

    device_name = torch.cuda.get_device_name(args.device)
    print("CUDA available: True")
    print(f"GPU device {args.device}: {device_name}")
    print(f"GPU memory: {torch.cuda.get_device_properties(args.device).total_memory / 1e9:.1f} GB")

    dataset = dataset_dir(args.data)
    data = str(absolute_data_yaml(args.data))
    validation = None if args.skip_validation_check else require_validated(dataset)

    # Determine starting checkpoint based on execution mode
    if args.resume:
        resume_ckpt = Path(args.model)
        if not resume_ckpt.exists():
            raise SystemExit(
                f"Resume mode requested but checkpoint not found: {resume_ckpt}\n"
                f"Run an initial training first, or provide a valid checkpoint path with --model."
            )
        print("\n=== RESUME RUN: Continuing from last checkpoint ===")
        print(f"Resume checkpoint: {resume_ckpt}")
        print(f"Checkpoint SHA-256: {compute_sha256(resume_ckpt)}")
        # Ultralytics resume=True restores optimizer state, epoch progress,
        # and original training arguments from the checkpoint.
        model = YOLO(str(resume_ckpt))
        model.train(
            resume=True,
            data=data,
            epochs=args.epochs,
            imgsz=args.imgsz,
            batch=args.batch,
            seed=args.seed,
            name=args.name,
            project=args.project,
            patience=args.patience,
            device=args.device,
        )
    else:
        # Initial run: start from the provided checkpoint (e.g., original best.pt)
        start_ckpt = Path(args.model)
        if not start_ckpt.exists():
            raise SystemExit(
                f"Starting checkpoint not found: {start_ckpt}\n"
                f"Provide a valid checkpoint path with --model."
            )
        print("\n=== INITIAL RUN: Starting from original checkpoint ===")
        print(f"Source checkpoint: {start_ckpt}")
        print(f"Checkpoint SHA-256: {compute_sha256(start_ckpt)}")
        model = YOLO(str(start_ckpt))
        model.train(
            data=data,
            epochs=args.epochs,
            imgsz=args.imgsz,
            batch=args.batch,
            seed=args.seed,
            name=args.name,
            project=args.project,
            patience=args.patience,  # stop early once validation stops improving
            device=args.device,
        )
    run_dir = Path(model.trainer.save_dir)

    # Score the best checkpoint on the validation split.
    best = YOLO(str(run_dir / "weights" / "best.pt"))
    metrics = best.val(data=data, split="val", imgsz=args.imgsz, plots=False, verbose=False)
    overall, rows = overall_metrics(metrics), per_class_rows(metrics)
    print_metrics("validation", overall, rows)
    overtraining = check_overtraining(read_results(run_dir / "results.csv"))
    print_overtraining_report(overtraining)

    # Everything needed to repeat or describe this run.
    build_record = dataset / "dataset_report.json"
    run_info = {
        "finished": datetime.now(timezone.utc).isoformat(timespec="seconds"),
        # The folder name, which gets a number added when the name is already taken.
        "run_name": run_dir.name,
        "starting_weights": args.model,
        "execution_mode": "resume" if args.resume else "initial",
        "epochs_requested": args.epochs,
        "patience": args.patience,
        "image_size": args.imgsz,
        "batch_size": args.batch,
        "seed": args.seed,
        "device": args.device,
        "ultralytics_version": ultralytics.__version__,
        "torch_version": torch.__version__,
        "cuda_device": device_name,
        "dataset": str(dataset),
        "dataset_built": json.loads(build_record.read_text()).get("created") if build_record.exists() else None,
        "dataset_validated": validation is not None,
        "validation_metrics": {"overall": overall, "per_class": rows},
        "overtraining_check": overtraining,
    }
    (run_dir / "run_info.json").write_text(json.dumps(run_info, indent=2) + "\n")

    print(f"\nBest model: {run_dir / 'weights' / 'best.pt'}")
    print(f"Run record: {run_dir / 'run_info.json'}")
    print("Copy the numbers above into docs/training-log.md.")
    print("These are validation scores. Use scripts/evaluate.py --split test once, at the very end.")
    print("Next: python scripts/check_hallucinations.py --weights " + str(run_dir / "weights" / "best.pt"))


if __name__ == "__main__":
    main()