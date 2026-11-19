"""Download the four Roboflow datasets into downloads/.

Reads the Roboflow Private API Key from the ROBOFLOW_API_KEY environment
variable, so it never has to be typed into a notebook. Datasets that are
already downloaded are skipped, so it is safe to run again.

Dataset versions are configured centrally in configs/datasets.yaml. Each entry
may pin an explicit version; if none is pinned, the newest downloadable
version is used and a reproducibility warning is printed.

Run from the ai-model/ folder:

    ROBOFLOW_API_KEY=... python scripts/download_datasets.py

A download manifest is written to downloads/download_manifest.json recording
the workspace, project, selected version, download timestamp and dataset
identifier for every dataset, so the build is reproducible.
"""

import argparse
import json
import os
from datetime import datetime, timezone
from pathlib import Path

import yaml

AI_MODEL_DIR = Path(__file__).resolve().parent.parent
CONFIG_PATH = AI_MODEL_DIR / "configs" / "datasets.yaml"
MANIFEST_NAME = "download_manifest.json"

from dataset_paths import data_root  # noqa: E402

# Fallback list used when configs/datasets.yaml does not exist. Kept in step
# with notebooks/train_ecosort.ipynb and configs/datasets.yaml.
FALLBACK_DATASETS = [
    ("trash-detection", "amongus-o6ilp", "trash-detection-1fjjc-ipij8", 1),
    (
        "trashnet",
        "polygence-project",
        "trashnet-a-set-of-annotated-images-of-trash-that-can-be-used-for-object-detection",
        20,
    ),
    ("neat-now", "fyp-gojku", "neat-now", 10),
    ("garbage-cls-3", "objectdetection-z2zn1", "garbage-classification-3-bjcgp", 5),
]

# Backward-compatible alias: (folder, workspace, project) tuples, version omitted.
# Kept so existing tests and imports that reference DATASETS continue to work.
DATASETS = [(f, w, p) for f, w, p, _ in FALLBACK_DATASETS]


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


def load_dataset_config() -> list[dict]:
    """Load dataset sources from configs/datasets.yaml.

    Falls back to the built-in FALLBACK_DATASETS when the config file is
    missing, so existing behaviour is preserved without the config.
    """
    if not CONFIG_PATH.exists():
        return [
            {"folder": f, "workspace": w, "project": p, "version": v}
            for f, w, p, v in FALLBACK_DATASETS
        ]
    with CONFIG_PATH.open() as fh:
        config = yaml.safe_load(fh) or {}
    datasets = config.get("datasets", [])
    if not datasets:
        raise SystemExit(f"{CONFIG_PATH} has no 'datasets' entries.")
    return datasets


def find_version(versions, requested: int | None):
    """Return the Roboflow version object matching `requested`, or None.

    When requested is None, returns the newest downloadable version.
    Raises SystemExit when a requested version is not available.
    """
    if requested is None:
        return max(versions, key=version_number)
    for version in versions:
        if version_number(version) == requested:
            return version
    available = sorted((version_number(v) for v in versions), reverse=True)
    raise SystemExit(
        f"Requested version {requested} is not available for this Roboflow project. "
        f"Available versions: {available}. Update configs/datasets.yaml or remove the pin."
    )


def main() -> None:
    parser = argparse.ArgumentParser(description="Download the EcoSort training datasets from Roboflow")
    parser.add_argument("--out", type=Path, default=data_root() / "downloads")
    args = parser.parse_args()

    config = load_dataset_config()
    entries = [
        (entry["folder"], entry["workspace"], entry["project"], entry.get("version"))
        for entry in config
    ]

    missing = [
        entry for entry in entries if not (args.out / entry[0] / "data.yaml").exists()
    ]
    for folder, _, _, _ in entries:
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

    manifest_entries = []
    for folder, workspace, project_name, requested_version in missing:
        target = args.out / folder
        versions = rf.workspace(workspace).project(project_name).versions()
        if not versions:
            raise SystemExit(
                f"{workspace}/{project_name} has no downloadable version on Roboflow. "
                "Pick another copy of this dataset and update DATASETS."
            )
        selected = find_version(versions, requested_version)
        selected_number = version_number(selected)
        if requested_version is not None and selected_number != requested_version:
            raise SystemExit(
                f"{workspace}/{project_name}: requested version {requested_version} "
                f"but resolved to {selected_number}."
            )
        if requested_version is None:
            print(
                f"{folder}: downloading newest version {selected.id} "
                f"(version not pinned — not reproducible).",
                flush=True,
            )
        else:
            print(f"{folder}: downloading pinned version {selected.id}", flush=True)
        selected.download("yolov8", location=str(target))

        manifest_entries.append(
            {
                "folder": folder,
                "workspace": workspace,
                "project": project_name,
                "version_requested": requested_version,
                "version_selected": selected_number,
                "dataset_id": str(selected.id),
                "downloaded_at": datetime.now(timezone.utc).isoformat(timespec="seconds"),
            }
        )

    args.out.mkdir(parents=True, exist_ok=True)
    manifest_path = args.out / MANIFEST_NAME
    manifest_path.write_text(
        json.dumps(
            {
                "downloaded_at": datetime.now(timezone.utc).isoformat(timespec="seconds"),
                "datasets": manifest_entries,
            },
            indent=2,
        )
        + "\n"
    )
    print("All datasets are in", args.out)
    print(f"Download manifest written to {manifest_path}")


if __name__ == "__main__":
    main()
