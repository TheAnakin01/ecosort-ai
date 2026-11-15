"""Finding the dataset folder a data.yaml points at. Needs no PyTorch."""

from pathlib import Path

import yaml


def dataset_dir(data_yaml: Path) -> Path:
    """The dataset folder a data.yaml points at."""
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
