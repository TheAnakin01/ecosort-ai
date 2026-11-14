"""Tests for scripts/validate_dataset.py. Run from ai-model/:  pytest"""

import json
import random
import subprocess
import sys
import zlib
from pathlib import Path

import pytest
from PIL import Image

SCRIPTS = Path(__file__).resolve().parent.parent / "scripts"
sys.path.insert(0, str(SCRIPTS))

from validate_dataset import check_label_line, validate  # noqa: E402

GOOD_BOX = "1 0.5 0.5 0.2 0.2\n"


def make_image(path: Path, seed: int, size=(64, 48)) -> None:
    """Write a small picture of coloured blocks. Different seeds give different pictures."""
    rng = random.Random(seed)
    image = Image.new("RGB", size)
    block_w, block_h = size[0] // 8, size[1] // 6
    for row in range(6):
        for col in range(8):
            colour = (rng.randrange(256), rng.randrange(256), rng.randrange(256))
            image.paste(colour, (col * block_w, row * block_h, (col + 1) * block_w, (row + 1) * block_h))
    path.parent.mkdir(parents=True, exist_ok=True)
    image.save(path)


def add(dataset: Path, split: str, stem: str, label: str | None = GOOD_BOX, seed: int | None = None) -> Path:
    """Add one image, and its label file unless label is None."""
    image = dataset / "images" / split / f"{stem}.png"
    # crc32 gives the same seed on every run, unlike Python's built-in hash().
    make_image(image, seed if seed is not None else zlib.crc32(f"{split}/{stem}".encode()))
    (dataset / "labels" / split).mkdir(parents=True, exist_ok=True)
    if label is not None:
        (dataset / "labels" / split / f"{stem}.txt").write_text(label)
    return image


@pytest.fixture
def dataset(tmp_path: Path) -> Path:
    """A small, clean dataset: every class present in every split."""
    root = tmp_path / "ecosort"
    all_classes = "".join(f"{i} 0.5 0.5 0.2 0.2\n" for i in range(4))
    for split in ("train", "val", "test"):
        add(root, split, f"{split}_a", all_classes)
        add(root, split, f"{split}_b", all_classes.replace("0.5 0.5", "0.3 0.3"))
    return root


@pytest.mark.parametrize(
    ("line", "problem"),
    [
        ("0 0.5 0.5 0.2 0.2", None),
        ("3 0.1 0.1 0.2 0.2", None),  # touches the top-left corner exactly
        ("0 0.5 0.5 0.2", "expected 5 values"),
        ("0 0.5 0.5 0.2 0.2 0.9", "expected 5 values"),
        ("0 0.5 abc 0.2 0.2", "not a number"),
        ("4 0.5 0.5 0.2 0.2", "class id 4"),
        ("-1 0.5 0.5 0.2 0.2", "class id -1"),
        ("0 0.5 0.5 0 0.2", "no width or height"),
        ("0 0.5 0.5 0.2 -0.1", "no width or height"),
        ("0 0.95 0.5 0.2 0.2", "outside the image"),
        ("0 0.5 1.4 0.2 0.2", "outside the image"),
    ],
)
def test_check_label_line(line, problem):
    result = check_label_line(line)
    if problem is None:
        assert result is None
    else:
        assert problem in result


def test_clean_dataset_passes(dataset):
    findings, stats = validate(dataset)

    assert not findings.errors
    assert stats["images_per_split"] == {"train": 2, "val": 2, "test": 2}
    assert stats["boxes_per_class"] == {"paper": 6, "plastic": 6, "metal": 6, "organic": 6}
    assert stats["boxes_per_class_by_split"]["val"] == {"paper": 2, "plastic": 2, "metal": 2, "organic": 2}


def test_unreadable_image_is_an_error(dataset):
    (dataset / "images/train/broken.jpg").write_bytes(b"this is not an image")
    (dataset / "labels/train/broken.txt").write_text(GOOD_BOX)

    findings, _ = validate(dataset)
    assert findings.errors["Unreadable image"] == ["train/broken.jpg"]


def test_image_and_label_must_come_in_pairs(dataset):
    add(dataset, "train", "no_label", label=None)
    (dataset / "labels/val/no_image.txt").write_text(GOOD_BOX)

    findings, _ = validate(dataset)
    assert findings.errors["Image without a label file"] == ["train/no_label.png"]
    assert findings.errors["Label file without an image"] == ["labels/val/no_image.txt"]


def test_invalid_boxes_are_reported_with_file_and_line(dataset):
    add(dataset, "train", "bad", GOOD_BOX + "7 0.5 0.5 0.2 0.2\n0 0.5 0.5 0 0.2\n")

    findings, stats = validate(dataset)
    assert findings.errors["Invalid box"] == [
        "train/bad.png, line 2: class id 7 is not one of 0-3",
        "train/bad.png, line 3: box has no width or height",
    ]
    # Only the valid box is counted.
    assert stats["boxes_per_class_by_split"]["train"]["plastic"] == 3


def test_empty_label_file_counts_as_background_not_an_error(dataset):
    add(dataset, "train", "background", label="")

    findings, stats = validate(dataset)
    assert not findings.errors
    assert stats["background_images_per_split"]["train"] == 1


def test_same_file_in_two_splits_is_leakage(dataset):
    original = add(dataset, "train", "shared", seed=777)
    copy = dataset / "images/test/shared_copy.png"
    copy.write_bytes(original.read_bytes())
    (dataset / "labels/test/shared_copy.txt").write_text(GOOD_BOX)

    findings, _ = validate(dataset)
    assert findings.errors["Same image file in more than one split"] == ["test/shared_copy.png; train/shared.png"]


def test_roboflow_copies_of_one_photo_in_two_splits_is_leakage(dataset):
    add(dataset, "train", "src__bottle_jpg.rf.aaa111", seed=1)
    add(dataset, "val", "src__bottle_jpg.rf.bbb222", seed=2)
    add(dataset, "train", "src__can_jpg.rf.ccc333", seed=3)  # another photo, one split only: fine

    findings, _ = validate(dataset)
    assert findings.errors["Copies of one source photo in more than one split"] == [
        "train/src__bottle_jpg.rf.aaa111.png; val/src__bottle_jpg.rf.bbb222.png"
    ]


def test_resaved_picture_in_two_splits_is_a_warning(dataset):
    original = add(dataset, "train", "photo_one", seed=4242)
    with Image.open(original) as image:
        resized = image.resize((128, 96))
    target = dataset / "images/test/photo_two.png"
    resized.save(target)
    (dataset / "labels/test/photo_two.txt").write_text(GOOD_BOX)

    findings, _ = validate(dataset)
    assert not findings.errors
    assert findings.warnings["Pictures that look identical in more than one split"] == [
        "test/photo_two.png; train/photo_one.png"
    ]


def test_missing_and_rare_classes_are_flagged(tmp_path):
    root = tmp_path / "ecosort"
    many_paper = "0 0.5 0.5 0.2 0.2\n" * 1 + "".join(f"0 0.{i} 0.5 0.1 0.1\n" for i in range(2, 9))
    for split in ("train", "val", "test"):
        add(root, split, f"{split}_a", many_paper + "1 0.5 0.5 0.3 0.3\n2 0.5 0.5 0.4 0.4\n")
    add(root, "train", "rare", "1 0.4 0.4 0.2 0.2\n" * 1)

    findings, _ = validate(root)
    assert findings.errors["Class with no boxes"] == ["organic"]
    assert any(detail.startswith("metal:") for detail in findings.warnings["Under-represented class"])


def test_missing_split_is_an_error(dataset):
    for path in (dataset / "images/test").iterdir():
        path.unlink()
    (dataset / "images/test").rmdir()

    findings, _ = validate(dataset)
    assert findings.errors["Missing split"] == ["images/test does not exist"]


def test_command_line_exit_code_and_report(dataset, tmp_path):
    script = [sys.executable, str(SCRIPTS / "validate_dataset.py"), str(dataset)]

    ok = subprocess.run(script, capture_output=True, text=True)
    assert ok.returncode == 0, ok.stdout + ok.stderr
    assert "No errors" in ok.stdout
    assert json.loads((dataset / "validation_report.json").read_text())["passed"] is True

    add(dataset, "val", "bad", "9 0.5 0.5 0.2 0.2\n")
    report = tmp_path / "report.json"
    failed = subprocess.run([*script, "--report", str(report)], capture_output=True, text=True)
    assert failed.returncode == 1
    assert "ERROR: Invalid box" in failed.stdout
    saved = json.loads(report.read_text())
    assert saved["passed"] is False
    assert saved["errors"]["Invalid box"] == ["val/bad.png, line 1: class id 9 is not one of 0-3"]


def test_resplit_fixes_a_source_whose_own_splits_leak(tmp_path):
    """A Roboflow export with copies of one photo in train and valid: prepare, validate, resplit, validate."""
    source = tmp_path / "leaky"
    (source / "data.yaml").parent.mkdir(parents=True)
    (source / "data.yaml").write_text("names: [paper, plastic, metal, organic]\n")
    labels = "".join(f"{i} 0.5 0.5 0.2 0.2\n" for i in range(4))
    seed = 0
    for photo in range(30):
        # Three augmented copies per photo; the export puts one copy in each split.
        for copy, split in (("aa", "train"), ("bb", "valid"), ("cc", "test")):
            seed += 1
            make_image(source / split / "images" / f"photo{photo}_jpg.rf.{copy}.png", seed)
            (source / split / "labels").mkdir(parents=True, exist_ok=True)
            (source / split / "labels" / f"photo{photo}_jpg.rf.{copy}.txt").write_text(labels)

    prepare = [sys.executable, str(SCRIPTS / "prepare_dataset.py"), str(source)]
    check = [sys.executable, str(SCRIPTS / "validate_dataset.py")]

    leaky = tmp_path / "out_leaky"
    assert subprocess.run([*prepare, "--out", str(leaky)], capture_output=True).returncode == 0
    result = subprocess.run([*check, str(leaky)], capture_output=True, text=True)
    assert result.returncode == 1
    assert "Copies of one source photo in more than one split (30)" in result.stdout
    assert "--resplit" in result.stdout

    fixed = tmp_path / "out_fixed"
    assert subprocess.run([*prepare, "--out", str(fixed), "--resplit"], capture_output=True).returncode == 0
    result = subprocess.run([*check, str(fixed)], capture_output=True, text=True)
    assert result.returncode == 0, result.stdout
    report = json.loads((fixed / "validation_report.json").read_text())
    assert sum(report["stats"]["images_per_split"].values()) == 90
    assert all(count > 0 for count in report["stats"]["images_per_split"].values())
