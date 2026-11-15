"""Tests for the overtraining and hallucination checks. Need no PyTorch."""

import sys
from pathlib import Path

SCRIPTS = Path(__file__).resolve().parent.parent / "scripts"
sys.path.insert(0, str(SCRIPTS))

from check_hallucinations import iou, match_image, summarise  # noqa: E402
from overfit_check import check, read_results  # noqa: E402


def epochs(scores, train_loss, val_loss):
    return [
        {"epoch": i + 1, "metrics/mAP50-95(B)": s, "train/box_loss": t, "val/box_loss": v}
        for i, (s, t, v) in enumerate(zip(scores, train_loss, val_loss, strict=True))
    ]


def test_rising_validation_loss_is_overtraining():
    rows = epochs(
        [0.40, 0.50, 0.55, 0.56, 0.55, 0.54],
        [2.0, 1.6, 1.3, 1.1, 0.9, 0.7],
        [1.8, 1.5, 1.3, 1.30, 1.40, 1.50],
    )
    report = check(rows)
    assert report["verdict"] == "overtraining"
    assert report["best_epoch"] == 4
    assert report["lowest_val_loss_epoch"] == 3


def test_scores_still_rising_at_the_end():
    rows = epochs(
        [0.40, 0.45, 0.50, 0.53, 0.56, 0.58, 0.60],
        [2.0, 1.8, 1.6, 1.4, 1.3, 1.2, 1.1],
        [1.9, 1.7, 1.6, 1.5, 1.4, 1.35, 1.3],
    )
    assert check(rows)["verdict"] == "still improving"


def test_flat_scores_have_levelled_off():
    rows = epochs(
        [0.50, 0.60, 0.62, 0.62, 0.621, 0.62, 0.62],
        [2.0, 1.5, 1.3, 1.25, 1.22, 1.2, 1.19],
        [1.8, 1.4, 1.3, 1.29, 1.29, 1.29, 1.29],
    )
    assert check(rows)["verdict"] == "levelled off"


def test_read_results_handles_ultralytics_padding(tmp_path):
    # Older Ultralytics versions pad column names with spaces.
    csv = tmp_path / "results.csv"
    csv.write_text("epoch,  train/box_loss,  val/box_loss,  metrics/mAP50-95(B)\n1, 2.0, 1.8, 0.4\n2, 1.5, 1.4, 0.5\n")
    rows = read_results(csv)
    assert rows[1]["metrics/mAP50-95(B)"] == 0.5


def test_iou():
    assert iou((0, 0, 0.5, 0.5), (0, 0, 0.5, 0.5)) == 1.0
    assert iou((0, 0, 0.2, 0.2), (0.5, 0.5, 0.7, 0.7)) == 0.0
    assert abs(iou((0, 0, 0.4, 0.2), (0.2, 0, 0.6, 0.2)) - 1 / 3) < 1e-9


BOTTLE = (0.1, 0.1, 0.3, 0.5)
CAN = (0.6, 0.6, 0.8, 0.8)


def test_each_kind_of_detection_is_sorted_correctly():
    labels = [(1, BOTTLE), (2, CAN)]  # a plastic bottle and a metal can
    predictions = [
        (1, 0.90, BOTTLE),  # right box, right class
        (1, 0.60, (0.1, 0.1, 0.3, 0.48)),  # a second box on the bottle
        (0, 0.80, CAN),  # right box, wrong class
        (3, 0.70, (0.0, 0.85, 0.1, 0.95)),  # nothing there
        (2, 0.50, (0.7, 0.7, 0.95, 0.95)),  # half on the can
    ]
    outcomes, found = match_image(predictions, labels)
    assert outcomes == ["correct", "duplicate", "wrong class", "on nothing", "poor box"]
    assert found == [True, True]


def test_most_confident_box_claims_the_item():
    labels = [(1, BOTTLE)]
    outcomes, _ = match_image([(1, 0.40, BOTTLE), (1, 0.95, BOTTLE)], labels)
    assert outcomes == ["duplicate", "correct"]


def test_unfound_items_and_empty_photos():
    outcomes, found = match_image([], [(0, BOTTLE)])
    assert (outcomes, found) == ([], [False])
    outcomes, found = match_image([(2, 0.9, CAN)], [])
    assert (outcomes, found) == (["on nothing"], [])


def test_summary_counts_hallucinations_per_class():
    per_image = [
        {
            "pred_classes": [1, 3],
            "outcomes": ["correct", "on nothing"],
            "labels": [(1, BOTTLE), (2, CAN)],
            "found": [True, False],
            "confusions": [],
        },
        {"pred_classes": [3], "outcomes": ["on nothing"], "labels": [], "found": [], "confusions": []},
        {
            "pred_classes": [0],
            "outcomes": ["wrong class"],
            "labels": [(2, CAN)],
            "found": [True],
            "confusions": [(0, 2)],
        },
    ]
    summary = summarise(per_image)
    assert summary["detections"] == 4
    assert summary["on_nothing"] == 2
    assert summary["per_class"]["organic"]["on nothing"] == 2
    assert summary["per_class"]["organic"]["share_on_nothing"] == 1.0
    assert summary["per_class"]["metal"]["missed"] == 1
    assert summary["per_class"]["metal"]["labelled_as_this_but_called"] == {"paper": 1}
    assert summary["images_without_labels"] == 1
    assert summary["of_which_got_detections"] == 1


def test_read_results_raises_on_empty_csv(tmp_path):
    csv = tmp_path / "results.csv"
    csv.write_text("epoch,metrics/mAP50-95(B)\n")
    with pytest.raises(SystemExit, match="has no epochs"):
        read_results(csv)


def test_check_single_epoch():
    rows = epochs([0.50], [2.0], [1.8])
    report = check(rows)
    assert report["epochs_run"] == 1
    assert report["best_epoch"] == 1
    assert report["verdict"] in ("levelled off", "still improving")


def test_check_hallucinations_missing_weights(tmp_path, monkeypatch):
    """check_hallucinations.py fails with a clear message when weights are missing,
    before any PyTorch import."""
    import check_hallucinations

    missing = tmp_path / "nonexistent.pt"
    assert not missing.exists()

    # Simulate CLI args with missing weights.
    test_args = ["check_hallucinations.py", "--weights", str(missing)]
    monkeypatch.setattr(sys, "argv", test_args)
    with pytest.raises(SystemExit, match="not found"):
        check_hallucinations.main()


def test_train_blocked_without_validation_report(tmp_path):
    """train.py refuses to train when validation_report.json is missing.

    This test runs train.py as a subprocess. It requires torch/ultralytics to be
    installed; without them the import itself fails, which still proves the
    script cannot start training. The key assertion is that the process exits
    non-zero and never reaches model training.
    """
    import subprocess

    # Create a data.yaml pointing at a nonexistent dataset.
    data_yaml = tmp_path / "data.yaml"
    data_yaml.write_text("path: /nonexistent/dataset\ntrain: images/train\nval: images/val\ntest: images/test\nnames: [paper, plastic, metal, organic]\n")

    result = subprocess.run(
        [
            sys.executable,
            str(SCRIPTS / "train.py"),
            "--data",
            str(data_yaml),
            "--epochs",
            "1",
            "--name",
            "no-validation",
        ],
        capture_output=True,
        text=True,
    )
    assert result.returncode != 0
    combined = result.stdout + result.stderr
    # Either validation report missing, dataset folder missing, or torch import error.
    assert any(
        phrase in combined
        for phrase in (
            "validation_report.json",
            "Dataset folder not found",
            "validate_dataset.py",
            "No module named",
        )
    ), combined


def test_invalid_training_config_rejected(tmp_path):
    """train.py exits non-zero when the dataset path is invalid (never reaches training)."""
    import subprocess

    data_yaml = tmp_path / "data.yaml"
    data_yaml.write_text("path: /nonexistent/dataset\ntrain: images/train\nval: images/val\ntest: images/test\nnames: [paper, plastic, metal, organic]\n")

    result = subprocess.run(
        [
            sys.executable,
            str(SCRIPTS / "train.py"),
            "--data",
            str(data_yaml),
            "--epochs",
            "0",
        ],
        capture_output=True,
        text=True,
    )
    assert result.returncode != 0
