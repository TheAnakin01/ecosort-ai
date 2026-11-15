"""Tests for scripts/dataset_paths.py. Run from ai-model/:  pytest"""

import sys
from pathlib import Path

import pytest
import yaml

SCRIPTS = Path(__file__).resolve().parent.parent / "scripts"
sys.path.insert(0, str(SCRIPTS))

from dataset_paths import absolute_data_yaml, dataset_dir  # noqa: E402

AI_MODEL = SCRIPTS.parent


def test_repo_config_points_at_the_dataset_folder_inside_ai_model():
    assert dataset_dir(AI_MODEL / "configs" / "data.yaml") == AI_MODEL / "datasets" / "ecosort"


def test_relative_path_is_resolved_from_the_config_file_not_the_current_folder(tmp_path, monkeypatch):
    """The bug this guards against: training failed when run from a different folder."""
    (tmp_path / "configs").mkdir()
    (tmp_path / "datasets" / "ecosort").mkdir(parents=True)
    config = tmp_path / "configs" / "data.yaml"
    config.write_text("path: ../datasets/ecosort\ntrain: images/train\nval: images/val\nnames:\n  0: paper\n")
    elsewhere = tmp_path / "somewhere" / "else"
    elsewhere.mkdir(parents=True)
    monkeypatch.chdir(elsewhere)

    resolved = absolute_data_yaml(config)

    written = yaml.safe_load(resolved.read_text())
    assert Path(written["path"]).is_absolute()
    assert Path(written["path"]) == (tmp_path / "datasets" / "ecosort").resolve()
    # Everything else is carried over unchanged.
    assert written["train"] == "images/train" and written["names"] == {0: "paper"}
    assert resolved == (tmp_path / "datasets" / "ecosort").resolve() / "data.yaml"


def test_absolute_path_is_kept(tmp_path):
    dataset = tmp_path / "data"
    dataset.mkdir()
    config = tmp_path / "data.yaml"
    config.write_text(f"path: {dataset}\ntrain: images/train\n")
    assert yaml.safe_load(absolute_data_yaml(config).read_text())["path"] == str(dataset)


def test_missing_dataset_folder_gives_a_clear_message(tmp_path):
    config = tmp_path / "data.yaml"
    config.write_text("path: not-there\n")
    with pytest.raises(SystemExit, match="prepare_dataset.py"):
        absolute_data_yaml(config)
