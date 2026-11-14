# Dataset card

**Status: not filled in yet.** No merged dataset has been built and checked. Fill each section from real output; do not estimate.

Where the numbers come from:

- `datasets/ecosort/dataset_report.json`, written by `prepare_dataset.py`
- `datasets/ecosort/validation_report.json`, written by `validate_dataset.py`

## Sources

| Dataset | Link | Version | License | Downloaded on | Checked by |
|---|---|---|---|---|---|
| Trash Detection | https://universe.roboflow.com/amongus-o6ilp/trash-detection-1fjjc-ipij8 | | Not yet checked | | |
| TrashNet: annotated images of trash | https://universe.roboflow.com/polygence-project/trashnet-a-set-of-annotated-images-of-trash-that-can-be-used-for-object-detection | | CC BY 4.0 (per its Roboflow page, read 2026-11-14) | | |
| Neat Now | https://universe.roboflow.com/fyp-gojku/neat-now | | Not yet checked | | |

Open each dataset's page and copy its license here before the model is used in a submission.

## Class mapping

One row per source class. Copy the mapping from the `--dry-run` output, then review every row by eye: the script matches class names by keyword and can be wrong.

| Source dataset | Source class | EcoSort class or `exclude` | Why | Reviewed by | Date |
|---|---|---|---|---|---|
| | | | | | |

Rules used when mapping:

- Glass, batteries, e-waste and general "trash" are excluded. They are none of the four classes.
- A class naming two materials, or none (for example a plain "bottle"), is excluded unless a reviewer decides otherwise in `ai-model/configs/class_overrides.yaml`.
- Nothing is relabelled to balance the classes.

## Size

Images and boxes per class and split, from `validation_report.json`.

| Split | Images | Images with no boxes | paper | plastic | metal | organic |
|---|---|---|---|---|---|---|
| train | | | | | | |
| val | | | | | | |
| test | | | | | | |

## How it was built

- Command used:
- `--resplit` used: yes / no
- Boxes removed as invalid:
- Boxes dropped because their class was excluded:
- Photos left out because every item in them was excluded:

## Checks

- [ ] `validate_dataset.py` finished with 0 errors
- [ ] No photo appears in more than one split
- [ ] A sample of images from every class and split was looked at by a person
- [ ] Every source's license is recorded above

Warnings from the last validation run:

## Known gaps

To be written from the real numbers. Things to look for:

- Organic waste. TrashNet has no organic class, so it depends on the other two sources.
- Photos that match local conditions: Indian packaging, mixed household waste, indoor lighting.
- Small, crushed, wet, transparent or overlapping items.

## Our own photos

None added yet. If the team adds photos: take them with permission, keep people and personal details out of frame, and annotate them in Roboflow as one more source.
