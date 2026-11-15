"""Wraps the trained YOLO model so the API code never touches YOLO directly."""

import logging
import threading
from dataclasses import dataclass

from PIL import Image

from . import config
from .config import Settings

logger = logging.getLogger("ecosort")


@dataclass
class RawDetection:
    category: str
    confidence: float
    bbox: list[int]  # [x1, y1, x2, y2] in pixels of the image that was passed in


class ModelNotAvailable(Exception):
    """Raised when the weights file is missing, unreadable, or for other classes."""


def clean_box(xyxy: list[float], width: int, height: int) -> list[int] | None:
    """Round a box to whole pixels and clip it to the image.

    Returns None if nothing is left, so the API never returns an empty box.
    """
    x1 = min(max(round(xyxy[0]), 0), width)
    y1 = min(max(round(xyxy[1]), 0), height)
    x2 = min(max(round(xyxy[2]), 0), width)
    y2 = min(max(round(xyxy[3]), 0), height)
    if x2 <= x1 or y2 <= y1:
        return None
    return [x1, y1, x2, y2]


class YoloDetector:
    """Loads the weights once and reuses the model for every request."""

    def __init__(self, settings: Settings) -> None:
        if not settings.model_path.exists():
            raise ModelNotAvailable("no weights file at the configured MODEL_PATH")
        try:
            # Imported here so the API can start (and tests can run) on a
            # machine without PyTorch installed.
            from ultralytics import YOLO

            self._model = YOLO(str(settings.model_path))
        except Exception as exc:
            raise ModelNotAvailable(f"could not load the model ({type(exc).__name__})") from exc

        # The model's class ids must mean the same thing as ours. Loading
        # weights trained for other classes would label everything wrongly.
        names = [self._model.names[i] for i in sorted(self._model.names)]
        if names != config.CATEGORIES:
            raise ModelNotAvailable(f"the model's classes are {names}, expected {config.CATEGORIES}")

        self._settings = settings
        # A model detects best at the image size it was trained with, so that
        # is used unless IMAGE_SIZE overrides it.
        trained_size = self._model.overrides.get("imgsz")
        self.image_size: int | None = settings.image_size or (trained_size if isinstance(trained_size, int) else None)
        # One inference at a time: the model is not guaranteed to be thread-safe.
        self._lock = threading.Lock()

    def detect(self, image: Image.Image) -> list[RawDetection]:
        settings = self._settings
        options = {
            "conf": settings.confidence_threshold,
            "iou": settings.iou_threshold,
            "max_det": settings.max_detections,
            "verbose": False,
        }
        if self.image_size:
            options["imgsz"] = self.image_size
        if settings.device != "auto":
            options["device"] = settings.device

        # Ultralytics resizes and letterboxes the image itself, removes
        # duplicate boxes, and returns boxes in the original image's pixels.
        with self._lock:
            result = self._model.predict(image, **options)[0]

        width, height = image.size
        detections = []
        for box in result.boxes:
            bbox = clean_box(box.xyxy[0].tolist(), width, height)
            if bbox is None:
                continue
            detections.append(
                RawDetection(
                    category=config.CATEGORIES[int(box.cls)],
                    confidence=min(max(float(box.conf), 0.0), 1.0),
                    bbox=bbox,
                )
            )
        return detections


def load_detector(settings: Settings):
    """Load the model, or return None and log why it could not be loaded.

    A .onnx MODEL_PATH runs on onnxruntime (no PyTorch, small memory);
    anything else is loaded as Ultralytics .pt weights.
    """
    try:
        if settings.model_path.suffix.lower() == ".onnx":
            from .onnx_detector import OnnxDetector

            detector = OnnxDetector(settings)
        else:
            detector = YoloDetector(settings)
    except ModelNotAvailable as exc:
        logger.warning("Model not loaded: %s", exc)
        return None
    logger.info("Model loaded: %s version %s", settings.model_name, settings.model_version)
    return detector
