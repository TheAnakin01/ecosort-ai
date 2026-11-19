"""Find where the detector sees waste that is not there.

mAP is measured at a very low confidence threshold, so it says little about
what the app will actually show. This script runs the model the way the app
does (same confidence and overlap thresholds as the backend), compares every
detection with the labels, and sorts each one into:

- correct:      on a labelled item, with the right class
- wrong class:  on a labelled item, with the wrong class
- duplicate:    a second box on an item that already has one
- poor box:     touches a labelled item but does not cover it well
- on nothing:   no labelled item there at all. These are the hallucinations.

Labelled items with no box at all are counted under "no box".

It also saves the photos with the most "on nothing" boxes, drawn, so a person
can look at them. Some will turn out to be real waste that nobody labelled
(for example glass, which we exclude); those are label gaps, not model faults.

Run from the ai-model/ folder, on the validation split:

    python scripts/check_hallucinations.py --weights runs/ecosort-v2/weights/best.pt

Use --conf to try other thresholds. Choose the threshold on the validation
split; never tune on the test split.
"""

import argparse
import json
from collections import Counter, defaultdict
from datetime import datetime, timezone
from pathlib import Path

from PIL import Image, ImageDraw

from dataset_paths import AI_MODEL_DIR, data_root, dataset_dir  # noqa: E402

CLASSES = ["paper", "plastic", "metal", "organic"]
IMAGE_SUFFIXES = {".jpg", ".jpeg", ".png", ".bmp", ".webp"}
OUTCOMES = ["correct", "wrong class", "duplicate", "poor box", "on nothing"]
MATCH_IOU = 0.5  # the same rule as mAP@50
TOUCH_IOU = 0.1  # below this a box is not near any labelled item

# Box = (x1, y1, x2, y2), as fractions of the image width and height.
Box = tuple[float, float, float, float]


def iou(a: Box, b: Box) -> float:
    width = min(a[2], b[2]) - max(a[0], b[0])
    height = min(a[3], b[3]) - max(a[1], b[1])
    if width <= 0 or height <= 0:
        return 0.0
    overlap = width * height
    union = (a[2] - a[0]) * (a[3] - a[1]) + (b[2] - b[0]) * (b[3] - b[1]) - overlap
    return overlap / union if union > 0 else 0.0


def match_image(
    predictions: list[tuple[int, float, Box]], labels: list[tuple[int, Box]]
) -> tuple[list[str], list[bool]]:
    """Sort one image's detections into OUTCOMES.

    predictions: (class, confidence, box). labels: (class, box).
    Returns the outcome of each prediction, in the order given, and for each
    label whether some detection found it. The most confident detection claims
    an item first, so a weaker second box on it counts as a duplicate.
    """
    outcomes = [""] * len(predictions)
    found = [False] * len(labels)
    for index in sorted(range(len(predictions)), key=lambda i: -predictions[i][1]):
        cls, _, box = predictions[index]
        overlaps = [iou(box, label_box) for _, label_box in labels]
        free = [o if not found[j] else 0.0 for j, o in enumerate(overlaps)]
        best = max(range(len(labels)), key=lambda j: free[j], default=None)
        if best is not None and free[best] >= MATCH_IOU:
            found[best] = True
            outcomes[index] = "correct" if labels[best][0] == cls else "wrong class"
        elif any(o >= MATCH_IOU for o in overlaps):
            outcomes[index] = "duplicate"
        elif any(o >= TOUCH_IOU for o in overlaps):
            outcomes[index] = "poor box"
        else:
            outcomes[index] = "on nothing"
    return outcomes, found


def read_labels(label_file: Path) -> list[tuple[int, Box]]:
    labels = []
    if not label_file.exists():
        return labels
    for line in label_file.read_text().splitlines():
        parts = line.split()
        if len(parts) != 5:
            continue
        cx, cy, w, h = (float(v) for v in parts[1:])
        labels.append((int(parts[0]), (cx - w / 2, cy - h / 2, cx + w / 2, cy + h / 2)))
    return labels


def summarise(per_image: list[dict]) -> dict:
    """Totals per predicted class (for detections) and per true class (for misses)."""
    outcomes: dict[str, Counter] = defaultdict(Counter)
    labelled, missed, wrong_as = Counter(), Counter(), defaultdict(Counter)
    empty_images = empty_with_detections = 0
    for image in per_image:
        for cls, outcome in zip(image["pred_classes"], image["outcomes"], strict=True):
            outcomes[CLASSES[cls]][outcome] += 1
        for (cls, _), was_found in zip(image["labels"], image["found"], strict=True):
            labelled[CLASSES[cls]] += 1
            if not was_found:
                missed[CLASSES[cls]] += 1
        for pred_cls, true_cls in image["confusions"]:
            wrong_as[CLASSES[true_cls]][CLASSES[pred_cls]] += 1
        if not image["labels"]:
            empty_images += 1
            empty_with_detections += bool(image["outcomes"])

    per_class = {}
    for name in CLASSES:
        shown = sum(outcomes[name].values())
        per_class[name] = {
            "detections": shown,
            **{outcome: outcomes[name][outcome] for outcome in OUTCOMES},
            "share_correct": round(outcomes[name]["correct"] / shown, 4) if shown else None,
            "share_on_nothing": round(outcomes[name]["on nothing"] / shown, 4) if shown else None,
            "labelled": labelled[name],
            "missed": missed[name],
            "labelled_as_this_but_called": dict(wrong_as[name]),
        }
    total = sum(item["detections"] for item in per_class.values())
    on_nothing = sum(item["on nothing"] for item in per_class.values())
    return {
        "images": len(per_image),
        "detections": total,
        "on_nothing": on_nothing,
        "share_on_nothing": round(on_nothing / total, 4) if total else None,
        "images_without_labels": empty_images,
        "of_which_got_detections": empty_with_detections,
        "per_class": per_class,
    }


def print_summary(summary: dict, conf: float) -> None:
    print(f"\nWhat the app would show at confidence {conf}, on {summary['images']} images")
    print(
        f"{'class':8s} {'shown':>6s} {'correct':>8s} {'wrong':>6s} {'dupl.':>6s} "
        f"{'poor':>5s} {'nothing':>8s} {'no box':>12s}"
    )
    for name, row in summary["per_class"].items():
        missed = f"{row['missed']}/{row['labelled']}"
        print(
            f"{name:8s} {row['detections']:6d} {row['correct']:8d} {row['wrong class']:6d} {row['duplicate']:6d} "
            f"{row['poor box']:5d} {row['on nothing']:8d} {missed:>12s}"
        )
    if summary["detections"]:
        print(
            f"\nBoxes on nothing (hallucinations): {summary['on_nothing']} of {summary['detections']} "
            f"({summary['share_on_nothing']:.1%})"
        )
    print(
        f"Photos with no labelled items: {summary['images_without_labels']}, "
        f"of which the model drew boxes on {summary['of_which_got_detections']}"
    )
    for name, row in summary["per_class"].items():
        if row["labelled_as_this_but_called"]:
            print(f"Labelled {name}, detected as: {row['labelled_as_this_but_called']}")


def to_pixels(box: Box, size: tuple[int, int]) -> tuple[float, float, float, float]:
    width, height = size
    return (box[0] * width, box[1] * height, box[2] * width, box[3] * height)


def draw_examples(per_image: list[dict], out_dir: Path, count: int) -> list[str]:
    """Save the photos with the most boxes on nothing. Red = on nothing, yellow = other
    mistakes, green = correct, white outline = the labels."""
    worst = sorted(
        (image for image in per_image if "on nothing" in image["outcomes"]),
        key=lambda image: -image["outcomes"].count("on nothing"),
    )[:count]
    out_dir.mkdir(parents=True, exist_ok=True)
    saved = []
    for image in worst:
        with Image.open(image["path"]) as photo:
            picture = photo.convert("RGB")
        draw = ImageDraw.Draw(picture)
        size = picture.size
        for _, box in image["labels"]:
            draw.rectangle(to_pixels(box, size), outline=(255, 255, 255), width=2)
        for cls, conf, box, outcome in zip(
            image["pred_classes"], image["pred_confs"], image["pred_boxes"], image["outcomes"], strict=True
        ):
            colour = {"correct": (40, 200, 70), "on nothing": (230, 30, 30)}.get(outcome, (240, 200, 0))
            x1, y1, x2, y2 = to_pixels(box, size)
            draw.rectangle((x1, y1, x2, y2), outline=colour, width=3)
            draw.text((x1 + 3, y1 + 3), f"{CLASSES[cls]} {conf:.2f}", fill=colour)
        target = out_dir / Path(image["path"]).name
        picture.save(target)
        saved.append(str(target))
    return saved


def main() -> None:
    parser = argparse.ArgumentParser(description="Count false detections the way the app would see them")
    parser.add_argument("--weights", type=Path, default=data_root() / "weights" / "best.pt")
    parser.add_argument("--data", type=Path, default=AI_MODEL_DIR / "configs" / "data.yaml")
    parser.add_argument("--split", choices=["val", "test"], default="val")
    parser.add_argument("--conf", type=float, default=0.35, help="the backend's CONFIDENCE_THRESHOLD")
    parser.add_argument("--iou", type=float, default=0.7, help="the backend's IOU_THRESHOLD")
    parser.add_argument("--imgsz", type=int, default=640)
    parser.add_argument("--limit", type=int, help="check only the first N images, for a quick look")
    parser.add_argument("--examples", type=int, default=30, help="how many worst photos to save")
    parser.add_argument("--out", type=Path, help="folder for the report and example photos")
    args = parser.parse_args()

    if not args.weights.exists():
        raise SystemExit(f"{args.weights} not found. Train a model first, or pass --weights.")
    dataset = dataset_dir(args.data)
    image_dir, label_dir = dataset / "images" / args.split, dataset / "labels" / args.split
    if not image_dir.is_dir():
        raise SystemExit(f"{image_dir} not found. Run scripts/prepare_dataset.py first.")
    images = sorted(p for p in image_dir.iterdir() if p.suffix.lower() in IMAGE_SUFFIXES)[: args.limit]
    out = args.out or args.weights.parent.parent / f"hallucination_check_{args.split}"

    from ultralytics import YOLO  # imported here so the rest of this file needs no PyTorch

    model = YOLO(str(args.weights))
    per_image = []
    print(f"Checking {len(images)} images...", flush=True)
    for start in range(0, len(images), 32):
        batch = images[start : start + 32]
        results = model.predict(
            [str(p) for p in batch], conf=args.conf, iou=args.iou, imgsz=args.imgsz, verbose=False
        )
        for path, result in zip(batch, results, strict=True):
            predictions = [
                (int(c), float(s), tuple(b))
                for c, s, b in zip(
                    result.boxes.cls.tolist(), result.boxes.conf.tolist(), result.boxes.xyxyn.tolist(), strict=True
                )
            ]
            labels = read_labels(label_dir / (path.stem + ".txt"))
            outcomes, found = match_image(predictions, labels)
            confusions = []
            for (cls, _, box), outcome in zip(predictions, outcomes, strict=True):
                if outcome == "wrong class":
                    true = max(labels, key=lambda label: iou(box, label[1]))[0]
                    confusions.append((cls, true))
            per_image.append(
                {
                    "path": str(path),
                    "pred_classes": [p[0] for p in predictions],
                    "pred_confs": [p[1] for p in predictions],
                    "pred_boxes": [p[2] for p in predictions],
                    "outcomes": outcomes,
                    "labels": labels,
                    "found": found,
                    "confusions": confusions,
                }
            )

    summary = summarise(per_image)
    print_summary(summary, args.conf)
    examples = draw_examples(per_image, out / "worst_photos", args.examples)
    report = {
        "checked": datetime.now(timezone.utc).isoformat(timespec="seconds"),
        "weights": str(args.weights),
        "split": args.split,
        "conf": args.conf,
        "iou": args.iou,
        "image_size": args.imgsz,
        **summary,
        "example_photos": examples,
    }
    (out / "report.json").write_text(json.dumps(report, indent=2) + "\n")
    print(f"\nWorst {len(examples)} photos saved to {out / 'worst_photos'} (red = box on nothing)")
    print(f"Report: {out / 'report.json'}")


if __name__ == "__main__":
    main()
