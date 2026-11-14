"""Fine-tune a pretrained YOLO nano detector on the 4-class waste dataset.

Run from the ai-model/ folder (Colab or a laptop with a GPU):

    python scripts/train.py --epochs 50

The best checkpoint is saved to runs/detect/<name>/weights/best.pt.
Copy it to ai-model/weights/best.pt so the backend can load it.
"""

import argparse
from pathlib import Path

from ultralytics import YOLO

AI_MODEL_DIR = Path(__file__).resolve().parent.parent


def main() -> None:
    parser = argparse.ArgumentParser(description="Train the EcoSort detector")
    parser.add_argument("--model", default="yolo11n.pt", help="pretrained weights to start from")
    parser.add_argument("--data", default=str(AI_MODEL_DIR / "configs" / "data.yaml"))
    parser.add_argument("--epochs", type=int, default=50)
    parser.add_argument("--imgsz", type=int, default=640)
    parser.add_argument("--batch", type=int, default=16)
    parser.add_argument("--name", default="ecosort-baseline", help="name of this training run")
    args = parser.parse_args()

    # Transfer learning: start from weights that already know general shapes
    # and edges, then teach them our four waste classes.
    model = YOLO(args.model)
    model.train(
        data=args.data,
        epochs=args.epochs,
        imgsz=args.imgsz,
        batch=args.batch,
        name=args.name,
        patience=15,  # stop early if validation stops improving
    )

    # Score the best checkpoint on the test split, which training never saw.
    metrics = model.val(data=args.data, split="test")
    print(f"mAP@50:    {metrics.box.map50:.3f}")
    print(f"mAP@50-95: {metrics.box.map:.3f}")
    print("Write these numbers in docs/training-log.md")


if __name__ == "__main__":
    main()
