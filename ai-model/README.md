# AI model

Trains a YOLO nano detector on four classes: paper, plastic, metal, organic.

## The quick way: the Colab notebook

[Open the notebook in Colab](https://colab.research.google.com/github/TheAnakin01/ecosort-ai/blob/main/ai-model/notebooks/train_ecosort.ipynb) and run it top to bottom. It downloads the three Roboflow datasets, merges them, trains, and gives you `best.pt`.

The only thing you supply is your Roboflow API key (Roboflow → Settings → API Keys). The notebook asks for it when it runs and does not save it.

Datasets the team picked:

| Dataset | Notes |
|---|---|
| [Trash Detection](https://universe.roboflow.com/amongus-o6ilp/trash-detection-1fjjc-ipij8) | |
| [TrashNet: annotated images of trash](https://universe.roboflow.com/polygence-project/trashnet-a-set-of-annotated-images-of-trash-that-can-be-used-for-object-detection) | Classes are cardboard, glass, metal, paper, plastic and trash. It has **no organic class**. Licensed CC BY 4.0. |
| [Neat Now](https://universe.roboflow.com/fyp-gojku/neat-now) | |

Check each dataset's license on its Roboflow page before using it.

## What the merge does

`scripts/prepare_dataset.py` turns each dataset's own class names into our four:

- It matches class names by keyword. "PET Bottle" becomes plastic, "Card Board Paper" becomes paper, "Can/Metal" becomes metal.
- Classes that are none of our four, such as glass, battery and general trash, are dropped.
- Classes it cannot decide, such as a plain "bottle", are dropped and listed so you can decide. Put your decision in `configs/class_overrides.yaml`.
- Photos from all sources are copied into one folder with the source name in front, so file names never clash.

Always run it with `--dry-run` first and read the report:

```
python scripts/prepare_dataset.py downloads/trash-detection downloads/trashnet downloads/neat-now --dry-run
```

The report shows **Boxes per class**. A class with under 10% of the boxes is flagged. Expect organic to be the weak one; fix it by adding your own annotated photos of peels and food scraps, exported from Roboflow as one more source folder.

## Running the steps by hand

```
pip install -r requirements.txt
python scripts/prepare_dataset.py downloads/a downloads/b downloads/c
python scripts/train.py --epochs 50
python scripts/predict.py my_photo.jpg
```

- `train.py` saves the best model to `runs/detect/ecosort-baseline/weights/best.pt`. Copy it to `ai-model/weights/best.pt` for the backend.
- `predict.py` prints each item found and saves a copy of the photo with boxes drawn.

Record every training run in [docs/training-log.md](../docs/training-log.md). Test hard cases: crushed bottles, low light, overlapping items, a photo with no waste.

## Tests

```
pip install -r requirements-dev.txt
pytest
```

These cover the class mapping and the merge. Training and prediction have not been run yet, because that needs the real datasets and a GPU.
