"""Unit tests for the ONNX detector's pre- and post-processing (no model file needed)."""

import numpy as np
import pytest
from PIL import Image

pytest.importorskip("cv2")

from app.onnx_detector import STRIDE, letterbox, nms  # noqa: E402


def test_letterbox_long_side_is_size_and_padding_is_minimal():
    tensor, scale, left, top = letterbox(Image.new("RGB", (1280, 720), (10, 20, 30)), 640)
    assert tensor.dtype == np.float32 and tensor.shape[:2] == (1, 3)
    assert tensor.shape[3] == 640 and tensor.shape[2] % STRIDE == 0 and tensor.shape[2] < 640
    assert scale == 0.5 and left == 0.0 and top > 0


def test_letterbox_values_are_rgb_in_unit_range_with_grey_padding():
    tensor, _, _, top = letterbox(Image.new("RGB", (640, 320), (255, 0, 0)), 640)
    assert tensor.max() <= 1.0
    red = tensor[0, :, 160, 320]  # channel order is R, G, B
    assert red.tolist() == [1.0, 0.0, 0.0]
    if top:
        assert tensor[0, 0, 0, 0] == pytest.approx(114 / 255)


def test_nms_removes_overlap_and_keeps_highest_score():
    boxes = np.array([[0, 0, 100, 100], [5, 5, 105, 105], [300, 300, 400, 400]], dtype=np.float32)
    scores = np.array([0.6, 0.9, 0.5], dtype=np.float32)
    assert nms(boxes, scores, 0.7) == [1, 2]


def test_nms_keeps_overlapping_boxes_when_below_threshold():
    boxes = np.array([[0, 0, 100, 100], [60, 0, 160, 100]], dtype=np.float32)
    assert nms(boxes, np.array([0.9, 0.8], dtype=np.float32), 0.7) == [0, 1]
