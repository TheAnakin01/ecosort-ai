"""EcoSort AI backend: receives a photo, runs the detector, returns JSON.

Start it from the backend/ folder:

    uvicorn app.main:app --reload

Then open http://127.0.0.1:8000/docs to try the endpoints in a browser.
"""

import asyncio
import io
import logging
import time
import uuid
import warnings
from contextlib import asynccontextmanager

from fastapi import Depends, FastAPI, Request, UploadFile
from fastapi.concurrency import run_in_threadpool
from fastapi.exceptions import RequestValidationError
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from PIL import Image, ImageOps
from starlette.exceptions import HTTPException as StarletteHTTPException

from . import config, errors
from .detector import YoloDetector, load_detector
from .errors import ApiError
from .guidance import DISCLAIMER, GUIDANCE, NO_DETECTIONS_MESSAGE, UNCERTAIN_MESSAGE
from .schemas import (
    CategoriesResponse,
    Category,
    CategoryGuidance,
    Detection,
    DetectResponse,
    Health,
    ModelInfo,
)

logger = logging.getLogger("ecosort")


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Load the model once, when the server starts. If it cannot be loaded the
    # server still runs, and /api/v1/detect answers 503 until it is fixed.
    if not logging.getLogger().handlers:
        logging.basicConfig(level=logging.INFO, format="%(levelname)s %(name)s: %(message)s")
    app.state.detector = load_detector(config.settings)
    yield
    app.state.detector = None


app = FastAPI(title="EcoSort AI", version="0.2.0", lifespan=lifespan)


# ---------- request ids and error responses ----------


def request_id_of(request: Request) -> str:
    return getattr(request.state, "request_id", "unknown")


def error_response(request: Request, status_code: int, code: str, message: str) -> JSONResponse:
    request_id = request_id_of(request)
    return JSONResponse(
        status_code=status_code,
        content={"success": False, "error": {"code": code, "message": message}, "request_id": request_id},
        headers={"X-Request-ID": request_id},
    )


@app.middleware("http")
async def add_request_id(request: Request, call_next):
    """Give every request an id, and log how long it took. Never logs image data."""
    request.state.request_id = uuid.uuid4().hex
    started = time.perf_counter()
    try:
        response = await call_next(request)
    except Exception:
        # Anything nobody expected. The details go to the server log only,
        # never to the client.
        logger.exception("Unexpected error (request %s)", request.state.request_id)
        response = error_response(request, 500, "INTERNAL_ERROR", "Something went wrong on the server. Try again.")
    response.headers["X-Request-ID"] = request.state.request_id
    logger.info(
        "%s %s -> %s in %.0f ms (request %s)",
        request.method,
        request.url.path,
        response.status_code,
        (time.perf_counter() - started) * 1000,
        request.state.request_id,
    )
    return response


@app.exception_handler(ApiError)
async def handle_api_error(request: Request, exc: ApiError) -> JSONResponse:
    return error_response(request, exc.status_code, exc.code, exc.message)


@app.exception_handler(RequestValidationError)
async def handle_bad_request(request: Request, exc: RequestValidationError) -> JSONResponse:
    return error_response(
        request, 400, "MALFORMED_REQUEST", 'The request was not in the expected format. Send the image as "file".'
    )


@app.exception_handler(StarletteHTTPException)
async def handle_http_error(request: Request, exc: StarletteHTTPException) -> JSONResponse:
    known = {404: ("NOT_FOUND", "This address does not exist."), 405: ("METHOD_NOT_ALLOWED", "Method not allowed.")}
    code, message = known.get(exc.status_code, ("HTTP_ERROR", "The request could not be handled."))
    return error_response(request, exc.status_code, code, message)


# Added last so it wraps everything above, including error responses. Without
# that, a browser hides the real error behind a generic "blocked" message.
app.add_middleware(
    CORSMiddleware,
    allow_origins=config.settings.cors_origins,
    allow_methods=["GET", "POST"],
    allow_headers=["*"],
    expose_headers=["X-Request-ID"],
)


# ---------- helpers ----------


def loaded_detector(request: Request) -> YoloDetector | None:
    return getattr(request.app.state, "detector", None)


def get_detector(request: Request) -> YoloDetector:
    """The loaded model, or a 503 error. Tests replace this with a fake detector."""
    detector = loaded_detector(request)
    if detector is None:
        raise errors.model_unavailable()
    return detector


def read_image(data: bytes) -> Image.Image:
    """Validate the upload and return it as an upright RGB image."""
    settings = config.settings
    if not data:
        raise errors.empty_file()
    if len(data) > settings.max_upload_bytes:
        raise errors.upload_too_large(settings.max_upload_bytes // (1024 * 1024))

    try:
        with warnings.catch_warnings():
            # Treat "this image is suspiciously huge" as a failure, not a warning.
            warnings.simplefilter("error", Image.DecompressionBombWarning)
            image = Image.open(io.BytesIO(data))
    except (Image.DecompressionBombWarning, Image.DecompressionBombError) as exc:
        raise errors.image_dimensions() from exc
    except Exception as exc:
        # Any other failure means the bytes are not a usable image. This is
        # deliberately broad: image libraries, and libraries that hook into
        # them, raise many different error types for bad files.
        raise errors.invalid_image() from exc

    # Trust what the file actually is, not its name or the type the client claims.
    if image.format not in config.ALLOWED_FORMATS:
        raise errors.unsupported_image()

    # Check the size before decoding the pixels, so a tiny file that expands
    # into a gigantic image is rejected without using the memory.
    width, height = image.size
    if max(width, height) > settings.max_image_side or width * height > settings.max_image_pixels:
        raise errors.image_dimensions()

    try:
        image.load()
        # Phone photos store rotation as metadata. Apply it, so the boxes line
        # up with the picture the user sees. Also turns grey or transparent
        # images into plain RGB.
        return ImageOps.exif_transpose(image).convert("RGB")
    except Exception as exc:
        raise errors.invalid_image() from exc


# ---------- endpoints ----------


@app.get("/health", response_model=Health)
def health(request: Request) -> Health:
    return Health(status="ok", model_loaded=loaded_detector(request) is not None)


@app.post("/api/v1/detect", response_model=DetectResponse)
async def detect(
    request: Request, file: UploadFile, detector: YoloDetector = Depends(get_detector)
) -> DetectResponse:
    settings = config.settings
    # Read one byte past the limit: enough to know the upload is too large
    # without holding an unlimited amount in memory.
    image = read_image(await file.read(settings.max_upload_bytes + 1))

    try:
        # Inference is slow CPU work, so it runs in a worker thread and the
        # server stays free to answer other requests.
        raw = await asyncio.wait_for(
            run_in_threadpool(detector.detect, image), timeout=settings.inference_timeout_seconds
        )
    except asyncio.TimeoutError as exc:
        raise errors.inference_timeout() from exc
    except Exception as exc:
        logger.exception("Inference failed (request %s)", request_id_of(request))
        raise errors.inference_failed() from exc

    counts = {category: 0 for category in config.CATEGORIES}
    detections = []
    # Highest confidence first, so the order is the same every time.
    for number, item in enumerate(sorted(raw, key=lambda d: d.confidence, reverse=True), start=1):
        counts[item.category] += 1
        detections.append(
            Detection(
                id=number,
                category=item.category,
                confidence=round(item.confidence, 3),
                low_confidence=item.confidence < settings.low_confidence_threshold,
                bbox=item.bbox,
            )
        )

    message = None
    if not detections:
        message = NO_DETECTIONS_MESSAGE
    elif any(d.low_confidence for d in detections):
        message = UNCERTAIN_MESSAGE

    return DetectResponse(
        success=True,
        image_width=image.width,
        image_height=image.height,
        total_objects=len(detections),
        counts=counts,
        detections=detections,
        model_version=settings.model_version,
        message=message,
    )


@app.get("/api/v1/categories", response_model=CategoriesResponse)
def categories() -> CategoriesResponse:
    return CategoriesResponse(
        categories=[
            Category(id=index, name=name, label=config.CATEGORY_LABELS[name], guidance=f"/api/v1/guidance/{name}")
            for index, name in enumerate(config.CATEGORIES)
        ]
    )


@app.get("/api/v1/guidance/{category}", response_model=CategoryGuidance)
def guidance(category: str) -> CategoryGuidance:
    entry = GUIDANCE.get(category.lower())
    if entry is None:
        raise errors.unknown_category(category)
    return CategoryGuidance(category=category.lower(), disclaimer=DISCLAIMER, **entry)


@app.get("/api/v1/model-info", response_model=ModelInfo)
def model_info(request: Request) -> ModelInfo:
    settings = config.settings
    detector = loaded_detector(request)
    return ModelInfo(
        model_name=settings.model_name,
        model_version=settings.model_version,
        model_loaded=detector is not None,
        classes=config.CATEGORIES,
        confidence_threshold=settings.confidence_threshold,
        low_confidence_threshold=settings.low_confidence_threshold,
        iou_threshold=settings.iou_threshold,
        image_size=getattr(detector, "image_size", None) or settings.image_size,
    )
