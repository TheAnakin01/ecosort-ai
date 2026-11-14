"""Make a tiny fake dataset of coloured shapes, for checking the pipeline.

This is NOT waste data and a model trained on it is useless for the app. It
exists so the scripts can be run end to end in a couple of minutes, on a
laptop CPU, without downloading anything:

    python tests/make_synthetic_dataset.py /tmp/synthetic
    python scripts/validate_dataset.py /tmp/synthetic

Each class is one solid colour on a grey background:
paper = white, plastic = blue, metal = red, organic = green.
"""

import argparse
import random
from pathlib import Path

from PIL import Image, ImageDraw

COLOURS = [(245, 245, 245), (40, 90, 220), (210, 40, 40), (40, 170, 60)]  # class 0..3
SPLIT_SIZES = {"train": 96, "val": 24, "test": 24}
IMAGE_SIZE = (320, 240)


def overlaps(box, others) -> bool:
    return any(not (box[2] <= o[0] or box[0] >= o[2] or box[3] <= o[1] or box[1] >= o[3]) for o in others)


def make_example(rng: random.Random) -> tuple[Image.Image, list[str]]:
    width, height = IMAGE_SIZE
    shade = rng.randrange(90, 150)
    image = Image.new("RGB", IMAGE_SIZE, (shade, shade, shade))
    draw = ImageDraw.Draw(image)
    boxes, lines = [], []
    for _ in range(rng.randrange(1, 4)):
        for _attempt in range(20):
            w, h = rng.randrange(50, 110), rng.randrange(40, 90)
            x1, y1 = rng.randrange(0, width - w), rng.randrange(0, height - h)
            box = (x1, y1, x1 + w, y1 + h)
            if not overlaps(box, boxes):
                break
        else:
            continue
        class_id = rng.randrange(4)
        draw.rectangle(box, fill=COLOURS[class_id])
        boxes.append(box)
        lines.append(
            f"{class_id} {(box[0] + box[2]) / 2 / width:.6f} {(box[1] + box[3]) / 2 / height:.6f} "
            f"{w / width:.6f} {h / height:.6f}"
        )
    return image, lines


def main() -> None:
    parser = argparse.ArgumentParser(description="Make a tiny synthetic dataset for pipeline checks")
    parser.add_argument("out", type=Path)
    parser.add_argument("--seed", type=int, default=0)
    args = parser.parse_args()

    rng = random.Random(args.seed)
    for split, count in SPLIT_SIZES.items():
        (args.out / "images" / split).mkdir(parents=True, exist_ok=True)
        (args.out / "labels" / split).mkdir(parents=True, exist_ok=True)
        for index in range(count):
            image, lines = make_example(rng)
            image.save(args.out / "images" / split / f"{split}_{index:03d}.png")
            (args.out / "labels" / split / f"{split}_{index:03d}.txt").write_text("\n".join(lines) + "\n")

    (args.out / "data.yaml").write_text(
        f"path: {args.out.resolve()}\ntrain: images/train\nval: images/val\ntest: images/test\n"
        "names:\n  0: paper\n  1: plastic\n  2: metal\n  3: organic\n"
    )
    print(f"Synthetic dataset written to {args.out} (coloured shapes, not waste)")


if __name__ == "__main__":
    main()
