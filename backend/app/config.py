"""Backend settings, read from environment variables and checked at startup.

See backend/.env.example for the full list with defaults.
"""

import os
from dataclasses import dataclass
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]

# The four canonical classes. The index is the model's class id.
CATEGORIES = ["paper", "plastic", "metal", "organic"]
CATEGORY_LABELS = {"paper": "Paper", "plastic": "Plastic", "metal": "Metal", "organic": "Organic"}

ALLOWED_FORMATS = {"JPEG", "PNG", "WEBP"}

# Web pages allowed to call the API from a browser. Phone apps are not affected.
DEFAULT_CORS_ORIGINS = "http://localhost:8081,http://localhost:19006,https://theanakin01.github.io"


class SettingsError(ValueError):
    """A setting has a value the backend cannot run with."""


@dataclass
class Settings:
    model_path: Path
    model_name: str
    model_version: str
    confidence_threshold: float
    low_confidence_threshold: float
    iou_threshold: float
    image_size: int | None  # None means "the size the model was trained at"
    max_detections: int
    device: str
    inference_timeout_seconds: float
    max_upload_bytes: int
    max_image_side: int
    max_image_pixels: int
    cors_origins: list[str]

    def validate(self) -> None:
        def check(condition: bool, message: str) -> None:
            if not condition:
                raise SettingsError(message)

        check(0 < self.confidence_threshold < 1, "CONFIDENCE_THRESHOLD must be between 0 and 1")
        check(
            self.confidence_threshold <= self.low_confidence_threshold < 1,
            "LOW_CONFIDENCE_THRESHOLD must be at least CONFIDENCE_THRESHOLD and below 1",
        )
        check(0 < self.iou_threshold < 1, "IOU_THRESHOLD must be between 0 and 1")
        check(
            self.image_size is None or (self.image_size >= 32 and self.image_size % 32 == 0),
            'IMAGE_SIZE must be "auto" or a multiple of 32',
        )
        check(self.max_detections >= 1, "MAX_DETECTIONS must be at least 1")
        check(self.inference_timeout_seconds > 0, "INFERENCE_TIMEOUT_SECONDS must be above 0")
        check(self.max_upload_bytes > 0, "MAX_UPLOAD_MB must be above 0")
        check(self.max_image_side >= 32, "MAX_IMAGE_SIDE must be at least 32")
        check(self.max_image_pixels >= 32 * 32, "MAX_IMAGE_MEGAPIXELS is too small")
        check(bool(self.model_version.strip()), "MODEL_VERSION must not be empty")


def _number(name: str, default: str, kind: type):
    raw = os.getenv(name, default)
    try:
        return kind(raw)
    except ValueError:
        raise SettingsError(f"{name} must be a number, got {raw!r}") from None


def _image_size() -> int | None:
    if os.getenv("IMAGE_SIZE", "auto").strip().lower() == "auto":
        return None
    return _number("IMAGE_SIZE", "auto", int)


def load_settings() -> Settings:
    settings = Settings(
        model_path=Path(os.getenv("MODEL_PATH", REPO_ROOT / "ai-model" / "weights" / "best.onnx")),
        model_name=os.getenv("MODEL_NAME", "yolo-nano-waste-detector"),
        model_version=os.getenv("MODEL_VERSION", "baseline"),
        # Detections below this confidence are not returned at all.
        confidence_threshold=_number("CONFIDENCE_THRESHOLD", "0.35", float),
        # Detections below this are returned but flagged as uncertain.
        low_confidence_threshold=_number("LOW_CONFIDENCE_THRESHOLD", "0.5", float),
        # How much two boxes may overlap before the weaker one is removed.
        iou_threshold=_number("IOU_THRESHOLD", "0.7", float),
        # "auto" uses the size the model was trained at, which is what it detects best with.
        image_size=_image_size(),
        max_detections=_number("MAX_DETECTIONS", "100", int),
        # "cpu", "cuda", or "auto" to let the model library choose.
        device=os.getenv("DEVICE", "auto"),
        inference_timeout_seconds=_number("INFERENCE_TIMEOUT_SECONDS", "30", float),
        max_upload_bytes=_number("MAX_UPLOAD_MB", "10", int) * 1024 * 1024,
        max_image_side=_number("MAX_IMAGE_SIDE", "6000", int),
        max_image_pixels=_number("MAX_IMAGE_MEGAPIXELS", "24", int) * 1_000_000,
        cors_origins=[o.strip() for o in os.getenv("CORS_ORIGINS", DEFAULT_CORS_ORIGINS).split(",") if o.strip()],
    )
    settings.validate()
    return settings


settings = load_settings()
