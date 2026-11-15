"""Tests for download_datasets.py that need no network."""

import os
import subprocess
import sys
from pathlib import Path
from types import SimpleNamespace

import pytest
import yaml

SCRIPTS = Path(__file__).resolve().parent.parent / "scripts"
sys.path.insert(0, str(SCRIPTS))

from download_datasets import (  # noqa: E402
    DATASETS,
    FALLBACK_DATASETS,
    check_key,
    find_version,
    load_dataset_config,
    version_number,
)


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


def test_load_dataset_config_returns_all_four_datasets():
    config = load_dataset_config()
    folders = [entry["folder"] for entry in config]
    assert folders == ["trash-detection", "trashnet", "neat-now", "garbage-cls-3"]
    for entry in config:
        assert set(entry) >= {"folder", "workspace", "project", "version"}
        assert entry["version"] is None


def test_find_version_picks_requested_version():
    versions = [SimpleNamespace(id=f"ws/project/{n}") for n in (2, 10, 9)]
    assert find_version(versions, 10).id == "ws/project/10"
    assert find_version(versions, 2).id == "ws/project/2"


def test_find_version_picks_newest_when_none_requested():
    versions = [SimpleNamespace(id=f"ws/project/{n}") for n in (2, 10, 9)]
    assert find_version(versions, None).id == "ws/project/10"


def test_find_version_fails_clear_when_requested_version_unavailable():
    versions = [SimpleNamespace(id="ws/project/2"), SimpleNamespace(id="ws/project/5")]
    with pytest.raises(SystemExit, match="Requested version 99 is not available"):
        find_version(versions, 99)


def test_fallback_datasets_match_dataets_alias():
    # DATASETS is (folder, workspace, project); FALLBACK_DATASETS adds version.
    for (f1, w1, p1), (f2, w2, p2, _) in zip(DATASETS, FALLBACK_DATASETS):
        assert (f1, w1, p1) == (f2, w2, p2)


def test_load_dataset_config_reads_yaml_config(tmp_path, monkeypatch):
    """load_dataset_config reads from configs/datasets.yaml."""
    import download_datasets as dd

    config_dir = tmp_path / "configs"
    config_dir.mkdir()
    (config_dir / "datasets.yaml").write_text(
        yaml.safe_dump(
            {
                "datasets": [
                    {
                        "folder": "trash-detection",
                        "workspace": "amongus-o6ilp",
                        "project": "trash-detection-1fjjc-ipij8",
                        "version": 3,
                    },
                    {
                        "folder": "neat-now",
                        "workspace": "fyp-gojku",
                        "project": "neat-now",
                        "version": None,
                    },
                ]
            }
        )
    )

    original = dd.CONFIG_PATH
    dd.CONFIG_PATH = config_dir / "datasets.yaml"
    try:
        config = dd.load_dataset_config()
    finally:
        dd.CONFIG_PATH = original

    assert len(config) == 2
    assert config[0]["folder"] == "trash-detection"
    assert config[0]["version"] == 3
    assert config[1]["folder"] == "neat-now"
    assert config[1]["version"] is None


def test_load_dataset_config_fails_on_empty_config(tmp_path, monkeypatch):
    """An empty datasets list raises SystemExit."""
    import download_datasets as dd

    config_dir = tmp_path / "configs"
    config_dir.mkdir()
    (config_dir / "datasets.yaml").write_text(yaml.safe_dump({"datasets": []}))

    original = dd.CONFIG_PATH
    dd.CONFIG_PATH = config_dir / "datasets.yaml"
    try:
        with pytest.raises(SystemExit, match="no 'datasets' entries"):
            dd.load_dataset_config()
    finally:
        dd.CONFIG_PATH = original
