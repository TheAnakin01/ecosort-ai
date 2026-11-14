"""Shapes of the JSON the API returns. The mobile app relies on these."""

from pydantic import BaseModel, ConfigDict


class Detection(BaseModel):
    id: int
    category: str
    confidence: float
    low_confidence: bool
    bbox: list[int]  # [x1, y1, x2, y2] in pixels of the original image


class DetectResponse(BaseModel):
    success: bool
    image_width: int
    image_height: int
    total_objects: int
    counts: dict[str, int]
    detections: list[Detection]
    message: str | None = None


class CategoryGuidance(BaseModel):
    category: str
    bin: str
    tips: list[str]
    disclaimer: str


class ModelInfo(BaseModel):
    # Allow field names that start with "model_".
    model_config = ConfigDict(protected_namespaces=())

    model_loaded: bool
    model_version: str
    categories: list[str]
    confidence_threshold: float
    low_confidence_threshold: float
