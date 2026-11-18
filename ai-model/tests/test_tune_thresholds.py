"""Tests for the threshold sweep and recommendation. Need no PyTorch."""

import sys
from pathlib import Path

SCRIPTS = Path(__file__).resolve().parent.parent / "scripts"
sys.path.insert(0, str(SCRIPTS))

from tune_thresholds import recommend, score_at  # noqa: E402

ITEM = (0.1, 0.1, 0.4, 0.4)
OTHER = (0.6, 0.6, 0.9, 0.9)
EMPTY = (0.45, 0.0, 0.55, 0.05)


def test_score_counts_what_the_app_would_show():
    images = [
        (
            [(0, 0.9, ITEM), (1, 0.3, OTHER), (2, 0.2, EMPTY)],  # correct, wrong class, on nothing
            [(0, ITEM), (0, OTHER)],
        )
    ]
    low = score_at(images, 0.1)
    assert (low["shown"], low["correct"]) == (3, 1)
    assert low["precision"] == round(1 / 3, 4) and low["recall"] == 0.5
    assert low["share_on_nothing"] == round(1 / 3, 4)
    high = score_at(images, 0.5)
    assert (high["shown"], high["precision"], high["recall"], high["share_on_nothing"]) == (1, 1.0, 0.5, 0.0)


def test_no_boxes_gives_zeroes_not_errors():
    row = score_at([([], [(0, ITEM)])], 0.5)
    assert row == {**row, "shown": 0, "precision": 0.0, "recall": 0.0, "f1": 0.0, "share_on_nothing": 0.0}


def row(t, f1, precision, on_nothing, shown=1000):
    return {"threshold": t, "shown": shown, "f1": f1, "precision": precision, "share_on_nothing": on_nothing}


def test_recommends_best_f1_within_hallucination_cap():
    rows = [row(0.2, 0.80, 0.70, 0.10), row(0.3, 0.75, 0.80, 0.04), row(0.4, 0.70, 0.86, 0.02), row(0.5, 0.6, 0.9, 0.0)]
    choice = recommend(rows, max_on_nothing=0.05, sure_precision=0.85)
    assert choice["confidence_threshold"] == 0.3  # 0.2 has better F1 but too many boxes on nothing
    assert choice["low_confidence_threshold"] == 0.4
    assert choice["note"] is None


def test_falls_back_with_a_note_when_cap_cannot_be_met():
    rows = [row(0.2, 0.8, 0.5, 0.2), row(0.3, 0.7, 0.6, 0.1)]
    choice = recommend(rows, max_on_nothing=0.05, sure_precision=0.85)
    assert choice["confidence_threshold"] == 0.2
    assert choice["low_confidence_threshold"] == 0.3
    assert "no threshold keeps" in choice["note"] and "precision" in choice["note"]


def test_no_boxes_at_all():
    choice = recommend([row(0.2, 0.0, 0.0, 0.0, shown=0)], 0.05, 0.85)
    assert choice["confidence_threshold"] is None


def test_warns_when_too_few_boxes():
    choice = recommend([row(0.2, 0.9, 0.9, 0.0, shown=3)], 0.05, 0.85)
    assert choice["confidence_threshold"] == 0.2 and "too few" in choice["note"]
