"""Finding the dataset folder a data.yaml points at. Needs no PyTorch."""

import os
from pathlib import Path

import yaml

AI_MODEL_DIR = Path(__file__).resolve().parent.parent


def data_root() -> Path:
    """External data root for datasets, downloads, runs and weights.

    Reads the ECOSORT_DATA_ROOT environment variable. On Windows it defaults
    to D:\\EcoSortData so large datasets and training artifacts live off the
    system drive. On Linux (Colab, Kaggle) the variable is normally unset and
    the function falls back to the ai-model directory, preserving the original
    relative-path behaviour.
    """
    root = os.getenv("ECOSORT_DATA_ROOT")
    if root:
        return Path(root)
    if os.name == "nt":
        return Path("D:/EcoSortData")
    return AI_MODEL_DIR


def dataset_dir(data_yaml: Path) -> Path:
    """The dataset folder a data.yaml points at.

    When ECOSORT_DATA_ROOT is explicitly set, datasets live at
    {ECOSORT_DATA_ROOT}/datasets/ecosort regardless of what data.yaml says.
    Otherwise resolve path relative to the config file, as before.
    """
    root = os.getenv("ECOSORT_DATA_ROOT")
    if root:
        return Path(root) / "datasets" / "ecosort"
    path = Path(yaml.safe_load(data_yaml.read_text())["path"])
    return path if path.is_absolute() else (data_yaml.parent / path).resolve()


def absolute_data_yaml(data_yaml: Path) -> Path:
    """Write a copy of the dataset config with a full path, and return it.

    Ultralytics looks for a relative "path" from the folder the command was
    run in, not from the config file, so a relative path only works by luck.
    A full path always works.
    """
    config = yaml.safe_load(data_yaml.read_text())
    dataset = dataset_dir(data_yaml)
    if not dataset.is_dir():
        raise SystemExit(f"Dataset folder not found: {dataset}. Run scripts/prepare_dataset.py first.")
    config["path"] = str(dataset)
    resolved = dataset / "data.yaml"
    resolved.write_text(yaml.safe_dump(config, sort_keys=False))
    return resolved
