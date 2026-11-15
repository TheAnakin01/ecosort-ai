"""Download the four Roboflow datasets into downloads/.

Reads the Roboflow Private API Key from the ROBOFLOW_API_KEY environment
variable, so it never has to be typed into a notebook. Datasets that are
already downloaded are skipped, so it is safe to run again.

Run from the ai-model/ folder:

    ROBOFLOW_API_KEY=... python scripts/download_datasets.py

The Colab notebook asks for the key and downloads in its own cell; the Kaggle
notebook uses this script.
"""

import argparse
import os
from pathlib import Path

AI_MODEL_DIR = Path(__file__).resolve().parent.parent

# (folder name, workspace, project). Keep in step with notebooks/train_ecosort.ipynb.
DATASETS = [
    ("trash-detection", "amongus-o6ilp", "trash-detection-1fjjc-ipij8"),
    (
        "trashnet",
        "polygence-project",
        "trashnet-a-set-of-annotated-images-of-trash-that-can-be-used-for-object-detection",
    ),
    ("neat-now", "fyp-gojku", "neat-now"),
    ("garbage-cls-3", "objectdetection-z2zn1", "garbage-classification-3-bjcgp"),
]


def version_number(version) -> int:
    """A version id looks like "workspace/project/3"."""
    return int(str(version.id).rsplit("/", 1)[-1])


def check_key(key: str) -> str:
    key = key.strip()
    if not key:
        raise SystemExit("ROBOFLOW_API_KEY is empty. Set it to your Roboflow Private API Key.")
    if key.startswith("rf_"):
        raise SystemExit(
            "That is the Publishable key (it starts with rf_). Use the Private API Key from the same page."
        )
    return key


def main() -> None:
    parser = argparse.ArgumentParser(description="Download the EcoSort training datasets from Roboflow")
    parser.add_argument("--out", type=Path, default=AI_MODEL_DIR / "downloads")
    args = parser.parse_args()

    missing = [entry for entry in DATASETS if not (args.out / entry[0] / "data.yaml").exists()]
    for folder, _, _ in DATASETS:
        if (args.out / folder / "data.yaml").exists():
            print(f"{folder}: already downloaded, skipping")
    if not missing:
        print("All datasets are in", args.out)
        return

    key = check_key(os.environ.get("ROBOFLOW_API_KEY", ""))
    from roboflow import Roboflow  # imported here so nothing above needs the network

    try:
        rf = Roboflow(api_key=key)
    except RuntimeError as error:
        raise SystemExit(f"Roboflow rejected the key. Its reply: {error}") from None

    for folder, workspace, project_name in missing:
        target = args.out / folder
        versions = rf.workspace(workspace).project(project_name).versions()
        if not versions:
            raise SystemExit(
                f"{workspace}/{project_name} has no downloadable version on Roboflow. "
                "Pick another copy of this dataset and update DATASETS."
            )
        latest = max(versions, key=version_number)
        print(f"{folder}: downloading version {latest.id}", flush=True)
        latest.download("yolov8", location=str(target))
    print("All datasets are in", args.out)


if __name__ == "__main__":
    main()
