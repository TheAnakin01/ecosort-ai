"""API tests. They use a fake detector, so PyTorch and weights are not needed.

Run from the backend/ folder:  pytest
"""

import io

import pytest
from fastapi.testclient import TestClient
from PIL import Image

from app import config
from app.detector import ModelNotAvailable, RawDetection
from app.main import app, load_detector


class FakeDetector:
    def __init__(self, detections: list[RawDetection]) -> None:
        self.detections = detections
        self.seen_size: tuple[int, int] | None = None

    def detect(self, image: Image.Image) -> list[RawDetection]:
        self.seen_size = image.size
        return self.detections


def image_bytes(size=(640, 480), fmt="JPEG", exif_orientation=None) -> bytes:
    image = Image.new("RGB", size, "white")
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


def use_detector(detections: list[RawDetection]) -> FakeDetector:
    fake = FakeDetector(detections)
    app.dependency_overrides[load_detector] = lambda: fake
    return fake


def upload(client, data: bytes, name="photo.jpg"):
    return client.post("/api/v1/detect", files={"file": (name, data, "image/jpeg")})


def test_health(client):
    assert client.get("/health").json() == {"status": "ok"}


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
    assert body["total_objects"] == 3
    assert body["counts"] == {"paper": 1, "plastic": 2, "metal": 0, "organic": 0}
    assert [d["confidence"] for d in body["detections"]] == [0.96, 0.81, 0.62]
    assert [d["id"] for d in body["detections"]] == [1, 2, 3]
    assert body["detections"][0]["bbox"] == [120, 80, 250, 390]
    assert body["message"] is None


def test_no_detections_returns_empty_result(client):
    use_detector([])
    body = upload(client, image_bytes()).json()

    assert body["success"] is True
    assert body["total_objects"] == 0
    assert body["detections"] == []
    assert "No waste detected" in body["message"]


def test_low_confidence_is_flagged(client):
    use_detector([RawDetection("metal", 0.4, [0, 0, 50, 50])])
    body = upload(client, image_bytes()).json()

    assert body["detections"][0]["low_confidence"] is True
    assert "uncertain" in body["message"]


def test_rotated_phone_photo_is_turned_upright(client):
    fake = use_detector([])
    # Orientation 6 means the stored 640x480 pixels should display as 480x640.
    body = upload(client, image_bytes(exif_orientation=6)).json()

    assert fake.seen_size == (480, 640)
    assert (body["image_width"], body["image_height"]) == (480, 640)


def test_rejects_file_that_is_not_an_image(client):
    use_detector([])
    assert upload(client, b"this is not an image").status_code == 400


def test_rejects_empty_file(client):
    use_detector([])
    assert upload(client, b"").status_code == 400


def test_rejects_unsupported_format(client):
    use_detector([])
    assert upload(client, image_bytes(fmt="BMP"), name="photo.bmp").status_code == 415


def test_rejects_oversized_upload(client, monkeypatch):
    use_detector([])
    monkeypatch.setattr(config, "MAX_UPLOAD_BYTES", 100)
    assert upload(client, image_bytes()).status_code == 413


def test_missing_model_returns_503(client, monkeypatch):
    def no_model():
        raise ModelNotAvailable("No weights file")

    monkeypatch.setattr("app.main.get_detector", no_model)
    response = upload(client, image_bytes())

    assert response.status_code == 503
    assert "No weights file" in response.json()["detail"]


def test_categories(client):
    assert client.get("/api/v1/categories").json() == {
        "categories": ["paper", "plastic", "metal", "organic"]
    }


def test_guidance_for_known_and_unknown_category(client):
    body = client.get("/api/v1/guidance/Organic").json()
    assert body["category"] == "organic"
    assert body["bin"] == "Wet waste"
    assert body["tips"]

    assert client.get("/api/v1/guidance/glass").status_code == 404


def test_model_info(client):
    body = client.get("/api/v1/model-info").json()
    assert body["categories"] == ["paper", "plastic", "metal", "organic"]
    assert body["model_loaded"] is config.MODEL_PATH.exists()
