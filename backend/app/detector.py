"""Wraps the trained YOLO model so the API code never touches YOLO directly."""

from dataclasses import dataclass
from pathlib import Path

from PIL import Image

from . import config


@dataclass
class RawDetection:
    category: str
    confidence: float
    bbox: list[int]  # [x1, y1, x2, y2] in original-image pixels


class ModelNotAvailable(Exception):
    """Raised when the weights file is missing or cannot be loaded."""


class YoloDetector:
    """Loads the weights once and reuses the model for every request."""

    def __init__(self, weights_path: Path, confidence: float) -> None:
        if not weights_path.exists():
            raise ModelNotAvailable(f"No weights file at {weights_path}")
        try:
            # Imported here so the API can start (and tests can run) on a
            # machine without PyTorch installed.
            from ultralytics import YOLO

            self._model = YOLO(str(weights_path))
        except Exception as exc:
            raise ModelNotAvailable(f"Could not load model: {exc}") from exc
        self._confidence = confidence

    def detect(self, image: Image.Image) -> list[RawDetection]:
        # Ultralytics resizes and letterboxes the image itself, and returns
        # boxes already mapped back to the original image's pixels.
        result = self._model.predict(image, conf=self._confidence, verbose=False)[0]
        width, height = image.size
        detections = []
        for box in result.boxes:
            category = result.names[int(box.cls)]
            if category not in config.CATEGORIES:
                continue
            x1, y1, x2, y2 = box.xyxy[0].tolist()
            detections.append(
                RawDetection(
                    category=category,
                    confidence=float(box.conf),
                    bbox=[
                        max(0, round(x1)),
                        max(0, round(y1)),
                        min(width, round(x2)),
                        min(height, round(y2)),
                    ],
                )
            )
        return detections


_detector: YoloDetector | None = None


def get_detector() -> YoloDetector:
    """FastAPI dependency. Tests replace this with a fake detector."""
    global _detector
    if _detector is None:
        _detector = YoloDetector(config.MODEL_PATH, config.CONFIDENCE_THRESHOLD)
    return _detector
