"""EcoSort AI backend: receives a photo, runs the detector, returns JSON.

Start it from the backend/ folder:

    uvicorn app.main:app --reload

Then open http://127.0.0.1:8000/docs to try the endpoints in a browser.
"""

import io

from fastapi import Depends, FastAPI, HTTPException, UploadFile
from fastapi.middleware.cors import CORSMiddleware
from PIL import Image, ImageOps, UnidentifiedImageError

from . import config
from .detector import ModelNotAvailable, YoloDetector, get_detector
from .guidance import DISCLAIMER, GUIDANCE
from .schemas import CategoryGuidance, Detection, DetectResponse, ModelInfo

app = FastAPI(title="EcoSort AI", version="0.1.0")

# Lets the Expo app (and Expo web) call the API during development.
app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_methods=["*"], allow_headers=["*"])


def load_detector() -> YoloDetector:
    try:
        return get_detector()
    except ModelNotAvailable as exc:
        raise HTTPException(status_code=503, detail=str(exc)) from exc


def read_image(data: bytes) -> Image.Image:
    """Validate the upload and return it as an upright RGB image."""
    if not data:
        raise HTTPException(status_code=400, detail="The uploaded file is empty.")
    if len(data) > config.MAX_UPLOAD_BYTES:
        raise HTTPException(status_code=413, detail="Image is too large.")
    try:
        image = Image.open(io.BytesIO(data))
        image_format = image.format
        image.load()
    except (UnidentifiedImageError, OSError) as exc:
        raise HTTPException(status_code=400, detail="File is not a readable image.") from exc
    if image_format not in config.ALLOWED_FORMATS:
        raise HTTPException(status_code=415, detail="Use a JPEG, PNG or WebP image.")
    if max(image.size) > config.MAX_IMAGE_SIDE:
        raise HTTPException(status_code=413, detail="Image dimensions are too large.")
    # Phone photos store rotation as metadata. Apply it, so the boxes line up
    # with the picture the user sees.
    return ImageOps.exif_transpose(image).convert("RGB")


@app.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok"}


@app.post("/api/v1/detect", response_model=DetectResponse)
async def detect(file: UploadFile, detector: YoloDetector = Depends(load_detector)) -> DetectResponse:
    image = read_image(await file.read())
    raw = detector.detect(image)

    counts = {category: 0 for category in config.CATEGORIES}
    detections = []
    for number, item in enumerate(sorted(raw, key=lambda d: d.confidence, reverse=True), start=1):
        counts[item.category] += 1
        detections.append(
            Detection(
                id=number,
                category=item.category,
                confidence=round(item.confidence, 3),
                low_confidence=item.confidence < config.LOW_CONFIDENCE_THRESHOLD,
                bbox=item.bbox,
            )
        )

    message = None
    if not detections:
        message = "No waste detected. Try a closer, well-lit photo."
    elif any(d.low_confidence for d in detections):
        message = "Some items are uncertain. Retake the photo for a better result."

    return DetectResponse(
        success=True,
        image_width=image.width,
        image_height=image.height,
        total_objects=len(detections),
        counts=counts,
        detections=detections,
        message=message,
    )


@app.get("/api/v1/categories")
def categories() -> dict[str, list[str]]:
    return {"categories": config.CATEGORIES}


@app.get("/api/v1/guidance/{category}", response_model=CategoryGuidance)
def guidance(category: str) -> CategoryGuidance:
    entry = GUIDANCE.get(category.lower())
    if entry is None:
        raise HTTPException(status_code=404, detail=f"Unknown category: {category}")
    return CategoryGuidance(category=category.lower(), disclaimer=DISCLAIMER, **entry)


@app.get("/api/v1/model-info", response_model=ModelInfo)
def model_info() -> ModelInfo:
    return ModelInfo(
        model_loaded=config.MODEL_PATH.exists(),
        model_version=config.MODEL_VERSION,
        categories=config.CATEGORIES,
        confidence_threshold=config.CONFIDENCE_THRESHOLD,
        low_confidence_threshold=config.LOW_CONFIDENCE_THRESHOLD,
    )
