"""Check a prepared EcoSort dataset before training on it.

Run from the ai-model/ folder, after prepare_dataset.py:

    python scripts/validate_dataset.py
    python scripts/validate_dataset.py datasets/ecosort --report validation_report.json

Problems are split into two kinds:

  ERROR    the dataset must be fixed before training (the script exits with 1)
  WARNING  worth a look, but training can go ahead

What it checks:
  - every image opens, and every image has a label file (and the reverse)
  - every label line is a valid box: known class, numbers in range, real size
  - the same picture is not in two splits (that would inflate test scores)
  - augmented copies of one Roboflow photo are not spread across splits
  - how many images and boxes each class has in each split
"""

import argparse
import hashlib
import json
import sys
from collections import Counter, defaultdict
from pathlib import Path

from PIL import Image

from prepare_dataset import IMAGE_SUFFIXES, MIN_BOX_SIDE, OUR_CLASSES, source_key

AI_MODEL_DIR = Path(__file__).resolve().parent.parent
SPLITS = ["train", "val", "test"]
# A box may stick out of the image by this much before it counts as an error.
EDGE_TOLERANCE = 1e-3
# A class with less than this share of all boxes is flagged as under-represented.
MIN_CLASS_SHARE = 0.10
MAX_LISTED = 10


class Findings:
    """Collects errors and warnings, grouped by kind."""

    def __init__(self) -> None:
        self.errors: dict[str, list[str]] = defaultdict(list)
        self.warnings: dict[str, list[str]] = defaultdict(list)

    def error(self, kind: str, detail: str) -> None:
        self.errors[kind].append(detail)

    def warn(self, kind: str, detail: str) -> None:
        self.warnings[kind].append(detail)


def check_label_line(line: str) -> str | None:
    """Return what is wrong with one label line, or None if it is a valid box."""
    parts = line.split()
    if len(parts) != 5:
        return f"expected 5 values, found {len(parts)}"
    try:
        class_id = int(parts[0])
        cx, cy, w, h = (float(v) for v in parts[1:])
    except ValueError:
        return "contains something that is not a number"
    if not 0 <= class_id < len(OUR_CLASSES):
        return f"class id {class_id} is not one of 0-{len(OUR_CLASSES) - 1}"
    if w <= MIN_BOX_SIDE or h <= MIN_BOX_SIDE:
        return "box has no width or height"
    edges = (cx - w / 2, cy - h / 2, cx + w / 2, cy + h / 2)
    if min(edges) < -EDGE_TOLERANCE or max(edges) > 1 + EDGE_TOLERANCE:
        return "box reaches outside the image"
    return None


def visual_hash(path: Path) -> str:
    """A fingerprint that stays the same when a picture is re-saved or resized."""
    with Image.open(path) as image:
        small = image.convert("L").resize((9, 8), Image.Resampling.LANCZOS)
        pixels = small.tobytes()  # one byte per pixel, row by row
    bits = 0
    for row in range(8):
        for col in range(8):
            bits = (bits << 1) | (pixels[row * 9 + col] > pixels[row * 9 + col + 1])
    return f"{bits:016x}"


def is_readable(path: Path) -> bool:
    try:
        with Image.open(path) as image:
            image.verify()
        return True
    except Exception:
        return False


def validate(dataset: Path) -> tuple[Findings, dict]:
    findings = Findings()
    stats = {
        "images_per_split": {},
        "boxes_per_class_by_split": {},
        "background_images_per_split": {},
    }
    # fingerprint or source name -> {split: [file names]}
    by_bytes: dict[str, dict[str, list[str]]] = defaultdict(lambda: defaultdict(list))
    by_look: dict[str, dict[str, list[str]]] = defaultdict(lambda: defaultdict(list))
    by_source: dict[str, dict[str, list[str]]] = defaultdict(lambda: defaultdict(list))

    for split in SPLITS:
        image_dir = dataset / "images" / split
        label_dir = dataset / "labels" / split
        if not image_dir.is_dir():
            findings.error("Missing split", f"images/{split} does not exist")
            continue

        images = sorted(p for p in image_dir.iterdir() if p.suffix.lower() in IMAGE_SUFFIXES)
        image_stems = {p.stem for p in images}
        box_counts: Counter[str] = Counter()
        background = 0

        if label_dir.is_dir():
            for label in sorted(label_dir.glob("*.txt")):
                if label.stem not in image_stems:
                    findings.error("Label file without an image", f"labels/{split}/{label.name}")

        for image in images:
            name = f"{split}/{image.name}"
            if not is_readable(image):
                findings.error("Unreadable image", name)
                continue

            by_bytes[hashlib.md5(image.read_bytes()).hexdigest()][split].append(image.name)
            by_look[visual_hash(image)][split].append(image.name)
            by_source[source_key(image.name)][split].append(image.name)

            label = label_dir / (image.stem + ".txt")
            if not label.exists():
                findings.error("Image without a label file", name)
                continue
            lines = [ln for ln in label.read_text().splitlines() if ln.strip()]
            if not lines:
                background += 1
            if len(set(lines)) != len(lines):
                findings.warn("Same box listed twice", name)
            for number, line in enumerate(lines, start=1):
                problem = check_label_line(line)
                if problem:
                    findings.error("Invalid box", f"{name}, line {number}: {problem}")
                else:
                    box_counts[OUR_CLASSES[int(line.split()[0])]] += 1

        stats["images_per_split"][split] = len(images)
        stats["boxes_per_class_by_split"][split] = {name: box_counts[name] for name in OUR_CLASSES}
        stats["background_images_per_split"][split] = background
        if not images:
            findings.error("Empty split", f"images/{split} has no images")

    def across_splits(groups: dict[str, dict[str, list[str]]]) -> list[str]:
        found = []
        for splits in groups.values():
            if len(splits) > 1:
                found.append("; ".join(f"{split}/{names[0]}" for split, names in sorted(splits.items())))
        return found

    exact = across_splits(by_bytes)
    for detail in exact:
        findings.error("Same image file in more than one split", detail)
    for detail in across_splits(by_source):
        if detail not in exact:
            findings.error("Copies of one source photo in more than one split", detail)
    for detail in across_splits(by_look):
        if detail not in exact:
            findings.warn("Pictures that look identical in more than one split", detail)
    for splits in by_bytes.values():
        for split, names in splits.items():
            if len(names) > 1:
                findings.warn("Same image file more than once in a split", f"{split}/{names[0]} (x{len(names)})")

    totals = Counter()
    for counts in stats["boxes_per_class_by_split"].values():
        totals.update(counts)
    stats["boxes_per_class"] = {name: totals[name] for name in OUR_CLASSES}
    all_boxes = sum(totals.values())
    for name in OUR_CLASSES:
        if all_boxes and totals[name] == 0:
            findings.error("Class with no boxes", name)
        elif all_boxes and totals[name] / all_boxes < MIN_CLASS_SHARE:
            findings.warn("Under-represented class", f"{name}: {totals[name]} of {all_boxes} boxes")
    for split in ("val", "test"):
        for name, count in stats["boxes_per_class_by_split"].get(split, {}).items():
            if count == 0 and totals[name] > 0:
                findings.warn("Class missing from a split", f"{name} has no boxes in {split}")

    return findings, stats


def print_group(title: str, groups: dict[str, list[str]]) -> None:
    for kind, details in groups.items():
        print(f"\n{title}: {kind} ({len(details)})")
        for detail in details[:MAX_LISTED]:
            print(f"  {detail}")
        if len(details) > MAX_LISTED:
            print(f"  ... and {len(details) - MAX_LISTED} more (see the report file)")


def main() -> None:
    parser = argparse.ArgumentParser(description="Validate a prepared EcoSort dataset")
    parser.add_argument("dataset", nargs="?", type=Path, default=AI_MODEL_DIR / "datasets" / "ecosort")
    parser.add_argument("--report", type=Path, help="where to save the full report (default: inside the dataset)")
    args = parser.parse_args()

    if not args.dataset.is_dir():
        raise SystemExit(f"{args.dataset} does not exist. Run prepare_dataset.py first.")

    findings, stats = validate(args.dataset)

    print(f"Dataset: {args.dataset}")
    print(f"\n{'split':6s} {'images':>7s} {'empty':>6s} " + " ".join(f"{name:>8s}" for name in OUR_CLASSES))
    for split in SPLITS:
        if split not in stats["images_per_split"]:
            continue
        counts = stats["boxes_per_class_by_split"][split]
        print(
            f"{split:6s} {stats['images_per_split'][split]:7d} {stats['background_images_per_split'][split]:6d} "
            + " ".join(f"{counts[name]:8d}" for name in OUR_CLASSES)
        )
    print('("empty" = images with no boxes, which the model treats as background)')

    print_group("WARNING", findings.warnings)
    print_group("ERROR", findings.errors)

    error_count = sum(len(v) for v in findings.errors.values())
    warning_count = sum(len(v) for v in findings.warnings.values())
    report_path = args.report or args.dataset / "validation_report.json"
    report_path.write_text(
        json.dumps(
            {"passed": error_count == 0, "stats": stats, "errors": findings.errors, "warnings": findings.warnings},
            indent=2,
        )
        + "\n"
    )

    print(f"\n{error_count} errors, {warning_count} warnings. Full report: {report_path}")
    if error_count:
        print("Fix the errors before training.")
        if any("more than one split" in kind for kind in findings.errors):
            print("For photos in more than one split: delete the dataset folder, then run")
            print("prepare_dataset.py again with --resplit.")
        sys.exit(1)
    print("No errors. The dataset can be used for training.")


if __name__ == "__main__":
    main()
