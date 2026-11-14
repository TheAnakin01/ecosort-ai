"""Run the trained detector on one image and save a copy with boxes drawn.

    python scripts/predict.py path/to/photo.jpg
    python scripts/predict.py photo.jpg --weights weights/best.pt --conf 0.4

This is the first milestone in the blueprint: a model running locally that
returns labelled boxes for several objects in one photo.
"""

import argparse
from collections import Counter
from pathlib import Path

from ultralytics import YOLO

AI_MODEL_DIR = Path(__file__).resolve().parent.parent


def main() -> None:
    parser = argparse.ArgumentParser(description="Detect waste in one image")
    parser.add_argument("image", help="path to a photo")
    parser.add_argument("--weights", default=str(AI_MODEL_DIR / "weights" / "best.pt"))
    parser.add_argument("--conf", type=float, default=0.35, help="minimum confidence to keep")
    args = parser.parse_args()

    model = YOLO(args.weights)
    result = model.predict(args.image, conf=args.conf, verbose=False)[0]

    counts: Counter[str] = Counter()
    for box in result.boxes:
        category = result.names[int(box.cls)]
        x1, y1, x2, y2 = (round(v) for v in box.xyxy[0].tolist())
        counts[category] += 1
        print(f"{category:8s} {float(box.conf):.2f}  box=({x1}, {y1}, {x2}, {y2})")

    if not counts:
        print("No waste detected.")
    else:
        print("Counts:", dict(counts))

    out_path = Path(args.image).with_name(Path(args.image).stem + "_detected.jpg")
    result.save(filename=str(out_path))
    print(f"Saved {out_path}")


if __name__ == "__main__":
    main()
