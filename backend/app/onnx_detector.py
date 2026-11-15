"""Runs the exported ONNX model with onnxruntime, without PyTorch.

Same public interface as YoloDetector (`detect`, `image_size`), so the API code
does not care which one is loaded. Pre- and post-processing follow Ultralytics:
letterbox (long side = image size, minimal padding to a multiple of 32, grey 114), RGB in 0..1, NCHW float32; the
output is (1, 4 + classes, anchors) with boxes as centre x, centre y, width,
height in letterboxed pixels. Class-aware NMS is done here with numpy.
"""

import json
import logging
import threading

import cv2
import numpy as np
from PIL import Image

from . import config
from .config import Settings
from .detector import ModelNotAvailable, RawDetection, clean_box

logger = logging.getLogger("ecosort")

PAD_VALUE = 114
STRIDE = 32


def letterbox(image: Image.Image, size: int) -> tuple[np.ndarray, float, float, float]:
    """Resize and pad exactly like Ultralytics' predict (auto=True).

    The long side becomes `size`; padding is only what is needed to reach a
    multiple of 32. Returns (NCHW float32 tensor, scale, pad_left, pad_top).
    """
    rgb = np.asarray(image if image.mode == "RGB" else image.convert("RGB"))
    height, width = rgb.shape[:2]
    scale = min(size / height, size / width)
    new_w, new_h = round(width * scale), round(height * scale)
    pad_w, pad_h = (size - new_w) % STRIDE / 2, (size - new_h) % STRIDE / 2
    if (width, height) != (new_w, new_h):
        rgb = cv2.resize(rgb, (new_w, new_h), interpolation=cv2.INTER_LINEAR)
    top, bottom = round(pad_h - 0.1), round(pad_h + 0.1)
    left, right = round(pad_w - 0.1), round(pad_w + 0.1)
    rgb = cv2.copyMakeBorder(rgb, top, bottom, left, right, cv2.BORDER_CONSTANT, value=(PAD_VALUE,) * 3)
    tensor = np.ascontiguousarray(rgb.transpose(2, 0, 1)[None].astype(np.float32) / 255.0)
    return tensor, scale, float(left), float(top)


def nms(boxes: np.ndarray, scores: np.ndarray, iou_threshold: float) -> list[int]:
    """Greedy non-maximum suppression. boxes are x1, y1, x2, y2."""
    order = scores.argsort()[::-1]
    keep: list[int] = []
    areas = (boxes[:, 2] - boxes[:, 0]) * (boxes[:, 3] - boxes[:, 1])
    while order.size:
        i = int(order[0])
        keep.append(i)
        if order.size == 1:
            break
        rest = order[1:]
        xx1 = np.maximum(boxes[i, 0], boxes[rest, 0])
        yy1 = np.maximum(boxes[i, 1], boxes[rest, 1])
        xx2 = np.minimum(boxes[i, 2], boxes[rest, 2])
        yy2 = np.minimum(boxes[i, 3], boxes[rest, 3])
        inter = np.clip(xx2 - xx1, 0, None) * np.clip(yy2 - yy1, 0, None)
        union = areas[i] + areas[rest] - inter
        iou = inter / np.maximum(union, 1e-9)
        order = rest[iou <= iou_threshold]
    return keep


class OnnxDetector:
    """Loads the .onnx file once and reuses the session for every request."""

    def __init__(self, settings: Settings) -> None:
        if not settings.model_path.exists():
            raise ModelNotAvailable("no model file at the configured MODEL_PATH")
        try:
            import onnxruntime as ort

            options = ort.SessionOptions()
            options.log_severity_level = 3
            self._session = ort.InferenceSession(
                str(settings.model_path), sess_options=options, providers=["CPUExecutionProvider"]
            )
        except Exception as exc:
            raise ModelNotAvailable(f"could not load the model ({type(exc).__name__})") from exc

        model_input = self._session.get_inputs()[0]
        self._input_name = model_input.name
        if len(model_input.shape) != 4:
            raise ModelNotAvailable(f"unexpected input shape {model_input.shape}")

        # Class names live in the file's metadata (written by Ultralytics).
        meta = self._session.get_modelmeta().custom_metadata_map
        trained = self._read_trained_size(meta.get("imgsz"))
        self.image_size: int | None = settings.image_size or trained
        names = self._read_names()
        if names != config.CATEGORIES:
            raise ModelNotAvailable(f"the model's classes are {names}, expected {config.CATEGORIES}")

        out_shape = self._session.get_outputs()[0].shape
        if len(out_shape) != 3 or out_shape[1] != 4 + len(config.CATEGORIES):
            raise ModelNotAvailable(f"unexpected output shape {out_shape}")

        self._settings = settings
        self._lock = threading.Lock()

    @staticmethod
    def _read_trained_size(raw: str | None) -> int:
        """Ultralytics writes the export size as e.g. "[640, 640]"; default to 640."""
        try:
            import ast

            value = ast.literal_eval(raw) if raw else 640
            return int(value[0] if isinstance(value, (list, tuple)) else value)
        except (ValueError, SyntaxError, TypeError):
            return 640

    def _read_names(self) -> list[str]:
        raw = self._session.get_modelmeta().custom_metadata_map.get("names")
        if not raw:
            raise ModelNotAvailable("the ONNX file has no class names in its metadata")
        try:
            # Ultralytics writes a Python dict literal: {0: 'paper', ...}
            import ast

            mapping = ast.literal_eval(raw)
            return [mapping[i] for i in sorted(mapping)]
        except (ValueError, SyntaxError, TypeError):
            try:
                mapping = json.loads(raw)
                return [mapping[k] for k in sorted(mapping, key=int)]
            except Exception as exc:
                raise ModelNotAvailable("could not read the class names from the ONNX file") from exc

    def detect(self, image: Image.Image) -> list[RawDetection]:
        settings = self._settings
        size = self.image_size or 640
        width, height = image.size
        tensor, scale, pad_x, pad_y = letterbox(image, size)

        with self._lock:
            output = self._session.run(None, {self._input_name: tensor})[0]

        predictions = output[0].T  # (anchors, 4 + classes)
        class_scores = predictions[:, 4:]
        best_class = class_scores.argmax(axis=1)
        best_score = class_scores[np.arange(len(class_scores)), best_class]
        keep = best_score >= settings.confidence_threshold
        if not keep.any():
            return []
        predictions, best_class, best_score = predictions[keep], best_class[keep], best_score[keep]

        cx, cy, w, h = predictions[:, 0], predictions[:, 1], predictions[:, 2], predictions[:, 3]
        boxes = np.stack([cx - w / 2, cy - h / 2, cx + w / 2, cy + h / 2], axis=1)

        # Class-aware NMS: offset each class far apart so boxes of different
        # classes never suppress each other (same effect as Ultralytics).
        offset = best_class[:, None].astype(np.float32) * (size * 2.0)
        kept = nms(boxes + offset, best_score, settings.iou_threshold)[: settings.max_detections]

        detections = []
        for i in kept:
            x1, y1, x2, y2 = boxes[i]
            original = [(x1 - pad_x) / scale, (y1 - pad_y) / scale, (x2 - pad_x) / scale, (y2 - pad_y) / scale]
            bbox = clean_box(original, width, height)
            if bbox is None:
                continue
            detections.append(
                RawDetection(
                    category=config.CATEGORIES[int(best_class[i])],
                    confidence=min(max(float(best_score[i]), 0.0), 1.0),
                    bbox=bbox,
                )
            )
        return detections
