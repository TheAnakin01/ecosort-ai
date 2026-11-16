"""Make a validation set that two models have both never trained on.

Comparing two models is only fair on photos neither of them saw in training.
Run 2's validation photos were never in run 2's training set, but some of them
may have been in run 1's: adding a dataset regroups look-alike photos, and a
regrouped photo can change split.

This takes the validation split of one dataset build and leaves out every
photo that is in the training split of another build (matched by file name,
which prepare_dataset.py derives from the source and the original name). The
result is a small dataset folder, with links to the images, that evaluate.py
and check_hallucinations.py can use through --data.

Run from the ai-model/ folder:

    python scripts/make_comparison_split.py \\
        --val-from datasets/ecosort --exclude-train-of datasets/run1-split --out datasets/compare
"""

import argparse
import json
import os
from pathlib import Path

import yaml

AI_MODEL_DIR = Path(__file__).resolve().parent.parent
IMAGE_SUFFIXES = {".jpg", ".jpeg", ".png", ".bmp", ".webp"}


def stems(folder: Path) -> set[str]:
    if not folder.is_dir():
        return set()
    return {p.stem for p in folder.iterdir() if p.suffix.lower() in IMAGE_SUFFIXES}


def make_split(val_from: Path, exclude_train_of: Path, out: Path, class_names: list[str]) -> dict:
    val_images = val_from / "images" / "val"
    if not val_images.is_dir():
        raise SystemExit(f"{val_images} not found. Build the dataset first.")
    seen_in_training = stems(exclude_train_of / "images" / "train")
    if not seen_in_training:
        raise SystemExit(f"{exclude_train_of / 'images' / 'train'} has no images. Build that split first.")

    for kind in ("images", "labels"):
        (out / kind / "val").mkdir(parents=True, exist_ok=True)
    kept = left_out = 0
    for image in sorted(val_images.iterdir()):
        if image.suffix.lower() not in IMAGE_SUFFIXES:
            continue
        if image.stem in seen_in_training:
            left_out += 1
            continue
        label = val_from / "labels" / "val" / f"{image.stem}.txt"
        for source, target in (
            (image, out / "images" / "val" / image.name),
            (label, out / "labels" / "val" / label.name),
        ):
            if source.exists() and not target.exists():
                os.symlink(source.resolve(), target)
        kept += 1

    # evaluate.py asks Ultralytics for the "val" split; train must exist too, so it points at the same folder.
    (out / "data.yaml").write_text(
        yaml.safe_dump(
            {
                "path": str(out.resolve()),
                "train": "images/val",
                "val": "images/val",
                "names": dict(enumerate(class_names)),
            },
            sort_keys=False,
        )
    )
    summary = {
        "val_from": str(val_from),
        "excluded_training_photos_of": str(exclude_train_of),
        "validation_photos": kept + left_out,
        "left_out_seen_in_training": left_out,
        "kept": kept,
    }
    (out / "comparison_split.json").write_text(json.dumps(summary, indent=2) + "\n")
    return summary


def main() -> None:
    parser = argparse.ArgumentParser(description="Validation photos that neither model trained on")
    parser.add_argument("--val-from", type=Path, required=True, help="dataset build whose validation split is used")
    parser.add_argument(
        "--exclude-train-of", type=Path, required=True, help="dataset build whose training photos are left out"
    )
    parser.add_argument("--out", type=Path, required=True)
    parser.add_argument("--data", type=Path, default=AI_MODEL_DIR / "configs" / "data.yaml", help="for the class names")
    args = parser.parse_args()

    names = yaml.safe_load(args.data.read_text())["names"]
    class_names = list(names.values()) if isinstance(names, dict) else list(names)
    summary = make_split(args.val_from, args.exclude_train_of, args.out, class_names)
    print(
        f"{summary['validation_photos']} validation photos; left out {summary['left_out_seen_in_training']} "
        f"that the other model trained on; {summary['kept']} kept."
    )
    print("Use with: --data", args.out / "data.yaml")


if __name__ == "__main__":
    main()
