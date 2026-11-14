"""Shapes of the JSON the API returns. The mobile app relies on these."""

from pydantic import BaseModel, ConfigDict


class Detection(BaseModel):
    id: int
    category: str
    confidence: float
    low_confidence: bool
    bbox: list[int]  # [x1, y1, x2, y2] in pixels of the upright image


class DetectResponse(BaseModel):
    # Allow field names that start with "model_".
    model_config = ConfigDict(protected_namespaces=())

    success: bool
    image_width: int
    image_height: int
    total_objects: int
    counts: dict[str, int]
    detections: list[Detection]
    model_version: str
    message: str | None = None


class Category(BaseModel):
    id: int
    name: str
    label: str
    guidance: str  # path of the guidance endpoint for this category


class CategoriesResponse(BaseModel):
    categories: list[Category]


class CategoryGuidance(BaseModel):
    category: str
    bin: str
    tips: list[str]
    disclaimer: str


class Health(BaseModel):
    model_config = ConfigDict(protected_namespaces=())

    status: str
    model_loaded: bool


class ModelInfo(BaseModel):
    model_config = ConfigDict(protected_namespaces=())

    model_name: str
    model_version: str
    model_loaded: bool
    classes: list[str]
    confidence_threshold: float
    low_confidence_threshold: float
    iou_threshold: float
    image_size: int | None  # None until a model is loaded, unless IMAGE_SIZE is set


class ErrorDetail(BaseModel):
    code: str
    message: str


class ErrorResponse(BaseModel):
    success: bool = False
    error: ErrorDetail
    request_id: str
