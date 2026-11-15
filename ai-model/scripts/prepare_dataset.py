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

Identical image files are always removed, because public datasets often
contain each other's photos. Add --resplit to also ignore the sources' own
train/valid/test folders and make a fresh split that keeps copies of a photo,
and pictures that look the same, in one split. Use it when merging datasets
from different authors.

The result is written to datasets/ecosort in the layout configs/data.yaml expects.
"""

import argparse
import hashlib
import json
import re
import shutil
from collections import Counter, defaultdict
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path

import yaml
from PIL import Image

AI_MODEL_DIR = Path(__file__).resolve().parent.parent
OUR_CLASSES = ["paper", "plastic", "metal", "organic"]
IMAGE_SUFFIXES = {".jpg", ".jpeg", ".png", ".bmp", ".webp"}
SPLIT_FOLDERS = {"train": "train", "valid": "val", "val": "val", "test": "test"}
REPORT_NAME = "dataset_report.json"
# Boxes thinner than this fraction of the image are treated as empty.
MIN_BOX_SIDE = 1e-4

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


def to_box_line(parts: list[str], class_id: int) -> str | None:
    """Rewrite one label line with a new class id. Polygons become boxes.

    The box is clipped to the image. Returns None if nothing is left of it,
    or if the line is not a valid box or polygon.
    """
    try:
        values = [float(v) for v in parts[1:]]
    except ValueError:
        return None
    if len(values) == 4:
        cx, cy, w, h = values
        x1, y1, x2, y2 = cx - w / 2, cy - h / 2, cx + w / 2, cy + h / 2
    elif len(values) >= 6 and len(values) % 2 == 0:  # segmentation polygon: x1 y1 x2 y2 ...
        xs, ys = values[0::2], values[1::2]
        x1, y1, x2, y2 = min(xs), min(ys), max(xs), max(ys)
    else:
        return None

    x1, y1, x2, y2 = max(x1, 0.0), max(y1, 0.0), min(x2, 1.0), min(y2, 1.0)
    w, h = x2 - x1, y2 - y1
    if w <= MIN_BOX_SIDE or h <= MIN_BOX_SIDE:
        return None
    return f"{class_id} {(x1 + x2) / 2:.6f} {(y1 + y2) / 2:.6f} {w:.6f} {h:.6f}"


def source_key(filename: str) -> str:
    """Name of the original photo a file came from.

    Roboflow saves augmented copies of one photo as
    "<photo>_jpg.rf.<random id>.jpg". Everything before ".rf." identifies the
    photo, so copies of the same photo share a key.
    """
    stem = Path(filename).stem
    return stem.split(".rf.")[0]


def fallback_split(filename: str) -> str:
    """Split for one file of a source that only has a train folder.

    The split is chosen from the original photo's name, so augmented copies of
    one photo always land in the same split.
    """
    path = Path(filename)
    return bucket_split(f"{path.parent.as_posix()}/{source_key(path.name)}")


def bucket_split(key: str) -> str:
    """A stable 70/20/10 choice of split for a group of images."""
    bucket = int(hashlib.md5(key.encode()).hexdigest(), 16) % 10
    return "train" if bucket < 7 else "val" if bucket < 9 else "test"


def find_splits(source: Path) -> dict[str, Path]:
    found = {SPLIT_FOLDERS[d.name]: d for d in source.iterdir() if d.is_dir() and d.name in SPLIT_FOLDERS}
    # Train first, so when a duplicate is removed the training copy is the one kept.
    return {split: found[split] for split in ("train", "val", "test") if split in found}


@dataclass
class Item:
    """One image that will go into the merged dataset."""

    source: str
    split: str  # the split the source dataset put it in
    image: Path
    lines: list[str]  # label lines, already converted to our classes
    own_split: bool  # True when the source has no validation/test folders of its own

    @property
    def name(self) -> str:
        return f"{self.source}/{self.image.name}"


def collect_source(source: Path, overrides: dict[str, str], stats: dict) -> list[Item]:
    """Read one source dataset and convert its labels. Copies nothing."""
    names = load_names(source / "data.yaml")
    mapping = {class_id: map_class(name, overrides) for class_id, name in names.items()}
    stats["mappings"][source.name] = {names[i]: mapping[i] for i in names}

    splits = find_splits(source)
    if not splits:
        raise SystemExit(f"{source}: no train/valid/test folders found. Is this a YOLO export?")
    own_split = set(splits) == {"train"}

    items = []
    for split, folder in splits.items():
        for image in sorted((folder / "images").iterdir()):
            if image.suffix.lower() not in IMAGE_SUFFIXES:
                continue
            label = folder / "labels" / (image.stem + ".txt")
            source_lines = [ln.split() for ln in label.read_text().splitlines() if ln.strip()] if label.exists() else []

            kept = []
            for parts in source_lines:
                try:
                    source_id = int(parts[0])
                except ValueError:
                    stats["invalid_boxes"] += 1
                    continue
                target = mapping.get(source_id)
                if target is None:
                    stats["dropped"][f"{source.name}: {names.get(source_id, source_id)}"] += 1
                    continue
                line = to_box_line(parts, OUR_CLASSES.index(target))
                if line is None:
                    stats["invalid_boxes"] += 1
                elif line in kept:
                    stats["repeated_boxes"] += 1
                else:
                    kept.append(line)

            # Skip photos whose every item was dropped; they would teach the
            # model that visible waste is background.
            if source_lines and not kept:
                stats["skipped_images"] += 1
                continue
            items.append(Item(source.name, split, image, kept, own_split))
    return items


def file_digest(path: Path) -> str:
    return hashlib.md5(path.read_bytes()).hexdigest()


def visual_hash(path: Path) -> str | None:
    """A fingerprint that stays the same when a picture is re-saved or resized.

    Returns None for a file that will not open, and for a picture so plain
    (for example all one colour) that the fingerprint would match unrelated
    pictures.
    """
    try:
        with Image.open(path) as image:
            small = image.convert("L").resize((9, 8), Image.Resampling.LANCZOS)
            pixels = small.tobytes()  # one byte per pixel, row by row
    except Exception:
        return None
    bits = 0
    for row in range(8):
        for col in range(8):
            bits = (bits << 1) | (pixels[row * 9 + col] > pixels[row * 9 + col + 1])
    if bits in (0, 2**64 - 1):
        return None
    return f"{bits:016x}"


def remove_duplicates(items: list[Item], stats: dict) -> list[Item]:
    """Keep one copy of each identical image file.

    Public datasets often contain each other's photos under different names.
    Left in, the same photo can end up in both training and test data.
    """
    kept: dict[str, Item] = {}
    for item in items:
        digest = file_digest(item.image)
        first = kept.get(digest)
        if first is None:
            kept[digest] = item
            continue
        stats["duplicate_images"] += 1
        if sorted(first.lines) != sorted(item.lines):
            stats["duplicates_with_different_labels"] += 1
    return list(kept.values())


def choose_splits(items: list[Item], resplit: bool) -> list[str]:
    """Decide the split of every item. Returns one split name per item, in order."""
    if not resplit:
        # Trust each source's own split. Sources without one are split by
        # original photo, so augmented copies of a photo stay together.
        return [
            bucket_split(f"{item.source}/{source_key(item.image.name)}") if item.own_split else item.split
            for item in items
        ]

    # Fresh split. Images are first joined into groups that must not be
    # separated: copies of one original photo, and pictures that look the
    # same. Then each whole group goes to one split.
    parent = list(range(len(items)))

    def find(i: int) -> int:
        while parent[i] != i:
            parent[i] = parent[parent[i]]
            i = parent[i]
        return i

    first_with: dict[tuple, int] = {}
    for index, item in enumerate(items):
        keys = [("photo", item.source, source_key(item.image.name))]
        look = visual_hash(item.image)
        if look:
            keys.append(("look", look))
        for key in keys:
            other = first_with.setdefault(key, index)
            parent[find(index)] = find(other)

    group_name: dict[int, str] = {}
    for index, item in enumerate(items):
        root = find(index)
        group_name[root] = min(group_name.get(root, item.name), item.name)
    return [bucket_split(group_name[find(index)]) for index in range(len(items))]


def write_item(item: Item, split: str, out: Path) -> None:
    image_dir, label_dir = out / "images" / split, out / "labels" / split
    image_dir.mkdir(parents=True, exist_ok=True)
    label_dir.mkdir(parents=True, exist_ok=True)
    stem = f"{item.source}__{item.image.stem}"
    suffix = item.image.suffix.lower()
    # Two different files can share a name when they come from different
    # folders of one source. Number the later ones so nothing is overwritten.
    number = 2
    while (image_dir / (stem + suffix)).exists():
        stem = f"{item.source}__{item.image.stem}_{number}"
        number += 1
    shutil.copy2(item.image, image_dir / (stem + suffix))
    (label_dir / (stem + ".txt")).write_text("\n".join(item.lines) + ("\n" if item.lines else ""))


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

    print("\nImages per split:", {split: stats["images"][split] for split in ("train", "val", "test")})
    if stats["duplicate_images"]:
        print(f"Identical image files removed: {stats['duplicate_images']}")
    if stats["duplicates_with_different_labels"]:
        print(
            f"  of which {stats['duplicates_with_different_labels']} were labelled differently in "
            "their two copies (the first copy's labels were kept)"
        )
    if stats["repeated_boxes"]:
        print(f"Boxes listed twice in one label file, kept once: {stats['repeated_boxes']}")
    if stats["skipped_images"]:
        print(f"Images skipped (all items dropped): {stats['skipped_images']}")
    if stats["invalid_boxes"]:
        print(f"Invalid boxes removed (empty, outside the image, or unreadable): {stats['invalid_boxes']}")
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
    parser.add_argument(
        "--resplit",
        action="store_true",
        help="ignore the sources' own train/valid/test folders and make a fresh 70/20/10 split that "
        "keeps copies of a photo, and pictures that look the same, together",
    )
    args = parser.parse_args()

    overrides = {}
    if args.overrides.exists():
        loaded = yaml.safe_load(args.overrides.read_text()) or {}
        overrides = {str(k).strip().lower(): str(v).strip().lower() for k, v in loaded.items()}

    if not args.dry_run and args.out.exists():
        raise SystemExit(f"{args.out} already exists. Delete it first so old and new files do not mix.")

    stats = {
        "mappings": {},
        "boxes": Counter(),
        "boxes_by_split": defaultdict(Counter),
        "images": Counter(),
        "dropped": Counter(),
        "skipped_images": 0,
        "invalid_boxes": 0,
        "repeated_boxes": 0,
        "duplicate_images": 0,
        "duplicates_with_different_labels": 0,
    }
    items: list[Item] = []
    for source in args.sources:
        if not (source / "data.yaml").exists():
            raise SystemExit(f"{source}: data.yaml not found")
        items.extend(collect_source(source, overrides, stats))

    print(f"Checking {len(items)} images for duplicates. This can take a few minutes.", flush=True)
    items = remove_duplicates(items, stats)
    splits = choose_splits(items, args.resplit)

    for item, split in zip(items, splits, strict=True):
        stats["images"][split] += 1
        for line in item.lines:
            name = OUR_CLASSES[int(line.split()[0])]
            stats["boxes"][name] += 1
            stats["boxes_by_split"][split][name] += 1
        if not args.dry_run:
            write_item(item, split, args.out)

    print_report(stats)
    if args.dry_run:
        print("\nDry run: nothing was copied.")
        return

    # A record of exactly how this dataset was built, for the dataset card.
    report = {
        "created": datetime.now(timezone.utc).isoformat(timespec="seconds"),
        "sources": [source.name for source in args.sources],
        "class_mapping": stats["mappings"],
        "overrides": overrides,
        "resplit": args.resplit,
        "images_per_split": {split: stats["images"][split] for split in ("train", "val", "test")},
        "boxes_per_class": {name: stats["boxes"][name] for name in OUR_CLASSES},
        "boxes_per_class_by_split": {
            split: {name: counts[name] for name in OUR_CLASSES} for split, counts in stats["boxes_by_split"].items()
        },
        "boxes_dropped_by_source_class": dict(stats["dropped"]),
        "images_skipped_all_items_dropped": stats["skipped_images"],
        "invalid_boxes_removed": stats["invalid_boxes"],
        "repeated_boxes_removed": stats["repeated_boxes"],
        "identical_images_removed": stats["duplicate_images"],
        "identical_images_with_different_labels": stats["duplicates_with_different_labels"],
    }
    args.out.mkdir(parents=True, exist_ok=True)
    (args.out / REPORT_NAME).write_text(json.dumps(report, indent=2) + "\n")
    print(f"\nDataset written to {args.out}")
    print(f"Build record written to {args.out / REPORT_NAME}")
    print("Next: python scripts/validate_dataset.py")


if __name__ == "__main__":
    main()
