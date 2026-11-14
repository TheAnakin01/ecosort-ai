"""Checks the API against a real YOLO model, not the fake detector.

These tests are skipped unless you point them at trained weights and a dataset
whose labels are known to be right. The quickest way is the synthetic
coloured-shapes dataset, which trains in a few minutes on a laptop CPU:

    cd ai-model
    python tests/make_synthetic_dataset.py /tmp/synthetic
    python scripts/validate_dataset.py /tmp/synthetic
    python scripts/train.py --data /tmp/synthetic/data.yaml --epochs 30 --imgsz 320 \
        --name smoke --project /tmp/yolo-runs

    cd ../backend
    ECOSORT_TEST_WEIGHTS=/tmp/yolo-runs/smoke/weights/best.pt \
    ECOSORT_TEST_DATASET=/tmp/synthetic pytest tests/test_real_model.py

The synthetic model only knows coloured rectangles. It proves the plumbing
(model loading, inference, box coordinates), not waste detection quality.
"""

import io
import os
from pathlib import Path

import pytest
from fastapi.testclient import TestClient
from PIL import Image

from app import config
from app.main import app

WEIGHTS = os.getenv("ECOSORT_TEST_WEIGHTS")
DATASET = os.getenv("ECOSORT_TEST_DATASET")

pytestmark = pytest.mark.skipif(
    not (WEIGHTS and DATASET), reason="set ECOSORT_TEST_WEIGHTS and ECOSORT_TEST_DATASET to run"
)

MIN_OVERLAP = 0.8


@pytest.fixture(scope="module")
def client():
    pytest.importorskip("ultralytics")
    original = config.settings.model_path
    config.settings.model_path = Path(WEIGHTS)
    # Entering the client starts the app, which loads the model once.
    with TestClient(app) as started:
        assert started.get("/health").json() == {"status": "ok", "model_loaded": True}
        yield started
    config.settings.model_path = original


def examples(limit: int = 8) -> list[Path]:
    return sorted((Path(DATASET) / "images" / "test").glob("*.png"))[:limit]


def expected_boxes(image_path: Path, width: int, height: int) -> list[tuple[str, list[float]]]:
    """Ground-truth boxes for an image, as (category, [x1, y1, x2, y2]) in pixels."""
    label = Path(DATASET) / "labels" / "test" / (image_path.stem + ".txt")
    boxes = []
    for line in label.read_text().splitlines():
        class_id, cx, cy, w, h = line.split()
        cx, cy, w, h = float(cx) * width, float(cy) * height, float(w) * width, float(h) * height
        boxes.append((config.CATEGORIES[int(class_id)], [cx - w / 2, cy - h / 2, cx + w / 2, cy + h / 2]))
    return boxes


def overlap(a: list[float], b: list[float]) -> float:
    """Intersection over union of two boxes."""
    width = min(a[2], b[2]) - max(a[0], b[0])
    height = min(a[3], b[3]) - max(a[1], b[1])
    if width <= 0 or height <= 0:
        return 0.0
    shared = width * height
    return shared / ((a[2] - a[0]) * (a[3] - a[1]) + (b[2] - b[0]) * (b[3] - b[1]) - shared)


def assert_matches(body: dict, expected: list[tuple[str, list[float]]]) -> None:
    assert body["total_objects"] == len(body["detections"]) == sum(body["counts"].values())
    for category, box in expected:
        best = max(
            (overlap(box, d["bbox"]) for d in body["detections"] if d["category"] == category),
            default=0.0,
        )
        assert best >= MIN_OVERLAP, f"no {category} detection close to {box}; got {body['detections']}"
    for found in body["detections"]:
        x1, y1, x2, y2 = found["bbox"]
        assert 0 <= x1 < x2 <= body["image_width"] and 0 <= y1 < y2 <= body["image_height"]
        assert 0 <= found["confidence"] <= 1


def upload(client: TestClient, data: bytes, name: str = "photo.png"):
    return client.post("/api/v1/detect", files={"file": (name, data, "image/png")})


def test_real_detections_land_on_the_labelled_objects(client):
    paths = examples()
    assert paths, f"no test images found in {DATASET}"
    for path in paths:
        with Image.open(path) as image:
            width, height = image.size
        response = upload(client, path.read_bytes())
        assert response.status_code == 200, response.text
        body = response.json()
        assert (body["image_width"], body["image_height"]) == (width, height)
        assert_matches(body, expected_boxes(path, width, height))


def test_boxes_follow_a_photo_stored_sideways(client):
    """A phone often stores a photo rotated, with a note saying how to turn it upright.

    The API must return boxes for the upright picture, which is what the app shows.
    """
    path = examples(1)[0]
    with Image.open(path) as upright:
        width, height = upright.size
        # Store the pixels turned 90 degrees clockwise. EXIF orientation 8 tells
        # a viewer to turn them 90 degrees anticlockwise, restoring the original.
        stored = upright.transpose(Image.Transpose.ROTATE_270)
    exif = Image.Exif()
    exif[0x0112] = 8
    buffer = io.BytesIO()
    stored.save(buffer, format="JPEG", quality=95, exif=exif)

    response = upload(client, buffer.getvalue(), name="photo.jpg")
    assert response.status_code == 200, response.text
    body = response.json()
    assert (body["image_width"], body["image_height"]) == (width, height)
    assert_matches(body, expected_boxes(path, width, height))


def test_model_is_loaded_once_and_reused(client):
    loaded = app.state.detector
    # By default the model runs at the image size it was trained with.
    assert client.get("/api/v1/model-info").json()["image_size"] == loaded.image_size > 0
    upload(client, examples(1)[0].read_bytes())
    upload(client, examples(1)[0].read_bytes())
    assert loaded is not None and app.state.detector is loaded


def test_weights_for_other_classes_are_refused(tmp_path):
    """Loading a model trained for different classes must fail, not mislabel everything."""
    other = os.getenv("ECOSORT_TEST_OTHER_WEIGHTS")
    if not other:
        pytest.skip("set ECOSORT_TEST_OTHER_WEIGHTS to weights with different classes, such as yolo11n.pt")
    # Starting a second client restarts the app, so put the good model back afterwards.
    original_path, original_detector = config.settings.model_path, app.state.detector
    config.settings.model_path = Path(other)
    try:
        with TestClient(app) as started:
            assert started.get("/health").json()["model_loaded"] is False
            assert upload(started, examples(1)[0].read_bytes()).status_code == 503
    finally:
        config.settings.model_path, app.state.detector = original_path, original_detector


def test_picture_with_no_objects_returns_an_empty_result(client):
    buffer = io.BytesIO()
    Image.new("RGB", (320, 240), (120, 120, 120)).save(buffer, format="PNG")
    body = upload(client, buffer.getvalue()).json()
    assert body["success"] is True
    assert body["detections"] == []
    assert body["counts"] == {"paper": 0, "plastic": 0, "metal": 0, "organic": 0}
    assert body["model_version"] == config.settings.model_version
