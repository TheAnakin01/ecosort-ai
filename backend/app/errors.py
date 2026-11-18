"""One error shape for every failure, so the app can rely on it.

    {"success": false, "error": {"code": "...", "message": "..."}, "request_id": "..."}

Messages are written for the person using the app. They never contain stack
traces or file paths.
"""


class ApiError(Exception):
    def __init__(self, status_code: int, code: str, message: str) -> None:
        super().__init__(message)
        self.status_code = status_code
        self.code = code
        self.message = message
        self.headers: dict[str, str] = {}


def empty_file() -> ApiError:
    return ApiError(400, "EMPTY_FILE", "The uploaded file is empty.")


def upload_too_large(limit_mb: int) -> ApiError:
    return ApiError(413, "UPLOAD_TOO_LARGE", f"This photo is too large. The limit is {limit_mb} MB.")


def unsupported_image() -> ApiError:
    return ApiError(415, "UNSUPPORTED_IMAGE", "Please upload a JPEG, PNG or WebP image.")


def invalid_image() -> ApiError:
    return ApiError(422, "INVALID_IMAGE", "This file could not be read as an image. Try another photo.")


def image_dimensions() -> ApiError:
    return ApiError(422, "IMAGE_DIMENSIONS", "This photo's dimensions are too large. Try a smaller photo.")


def model_unavailable() -> ApiError:
    return ApiError(503, "MODEL_UNAVAILABLE", "The detection model is not available right now. Try again later.")


def inference_failed() -> ApiError:
    return ApiError(500, "INFERENCE_FAILED", "We couldn't analyze this photo. Try again.")


def inference_timeout() -> ApiError:
    return ApiError(504, "INFERENCE_TIMEOUT", "Analyzing this photo took too long. Try again.")


def unknown_category(name: str) -> ApiError:
    return ApiError(404, "UNKNOWN_CATEGORY", f"Unknown category: {name}")


def rate_limited(retry_after: float) -> ApiError:
    seconds = max(int(retry_after + 0.999), 1)
    error = ApiError(429, "RATE_LIMITED", f"Too many scans in a short time. Try again in {seconds} seconds.")
    error.headers = {"Retry-After": str(seconds)}
    return error
