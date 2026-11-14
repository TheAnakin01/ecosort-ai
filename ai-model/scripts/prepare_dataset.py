"""Merge several Roboflow YOLO exports into one 4-class EcoSort dataset.

Each source folder is a dataset downloaded from Roboflow in YOLO format:

    source/
      data.yaml
      train/images  train/labels
      valid/images  valid/labels   (optional)
      test/images   test/labels    (optional)

Run from the ai-model/ folder:

    python scripts/prepare_dataset.py downloads/trash-detection downloads/trashnet downloads/neat-now

Add --dry-run first to see how every source class will be mapped without
copying anything. Fix wrong or missing mappings in configs/class_overrides.yaml.

The result is written to datasets/ecosort in the layout configs/data.yaml expects.
"""

import argparse
import hashlib
import re
import shutil
from collections import Counter
from pathlib import Path

import yaml

AI_MODEL_DIR = Path(__file__).resolve().parent.parent
OUR_CLASSES = ["paper", "plastic", "metal", "organic"]
IMAGE_SUFFIXES = {".jpg", ".jpeg", ".png", ".bmp", ".webp"}
SPLIT_FOLDERS = {"train": "train", "valid": "val", "val": "val", "test": "test"}

# A source class is matched on whole words. Words in DROP_WORDS win, so
# "glass bottle" is dropped even though it contains "bottle".
DROP_WORDS = {
    "glass", "battery", "batteries", "trash", "garbage", "general", "other", "others",
    "waste", "clothes", "cloth", "textile", "shoe", "shoes", "medical", "hazardous",
    "ewaste", "electronic", "electronics", "mask", "masks", "cigarette", "ceramic",
    "wood", "rubber", "bulb", "diaper",
}
KEYWORDS = {
    "paper": {"paper", "cardboard", "carton", "newspaper", "magazine", "book", "envelope"},
    "plastic": {"plastic", "pet", "hdpe", "ldpe", "pvc", "polythene", "polyethylene", "wrapper", "styrofoam"},
    "metal": {"metal", "can", "cans", "tin", "aluminium", "aluminum", "foil", "steel"},
    "organic": {
        "organic", "food", "biological", "biodegradable", "fruit", "vegetable", "peel",
        "leaf", "leaves", "bread", "eggshell", "bone", "compost",
    },
}


def words_of(name: str) -> list[str]:
    return re.findall(r"[a-z]+", name.lower().replace("e-waste", "ewaste"))


def map_class(name: str, overrides: dict[str, str]) -> str | None:
    """Return our class for a source class name, or None to drop it."""
    key = name.strip().lower()
    if key in overrides:
        target = overrides[key]
        if target == "drop":
            return None
        if target not in OUR_CLASSES:
            raise ValueError(f'Override for "{name}" must be one of {OUR_CLASSES} or "drop", got "{target}"')
        return target

    words = words_of(name)
    matches = {target for target, keywords in KEYWORDS.items() if keywords & set(words)}
    # "waste" and similar words are too vague to drop a class that also names a material.
    hard_drop = set(words) & (DROP_WORDS - {"waste", "general", "other", "others", "trash", "garbage"})
    if hard_drop:
        return None
    if len(matches) == 1:
        return matches.pop()
    return None  # no match, or two materials at once (for example "paper plastic cup")


def load_names(data_yaml: Path) -> dict[int, str]:
    names = yaml.safe_load(data_yaml.read_text())["names"]
    if isinstance(names, list):
        return dict(enumerate(names))
    return {int(k): str(v) for k, v in names.items()}


def to_box_line(parts: list[str], class_id: int) -> str:
    """Rewrite one label line with a new class id. Polygons become boxes."""
    values = [float(v) for v in parts[1:]]
    if len(values) == 4:
        cx, cy, w, h = values
    else:  # segmentation polygon: x1 y1 x2 y2 ...
        xs, ys = values[0::2], values[1::2]
        cx, cy = (min(xs) + max(xs)) / 2, (min(ys) + max(ys)) / 2
        w, h = max(xs) - min(xs), max(ys) - min(ys)
    return f"{class_id} {cx:.6f} {cy:.6f} {w:.6f} {h:.6f}"


def fallback_split(filename: str) -> str:
    """Stable 70/20/10 split for a source that only has a train folder."""
    bucket = int(hashlib.md5(filename.encode()).hexdigest(), 16) % 10
    return "train" if bucket < 7 else "val" if bucket < 9 else "test"


def find_splits(source: Path) -> dict[str, Path]:
    return {SPLIT_FOLDERS[d.name]: d for d in sorted(source.iterdir()) if d.is_dir() and d.name in SPLIT_FOLDERS}


def process_source(source: Path, out: Path | None, overrides: dict[str, str], stats: dict) -> None:
    names = load_names(source / "data.yaml")
    mapping = {class_id: map_class(name, overrides) for class_id, name in names.items()}
    stats["mappings"][source.name] = {names[i]: mapping[i] for i in names}

    splits = find_splits(source)
    if not splits:
        raise SystemExit(f"{source}: no train/valid/test folders found. Is this a YOLO export?")
    only_train = set(splits) == {"train"}

    for split, folder in splits.items():
        for image in sorted((folder / "images").iterdir()):
            if image.suffix.lower() not in IMAGE_SUFFIXES:
                continue
            label = folder / "labels" / (image.stem + ".txt")
            source_lines = [ln.split() for ln in label.read_text().splitlines() if ln.strip()] if label.exists() else []

            kept = []
            for parts in source_lines:
                source_id = int(parts[0])
                target = mapping.get(source_id)
                if target is None:
                    stats["dropped"][f"{source.name}: {names.get(source_id, source_id)}"] += 1
                    continue
                kept.append(to_box_line(parts, OUR_CLASSES.index(target)))
                stats["boxes"][target] += 1

            # Skip photos whose every item was dropped; they would teach the
            # model that visible waste is background.
            if source_lines and not kept:
                stats["skipped_images"] += 1
                continue

            target_split = fallback_split(image.name) if only_train else split
            stats["images"][target_split] += 1
            if out is not None:
                stem = f"{source.name}__{image.stem}"
                (out / "images" / target_split).mkdir(parents=True, exist_ok=True)
                (out / "labels" / target_split).mkdir(parents=True, exist_ok=True)
                shutil.copy2(image, out / "images" / target_split / (stem + image.suffix.lower()))
                (out / "labels" / target_split / (stem + ".txt")).write_text("\n".join(kept) + ("\n" if kept else ""))


def print_report(stats: dict) -> None:
    for source, mapping in stats["mappings"].items():
        print(f"\n{source}")
        for name, target in mapping.items():
            print(f"  {name:32s} -> {target or 'DROPPED'}")

    print("\nBoxes per class:")
    total = sum(stats["boxes"].values()) or 1
    for name in OUR_CLASSES:
        count = stats["boxes"][name]
        note = "   <-- too few, add more photos of this class" if count / total < 0.1 else ""
        print(f"  {name:8s} {count:6d}  ({count / total:.0%}){note}")

    print("\nImages per split:", dict(stats["images"]))
    if stats["skipped_images"]:
        print(f"Images skipped (all items dropped): {stats['skipped_images']}")
    if stats["dropped"]:
        print("\nBoxes dropped, by source class:")
        for name, count in stats["dropped"].most_common():
            print(f"  {name}: {count}")
        print("If a dropped class belongs to one of our four, add it to configs/class_overrides.yaml")


def main() -> None:
    parser = argparse.ArgumentParser(description="Merge Roboflow YOLO exports into the EcoSort dataset")
    parser.add_argument("sources", nargs="+", type=Path, help="downloaded dataset folders")
    parser.add_argument("--out", type=Path, default=AI_MODEL_DIR / "datasets" / "ecosort")
    parser.add_argument("--overrides", type=Path, default=AI_MODEL_DIR / "configs" / "class_overrides.yaml")
    parser.add_argument("--dry-run", action="store_true", help="show the mapping and counts, copy nothing")
    args = parser.parse_args()

    overrides = {}
    if args.overrides.exists():
        loaded = yaml.safe_load(args.overrides.read_text()) or {}
        overrides = {str(k).strip().lower(): str(v).strip().lower() for k, v in loaded.items()}

    if not args.dry_run and args.out.exists():
        raise SystemExit(f"{args.out} already exists. Delete it first so old and new files do not mix.")

    stats = {"mappings": {}, "boxes": Counter(), "images": Counter(), "dropped": Counter(), "skipped_images": 0}
    for source in args.sources:
        if not (source / "data.yaml").exists():
            raise SystemExit(f"{source}: data.yaml not found")
        process_source(source, None if args.dry_run else args.out, overrides, stats)

    print_report(stats)
    print("\nDry run: nothing was copied." if args.dry_run else f"\nDataset written to {args.out}")


if __name__ == "__main__":
    main()
