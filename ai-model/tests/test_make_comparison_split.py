"""Tests for make_comparison_split.py."""

import json
import subprocess
import sys
from pathlib import Path

import yaml

SCRIPTS = Path(__file__).resolve().parent.parent / "scripts"


def add(dataset: Path, split: str, stem: str) -> None:
    for kind, suffix, content in (("images", ".jpg", b"x"), ("labels", ".txt", b"0 0.5 0.5 0.1 0.1\n")):
        folder = dataset / kind / split
        folder.mkdir(parents=True, exist_ok=True)
        (folder / f"{stem}{suffix}").write_bytes(content)


def test_leaves_out_photos_the_other_model_trained_on(tmp_path):
    run2, run1 = tmp_path / "run2", tmp_path / "run1"
    for stem in ("trashnet__a", "trashnet__b", "garbage-cls-3__c"):
        add(run2, "val", stem)
    add(run1, "train", "trashnet__b")  # run 1 trained on this one
    add(run1, "val", "trashnet__a")  # in run 1's validation: still fair
    out = tmp_path / "compare"

    result = subprocess.run(
        [
            sys.executable,
            str(SCRIPTS / "make_comparison_split.py"),
            "--val-from",
            str(run2),
            "--exclude-train-of",
            str(run1),
            "--out",
            str(out),
        ],
        capture_output=True,
        text=True,
    )
    assert result.returncode == 0, result.stderr

    kept = sorted(p.name for p in (out / "images" / "val").iterdir())
    assert kept == ["garbage-cls-3__c.jpg", "trashnet__a.jpg"]
    assert sorted(p.name for p in (out / "labels" / "val").iterdir()) == ["garbage-cls-3__c.txt", "trashnet__a.txt"]
    # Images are linked when symlinks are supported, copied otherwise (Windows without privilege).
    assert (out / "images" / "val" / "trashnet__a.jpg").is_file()

    summary = json.loads((out / "comparison_split.json").read_text())
    assert (summary["validation_photos"], summary["left_out_seen_in_training"], summary["kept"]) == (3, 1, 2)

    data = yaml.safe_load((out / "data.yaml").read_text())
    assert data["path"] == str(out.resolve())
    assert data["val"] == "images/val"
    assert data["names"] == {0: "paper", 1: "plastic", 2: "metal", 3: "organic"}


def test_refuses_an_empty_training_split(tmp_path):
    add(tmp_path / "run2", "val", "x")
    result = subprocess.run(
        [
            sys.executable,
            str(SCRIPTS / "make_comparison_split.py"),
            "--val-from",
            str(tmp_path / "run2"),
            "--exclude-train-of",
            str(tmp_path / "missing"),
            "--out",
            str(tmp_path / "out"),
        ],
        capture_output=True,
        text=True,
    )
    assert result.returncode != 0
    assert "has no images" in result.stderr
