# AI model

Trains a YOLO nano detector on four classes: paper, plastic, metal, organic.

## The quick way: the Colab notebook

[Open the notebook in Colab](https://colab.research.google.com/github/TheAnakin01/ecosort-ai/blob/main/ai-model/notebooks/train_ecosort.ipynb) and run it top to bottom. It downloads the four Roboflow datasets, merges them, trains, and gives you `best.pt`.

The only thing you supply is your Roboflow API key (Roboflow → Settings → API Keys). The notebook asks for it when it runs and does not save it.

Datasets the team picked:

| Dataset | Notes |
|---|---|
| [Trash Detection](https://universe.roboflow.com/amongus-o6ilp/trash-detection-1fjjc-ipij8) | |
| [TrashNet: annotated images of trash](https://universe.roboflow.com/polygence-project/trashnet-a-set-of-annotated-images-of-trash-that-can-be-used-for-object-detection) | Classes are cardboard, glass, metal, paper, plastic and trash. It has **no organic class**. Licensed CC BY 4.0. |
| [Neat Now](https://universe.roboflow.com/fyp-gojku/neat-now) | |
| [GARBAGE CLASSIFICATION 3](https://universe.roboflow.com/objectdetection-z2zn1/garbage-classification-3-bjcgp) | Added 2026-11-15. A copy of [material-identification/garbage-classification-3](https://universe.roboflow.com/material-identification/garbage-classification-3) (CC BY 4.0); the copy's own license is not yet confirmed. BIODEGRADABLE is mapped to organic; glass and cloth are dropped. |

Check each dataset's license on its Roboflow page before using it.

## The scripts

Run them in this order, from the `ai-model/` folder. The notebook does the same steps.

| Step | Command | What it does |
|---|---|---|
| 1 | `python scripts/prepare_dataset.py <sources> --resplit --dry-run` | Shows how each source class will be mapped. Copies nothing. |
| 2 | `python scripts/prepare_dataset.py <sources> --resplit` | Builds `datasets/ecosort/` and writes `dataset_report.json`. |
| 3 | `python scripts/validate_dataset.py` | Checks the dataset. Training refuses to start until this passes. |
| 4 | `python scripts/train.py --epochs 50` | Fine-tunes YOLO nano. Stops early after 10 epochs without improvement (`--patience`). Prints validation scores per class and an overtraining check. |
| 5 | `python scripts/check_hallucinations.py --weights <run>/weights/best.pt` | Runs the model like the app does (confidence 0.35) and counts boxes on nothing, wrong classes, duplicates and items with no box. Saves the worst photos. |
| 6 | `python scripts/predict.py photo.jpg` | Runs the model on one photo and saves a copy with boxes drawn. |
| 7 | `python scripts/evaluate.py --split test` | The final score. Run once, at the very end. |

`python scripts/overfit_check.py <run folder>` runs the overtraining check on any finished run, including old ones.

`<sources>` is the list of downloaded dataset folders, for example `downloads/trash-detection downloads/trashnet downloads/neat-now downloads/garbage-cls-3`.

### How classes are merged

`prepare_dataset.py` turns each dataset's own class names into our four:

- It matches class names by keyword. "PET Bottle" becomes plastic, "Card Board Paper" becomes paper, "Can/Metal" becomes metal.
- Classes that are none of our four, such as glass, battery and general trash, are dropped.
- Classes it cannot decide, such as a plain "bottle", are dropped and listed so you can decide. Put your decision in `configs/class_overrides.yaml`.
- Boxes that are empty or lie outside the image are removed, and boxes that stick out are trimmed to the image.
- Photos from all sources are copied into one folder with the source name in front, so file names never clash.
- Identical image files are kept once. Public datasets often contain each other's photos under different names.
- With `--resplit`, the sources' own train/valid/test folders are ignored and one fresh 70/20/10 split is made. Copies of one original photo, and pictures that look the same, always go into the same split. Use it whenever you merge datasets from different authors.

The keyword mapping is a first draft. A person must review it and record the result in [docs/dataset-card.md](../docs/dataset-card.md).

### What the check looks for

`validate_dataset.py` stops with an error for:

- an image that will not open, or an image and label file that do not come as a pair
- a box with an unknown class, a bad number, no size, or a position outside the image
- the same image file, or augmented copies of one Roboflow photo, in more than one split
- a class with no boxes at all

It warns about a class with under 10% of the boxes, a class missing from the validation or test split, and pictures that look identical across splits. Expect organic to be the weak class; fix it by adding your own annotated photos of peels and food scraps as one more source folder.

If it reports photos in more than one split, the dataset was built without `--resplit`. Delete `datasets/ecosort/` and run step 2 again with it.

One kind of overlap cannot be detected: the same photo present in two sources with different augmentations applied (flipped in one, rotated in the other). After merging overlapping public datasets, treat test scores as somewhat optimistic, and check the model on your own fresh photos.

### Training and scoring

- `train.py` picks the best checkpoint on the validation split and never reads the test split.
- Each run is saved in `ai-model/runs/<name>/`, with `weights/best.pt` and a `run_info.json` recording the seed, settings, package versions and scores.
- Copy `best.pt` to `ai-model/weights/best.pt` for the backend.
- Record every run in [docs/training-log.md](../docs/training-log.md).

Test hard cases with `predict.py`: crushed bottles, low light, overlapping items, a photo with no waste.

## Running the steps by hand

```
pip install -r requirements.txt
```

Then follow the table above.

## Checking that your setup works

To try the whole pipeline in about five minutes on a laptop CPU, without downloading a dataset:

```
python tests/make_synthetic_dataset.py /tmp/synthetic
python scripts/validate_dataset.py /tmp/synthetic
python scripts/train.py --data /tmp/synthetic/data.yaml --epochs 30 --imgsz 320 --name smoke
```

The synthetic dataset is coloured rectangles, not waste. A model trained on it scores close to perfect because the task is trivial. It proves the scripts run; it is not a result.

## Tests

```
pip install -r requirements-dev.txt
pytest
```

These cover the class mapping, the merge and the dataset check, and need no PyTorch. They also run on GitHub for every push.

What has been run so far:

- All the scripts above have been run end to end on the synthetic dataset, on a CPU.
- No real waste dataset has been merged and checked yet, and no real model has been trained to completion.
