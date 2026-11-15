"""Checks that the ONNX model gives the same detections as the .pt weights.

Skipped unless pointed at both files (and Ultralytics is installed):

    ECOSORT_TEST_WEIGHTS=best.pt ECOSORT_TEST_ONNX=best.onnx \
    ECOSORT_TEST_IMAGES=/path/to/photos pytest tests/test_onnx_parity.py

ECOSORT_TEST_IMAGES is a folder of .jpg/.png files. Use real waste photos for a
meaningful check; without it, the sample images shipped with Ultralytics are used.
The test compares at a very low confidence so that many boxes are compared.
"""

import dataclasses
import os
from pathlib import Path

import pytest
from PIL import Image

PT = os.getenv("ECOSORT_TEST_WEIGHTS")
ONNX = os.getenv("ECOSORT_TEST_ONNX")
IMAGES = os.getenv("ECOSORT_TEST_IMAGES")

pytestmark = pytest.mark.skipif(not (PT and ONNX), reason="set ECOSORT_TEST_WEIGHTS and ECOSORT_TEST_ONNX to run")

BOX_TOLERANCE_PX = 2
CONFIDENCE_TOLERANCE = 0.01


def image_paths() -> list[Path]:
    if IMAGES:
        folder = Path(IMAGES)
    else:
        ultralytics = pytest.importorskip("ultralytics")
        folder = Path(ultralytics.__file__).parent / "assets"
    paths = sorted(p for p in folder.iterdir() if p.suffix.lower() in {".jpg", ".jpeg", ".png"})
    assert paths, f"no images in {folder}"
    return paths


def test_onnx_matches_pytorch_detections():
    pytest.importorskip("ultralytics")
    from app.config import load_settings
    from app.detector import YoloDetector
    from app.onnx_detector import OnnxDetector

    base = dataclasses.replace(load_settings(), confidence_threshold=0.05, low_confidence_threshold=0.5)
    pt = YoloDetector(dataclasses.replace(base, model_path=Path(PT)))
    onnx = OnnxDetector(dataclasses.replace(base, model_path=Path(ONNX)))
    assert pt.image_size == onnx.image_size

    for path in image_paths():
        image = Image.open(path).convert("RGB")
        expected = sorted(pt.detect(image), key=lambda d: (-d.confidence, d.bbox))
        actual = sorted(onnx.detect(image), key=lambda d: (-d.confidence, d.bbox))
        assert len(actual) == len(expected), f"{path.name}: {len(actual)} vs {len(expected)} detections"
        for a, e in zip(actual, expected, strict=True):
            assert a.category == e.category, path.name
            assert abs(a.confidence - e.confidence) <= CONFIDENCE_TOLERANCE, path.name
            assert max(abs(x - y) for x, y in zip(a.bbox, e.bbox, strict=True)) <= BOX_TOLERANCE_PX, path.name
