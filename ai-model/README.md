# AI model

Trains a YOLO nano detector on four classes: paper, plastic, metal, organic.

## 1. Build the dataset

The detector needs photos with a box drawn around every waste item. Sorted folders of photos are not enough.

1. Find annotated waste datasets on [Roboflow Universe](https://universe.roboflow.com/) and export them in **YOLO format**. Check each dataset's license.
2. Edit `CLASS_MAP` in `scripts/remap_labels.py` so the dataset's class names map to our four, then run:

   ```
   python scripts/remap_labels.py source/data.yaml source/labels datasets/ecosort/labels
   ```

   It prints how many boxes each class ended up with. Watch the organic count: most public sets have very little of it.
3. Copy the matching images into `datasets/ecosort/images/`, keeping the same train/val/test folders.
4. Add your own photos, annotated in Roboflow, especially organic waste.

Expected layout:

```
datasets/ecosort/
  images/train  images/val  images/test
  labels/train  labels/val  labels/test
```

## 2. Train (Google Colab, free GPU)

Upload the dataset to Google Drive, then in a Colab notebook with the GPU runtime on:

```
!git clone https://github.com/TheAnakin01/ecosort-ai
%cd ecosort-ai/ai-model
!pip install ultralytics
!python scripts/train.py --epochs 50
```

The best model is saved as `runs/detect/ecosort-baseline/weights/best.pt`. Download it and put it at `ai-model/weights/best.pt`.

Record every run in [docs/training-log.md](../docs/training-log.md).

## 3. Try it on a photo

```
python scripts/predict.py my_photo.jpg
```

It prints each item found and saves `my_photo_detected.jpg` with the boxes drawn. Test hard cases: crushed bottles, low light, overlapping items, a photo with no waste.
