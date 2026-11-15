"""Tests for download_datasets.py that need no network."""

import os
import subprocess
import sys
from pathlib import Path
from types import SimpleNamespace

import pytest

SCRIPTS = Path(__file__).resolve().parent.parent / "scripts"
sys.path.insert(0, str(SCRIPTS))

from download_datasets import DATASETS, check_key, version_number  # noqa: E402


def run(out: Path, key: str | None) -> subprocess.CompletedProcess:
    env = {k: v for k, v in os.environ.items() if k != "ROBOFLOW_API_KEY"}
    if key is not None:
        env["ROBOFLOW_API_KEY"] = key
    return subprocess.run(
        [sys.executable, str(SCRIPTS / "download_datasets.py"), "--out", str(out)],
        capture_output=True,
        text=True,
        env=env,
    )


def test_newest_version_is_picked_by_number_not_text():
    versions = [SimpleNamespace(id=f"ws/project/{n}") for n in (2, 10, 9)]
    assert max(versions, key=version_number).id == "ws/project/10"


def test_key_checks():
    assert check_key("  abc123\n") == "abc123"
    with pytest.raises(SystemExit, match="empty"):
        check_key("   ")
    with pytest.raises(SystemExit, match="Publishable"):
        check_key("rf_abcdef")


def test_needs_no_key_or_network_when_everything_is_downloaded(tmp_path):
    for folder, _, _ in DATASETS:
        (tmp_path / folder).mkdir()
        (tmp_path / folder / "data.yaml").write_text("names: [paper]\n")
    result = run(tmp_path, key=None)
    assert result.returncode == 0, result.stderr
    assert result.stdout.count("already downloaded") == len(DATASETS)


def test_missing_key_stops_with_a_clear_message(tmp_path):
    result = run(tmp_path, key="")
    assert result.returncode != 0
    assert "ROBOFLOW_API_KEY is empty" in result.stderr


def test_same_datasets_as_the_colab_notebook():
    import json

    notebook = json.loads((SCRIPTS.parent / "notebooks" / "train_ecosort.ipynb").read_text())
    source = "".join("".join(cell["source"]) for cell in notebook["cells"])
    for folder, workspace, project in DATASETS:
        assert f'("{folder}", "{workspace}", "{project}")' in source
