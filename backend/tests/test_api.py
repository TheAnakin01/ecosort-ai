"""API tests. They use a fake detector, so PyTorch and weights are not needed.

Run from the backend/ folder:  pytest
"""

import io
import time

import pytest
from fastapi.testclient import TestClient
from PIL import Image

from app import config
from app.config import SettingsError, load_settings
from app.detector import RawDetection, clean_box
from app.main import app, get_detector

CATEGORIES = ["paper", "plastic", "metal", "organic"]


class FakeDetector:
    def __init__(self, detections=(), error: Exception | None = None, delay: float = 0.0) -> None:
        self.detections = list(detections)
        self.error = error
        self.delay = delay
        self.seen: Image.Image | None = None

    def detect(self, image: Image.Image) -> list[RawDetection]:
        self.seen = image
        time.sleep(self.delay)
        if self.error:
            raise self.error
        return self.detections


def image_bytes(size=(640, 480), fmt="JPEG", mode="RGB", exif_orientation=None) -> bytes:
    image = Image.new(mode, size)
    buffer = io.BytesIO()
    if exif_orientation is not None:
        exif = Image.Exif()
        exif[0x0112] = exif_orientation
        image.save(buffer, format=fmt, exif=exif)
    else:
        image.save(buffer, format=fmt)
    return buffer.getvalue()


@pytest.fixture
def client():
    yield TestClient(app)
    app.dependency_overrides.clear()


def use_detector(*args, **kwargs) -> FakeDetector:
    fake = FakeDetector(*args, **kwargs)
    app.dependency_overrides[get_detector] = lambda: fake
    return fake


def upload(client, data: bytes, name="photo.jpg", mime="image/jpeg"):
    return client.post("/api/v1/detect", files={"file": (name, data, mime)})


def assert_error(response, status: int, code: str) -> dict:
    """Check the response is in the agreed error shape, and return its body."""
    assert response.status_code == status, response.text
    body = response.json()
    assert set(body) == {"success", "error", "request_id"}
    assert body["success"] is False
    assert body["error"]["code"] == code
    assert body["error"]["message"]
    assert body["request_id"] == response.headers["X-Request-ID"]
    return body


# ---------- successful scans ----------


def test_multiple_objects_are_counted_and_sorted(client):
    use_detector(
        [
            RawDetection("paper", 0.62, [400, 120, 600, 400]),
            RawDetection("plastic", 0.96, [120, 80, 250, 390]),
            RawDetection("plastic", 0.81, [10, 10, 90, 200]),
        ]
    )
    body = upload(client, image_bytes()).json()

    assert body["success"] is True
    assert (body["image_width"], body["image_height"]) == (640, 480)
    assert body["total_objects"] == len(body["detections"]) == sum(body["counts"].values()) == 3
    assert body["counts"] == {"paper": 1, "plastic": 2, "metal": 0, "organic": 0}
    assert [d["confidence"] for d in body["detections"]] == [0.96, 0.81, 0.62]
    assert [d["id"] for d in body["detections"]] == [1, 2, 3]
    assert body["detections"][0]["bbox"] == [120, 80, 250, 390]
    assert body["model_version"] == config.settings.model_version
    assert body["message"] is None


def test_no_detections_returns_empty_result_not_an_error(client):
    use_detector([])
    response = upload(client, image_bytes())
    body = response.json()

    assert response.status_code == 200
    assert body["success"] is True
    assert body["total_objects"] == 0
    assert body["detections"] == []
    assert body["counts"] == {"paper": 0, "plastic": 0, "metal": 0, "organic": 0}
    assert "No supported waste items were detected" in body["message"]


def test_low_confidence_is_flagged(client):
    use_detector([RawDetection("metal", 0.4, [0, 0, 50, 50]), RawDetection("paper", 0.9, [60, 60, 90, 90])])
    body = upload(client, image_bytes()).json()

    assert [d["low_confidence"] for d in body["detections"]] == [False, True]
    assert "estimates" in body["message"]


def test_rotated_phone_photo_is_turned_upright(client):
    fake = use_detector([])
    # Orientation 6 means the stored 640x480 pixels should display as 480x640.
    body = upload(client, image_bytes(exif_orientation=6)).json()

    assert fake.seen.size == (480, 640)
    assert (body["image_width"], body["image_height"]) == (480, 640)


@pytest.mark.parametrize(("mode", "fmt"), [("L", "JPEG"), ("RGBA", "PNG"), ("P", "PNG"), ("RGB", "WEBP")])
def test_grey_transparent_and_webp_images_are_accepted(client, mode, fmt):
    fake = use_detector([])
    response = upload(client, image_bytes(mode=mode, fmt=fmt))

    assert response.status_code == 200
    assert fake.seen.mode == "RGB"


def test_format_is_judged_by_content_not_by_name(client):
    use_detector([])
    # A real PNG with a misleading name and type is fine.
    assert upload(client, image_bytes(fmt="PNG"), name="notes.txt", mime="text/plain").status_code == 200
    # A BMP dressed up as a JPEG is not.
    assert_error(upload(client, image_bytes(fmt="BMP"), name="photo.jpg"), 415, "UNSUPPORTED_IMAGE")


def test_every_response_has_its_own_request_id(client):
    use_detector([])
    first = upload(client, image_bytes()).headers["X-Request-ID"]
    second = upload(client, image_bytes()).headers["X-Request-ID"]
    assert first and second and first != second


# ---------- rejected uploads ----------


def test_rejects_empty_file(client):
    use_detector([])
    assert_error(upload(client, b""), 400, "EMPTY_FILE")


def test_rejects_file_that_is_not_an_image(client):
    use_detector([])
    assert_error(upload(client, b"this is not an image"), 422, "INVALID_IMAGE")


def test_any_failure_to_open_the_file_counts_as_an_invalid_image(client, monkeypatch):
    """Found with a real model: Ultralytics hooks into image opening and raised an
    error type the backend did not expect, which surfaced as a server crash."""

    def hooked_open(*_args, **_kwargs):
        raise ModuleNotFoundError("No module named 'pi_heif'")

    use_detector([])
    monkeypatch.setattr("app.main.Image.open", hooked_open)
    assert_error(upload(client, b"this is not an image"), 422, "INVALID_IMAGE")


def test_rejects_truncated_image(client):
    use_detector([])
    data = image_bytes(size=(800, 600))
    assert_error(upload(client, data[: len(data) // 2]), 422, "INVALID_IMAGE")


def test_rejects_unsupported_format(client):
    use_detector([])
    assert_error(upload(client, image_bytes(fmt="GIF", mode="P"), name="photo.gif"), 415, "UNSUPPORTED_IMAGE")


def test_rejects_oversized_upload(client, monkeypatch):
    use_detector([])
    monkeypatch.setattr(config.settings, "max_upload_bytes", 100)
    assert_error(upload(client, image_bytes()), 413, "UPLOAD_TOO_LARGE")


def test_rejects_too_many_pixels_before_decoding(client, monkeypatch):
    fake = use_detector([])
    monkeypatch.setattr(config.settings, "max_image_pixels", 100 * 100)
    assert_error(upload(client, image_bytes(size=(200, 200))), 422, "IMAGE_DIMENSIONS")
    assert fake.seen is None


def test_rejects_image_with_a_very_long_side(client, monkeypatch):
    use_detector([])
    monkeypatch.setattr(config.settings, "max_image_side", 300)
    assert_error(upload(client, image_bytes(size=(400, 20))), 422, "IMAGE_DIMENSIONS")


def test_request_without_a_file_is_malformed(client):
    use_detector([])
    assert_error(client.post("/api/v1/detect"), 400, "MALFORMED_REQUEST")


# ---------- model and server failures ----------


def test_model_not_loaded_returns_503_not_a_fake_result(client):
    assert_error(upload(client, image_bytes()), 503, "MODEL_UNAVAILABLE")


def test_server_starts_without_weights_and_reports_it(monkeypatch, tmp_path):
    monkeypatch.setattr(config.settings, "model_path", tmp_path / "missing.pt")
    with TestClient(app) as started:
        assert started.get("/health").json() == {"status": "ok", "model_loaded": False}
        assert started.get("/api/v1/model-info").json()["model_loaded"] is False
        assert_error(upload(started, image_bytes()), 503, "MODEL_UNAVAILABLE")


def test_inference_failure_returns_500_without_leaking_details(client):
    use_detector(error=RuntimeError("CUDA exploded at /srv/secret/path"))
    response = upload(client, image_bytes())

    assert_error(response, 500, "INFERENCE_FAILED")
    assert "CUDA" not in response.text and "secret" not in response.text


def test_slow_inference_returns_504(client, monkeypatch):
    use_detector(delay=0.5)
    monkeypatch.setattr(config.settings, "inference_timeout_seconds", 0.05)
    assert_error(upload(client, image_bytes()), 504, "INFERENCE_TIMEOUT")


def test_unexpected_error_returns_500_without_leaking_details(monkeypatch):
    def broken(_data):
        raise RuntimeError("database password is hunter2")

    use_detector([])
    monkeypatch.setattr("app.main.read_image", broken)
    quiet_client = TestClient(app, raise_server_exceptions=False)
    try:
        response = upload(quiet_client, image_bytes())
    finally:
        app.dependency_overrides.clear()

    assert_error(response, 500, "INTERNAL_ERROR")
    assert "hunter2" not in response.text


def test_unknown_address_uses_the_error_shape(client):
    assert_error(client.get("/api/v1/nothing-here"), 404, "NOT_FOUND")


# ---------- other endpoints ----------


def test_health_without_a_model(client):
    assert client.get("/health").json() == {"status": "ok", "model_loaded": False}


def test_categories(client):
    body = client.get("/api/v1/categories").json()
    assert [c["name"] for c in body["categories"]] == CATEGORIES
    assert [c["id"] for c in body["categories"]] == [0, 1, 2, 3]
    assert body["categories"][3] == {
        "id": 3,
        "name": "organic",
        "label": "Organic",
        "guidance": "/api/v1/guidance/organic",
    }
    # Every guidance link works.
    for category in body["categories"]:
        assert client.get(category["guidance"]).status_code == 200


def test_guidance_for_known_and_unknown_category(client):
    body = client.get("/api/v1/guidance/Organic").json()
    assert body["category"] == "organic"
    assert body["bin"] == "Wet waste"
    assert body["tips"]
    assert "vary by location" in body["disclaimer"]

    assert_error(client.get("/api/v1/guidance/glass"), 404, "UNKNOWN_CATEGORY")


def test_model_info(client):
    body = client.get("/api/v1/model-info").json()
    assert body["classes"] == CATEGORIES
    assert body["model_name"] == config.settings.model_name
    assert body["model_version"] == config.settings.model_version
    assert body["model_loaded"] is False
    assert 0 < body["confidence_threshold"] <= body["low_confidence_threshold"] < 1
    assert 0 < body["iou_threshold"] < 1
    assert "model_path" not in body


def test_error_responses_carry_cors_headers_too(monkeypatch):
    """Otherwise a browser reports every server error as "could not connect"."""
    site = {"Origin": "https://theanakin01.github.io"}

    def broken(_data):
        raise RuntimeError("boom")

    use_detector([])
    quiet_client = TestClient(app, raise_server_exceptions=False)
    try:
        rejected = quiet_client.post("/api/v1/detect", files={"file": ("a.jpg", b"", "image/jpeg")}, headers=site)
        monkeypatch.setattr("app.main.read_image", broken)
        crashed = quiet_client.post(
            "/api/v1/detect", files={"file": ("a.jpg", image_bytes(), "image/jpeg")}, headers=site
        )
    finally:
        app.dependency_overrides.clear()

    assert rejected.status_code == 400 and crashed.status_code == 500
    for response in (rejected, crashed):
        assert response.headers["access-control-allow-origin"] == site["Origin"]


def test_cors_allows_only_configured_sites(client):
    allowed = client.get("/health", headers={"Origin": "https://theanakin01.github.io"})
    assert allowed.headers["access-control-allow-origin"] == "https://theanakin01.github.io"

    other = client.get("/health", headers={"Origin": "https://example.com"})
    assert "access-control-allow-origin" not in other.headers


# ---------- settings and box clean-up ----------


@pytest.mark.parametrize(
    ("name", "value"),
    [
        ("CONFIDENCE_THRESHOLD", "1.5"),
        ("CONFIDENCE_THRESHOLD", "abc"),
        ("LOW_CONFIDENCE_THRESHOLD", "0.1"),  # below CONFIDENCE_THRESHOLD
        ("IOU_THRESHOLD", "0"),
        ("IMAGE_SIZE", "500"),  # not a multiple of 32
        ("IMAGE_SIZE", "big"),
        ("MAX_DETECTIONS", "0"),
        ("MAX_UPLOAD_MB", "-1"),
        ("INFERENCE_TIMEOUT_SECONDS", "0"),
        ("MODEL_VERSION", " "),
    ],
)
def test_bad_settings_are_rejected_at_startup(monkeypatch, name, value):
    monkeypatch.setenv(name, value)
    with pytest.raises(SettingsError):
        load_settings()


def test_settings_are_read_from_the_environment(monkeypatch):
    monkeypatch.setenv("MODEL_VERSION", "0.3.1")
    monkeypatch.setenv("CORS_ORIGINS", "https://a.example, https://b.example")
    settings = load_settings()
    assert settings.model_version == "0.3.1"
    assert settings.image_size is None  # "auto" by default

    monkeypatch.setenv("IMAGE_SIZE", "416")
    assert load_settings().image_size == 416
    assert settings.cors_origins == ["https://a.example", "https://b.example"]


@pytest.mark.parametrize(
    ("box", "expected"),
    [
        ([10.4, 20.6, 100.5, 200.2], [10, 21, 100, 200]),
        ([-5, -5, 50, 50], [0, 0, 50, 50]),  # clipped to the top-left corner
        ([600, 400, 700, 500], [600, 400, 640, 480]),  # clipped to the bottom-right corner
        ([0, 0, 640, 480], [0, 0, 640, 480]),  # the whole image
        ([100.2, 100, 100.4, 300], None),  # rounds to no width
        ([650, 10, 700, 50], None),  # entirely outside
    ],
)
def test_clean_box(box, expected):
    assert clean_box(box, 640, 480) == expected
