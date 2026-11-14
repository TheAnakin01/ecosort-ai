"""Convert a downloaded YOLO dataset's classes into our four classes.

Datasets from Roboflow Universe or TACO use their own class lists, such as
"bottle", "can", "cardboard". This script rewrites every label file so the
class numbers match ours: 0 paper, 1 plastic, 2 metal, 3 organic.

1. Edit CLASS_MAP below for the dataset you downloaded. The keys are that
   dataset's class names (see its data.yaml). Leave a class out to drop it.
2. Run:

    python scripts/remap_labels.py path/to/source/data.yaml path/to/source/labels out/labels

Nothing in the source folder is changed.
"""

import argparse
from collections import Counter
from pathlib import Path

import yaml

OUR_CLASSES = ["paper", "plastic", "metal", "organic"]

# Source class name (lower case) -> our class name. Edit for each dataset.
CLASS_MAP = {
    "paper": "paper",
    "cardboard": "paper",
    "carton": "paper",
    "plastic": "plastic",
    "bottle": "plastic",
    "plastic bag": "plastic",
    "metal": "metal",
    "can": "metal",
    "aluminium foil": "metal",
    "organic": "organic",
    "biological": "organic",
    "food waste": "organic",
}


def load_source_names(data_yaml: Path) -> dict[int, str]:
    names = yaml.safe_load(data_yaml.read_text())["names"]
    if isinstance(names, list):
        return dict(enumerate(names))
    return {int(k): v for k, v in names.items()}


def remap_line(line: str, source_names: dict[int, str]) -> tuple[str | None, str]:
    """Return (new line or None if dropped, source class name)."""
    parts = line.split()
    source_name = source_names[int(parts[0])].lower()
    target = CLASS_MAP.get(source_name)
    if target is None:
        return None, source_name
    return " ".join([str(OUR_CLASSES.index(target)), *parts[1:]]), source_name


def main() -> None:
    parser = argparse.ArgumentParser(description="Remap YOLO labels to the 4 EcoSort classes")
    parser.add_argument("data_yaml", type=Path, help="source dataset's data.yaml")
    parser.add_argument("labels_in", type=Path, help="source labels folder")
    parser.add_argument("labels_out", type=Path, help="where to write remapped labels")
    args = parser.parse_args()

    source_names = load_source_names(args.data_yaml)
    kept: Counter[str] = Counter()
    dropped: Counter[str] = Counter()

    for label_file in sorted(args.labels_in.rglob("*.txt")):
        new_lines = []
        for line in label_file.read_text().splitlines():
            if not line.strip():
                continue
            new_line, source_name = remap_line(line, source_names)
            if new_line is None:
                dropped[source_name] += 1
            else:
                new_lines.append(new_line)
                kept[OUR_CLASSES[int(new_line.split()[0])]] += 1

        out_file = args.labels_out / label_file.relative_to(args.labels_in)
        out_file.parent.mkdir(parents=True, exist_ok=True)
        out_file.write_text("\n".join(new_lines) + ("\n" if new_lines else ""))

    print("Boxes kept per class:")
    for name in OUR_CLASSES:
        print(f"  {name:8s} {kept[name]}")
    if dropped:
        print("Boxes dropped (class not in CLASS_MAP):")
        for name, count in dropped.most_common():
            print(f"  {name}: {count}")


if __name__ == "__main__":
    main()
