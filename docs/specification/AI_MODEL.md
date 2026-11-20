# AI Model Specification

## 1. Task definition

This is a **multi-object detection** problem, not a single-label image classification problem.

Input: one image containing zero or more waste objects.  
Output: zero or more detections, each with a bounding box, class and confidence.

## 2. Initial label taxonomy

| Class ID | Canonical label | Meaning |
|---:|---|---|
| 0 | `paper` | Visually identifiable paper/cardboard-based waste |
| 1 | `plastic` | Visually identifiable plastic waste |
| 2 | `metal` | Visually identifiable metal waste |
| 3 | `organic` | Food scraps and other clearly organic waste |

The four-class taxonomy is intentionally broad. It does not claim exact chemical composition. Composite packaging and ambiguous objects require an explicit annotation policy. If an object cannot be confidently assigned, omit it from the four-class training labels or track it as an unsupported/ambiguous case outside the production taxonomy.

## 3. Model direction

- Start from a supported pretrained Ultralytics YOLO nano object-detection checkpoint.
- Fine-tune on a validated custom dataset in YOLO detection format.
- Use PyTorch/Ultralytics.
- Keep the exact model variant and package version in experiment records.
- Do not build a custom CNN/transformer hybrid before establishing a reproducible baseline.

A separate image-classification model may be used as an educational baseline, but it cannot replace the multi-object detector.

## 4. Training workflow

1. Inspect images, annotations and licenses.
2. Normalize source annotations into the four-class taxonomy.
3. Remove corrupt images and invalid boxes.
4. Review class mapping and ambiguous items.
5. Deduplicate near-identical images.
6. Split by source scene/session where possible to prevent leakage.
7. Train a baseline with documented configuration and seed.
8. Evaluate on validation data and inspect errors.
9. Tune thresholds using validation data only.
10. Run final evaluation once on held-out test data.
11. Save weights, config, class map, package versions and metrics.

## 5. Dataset split

A provisional 70/20/10 train/validation/test split can be used if the dataset is large enough. Adjust based on dataset size and class balance. Keep images from the same burst, video, scene or near-duplicate source in the same split. The test set must remain untouched during tuning.

## 6. Inference configuration

Configurable values should include:
- `confidence_threshold`
- `iou_threshold` for NMS
- image size
- maximum detections
- device (`cpu`, `cuda`, or supported accelerator)

Do not hard-code thresholds without validation. The backend should expose model/version metadata for debugging, not allow arbitrary public users to change unsafe inference settings.

## 7. Post-processing

- Convert model class IDs to canonical names.
- Remove invalid boxes.
- Clip coordinates to original oriented image dimensions.
- Return confidence as a float in `[0,1]`.
- Apply NMS through the model framework unless a documented reason requires custom handling.
- Keep deterministic sorting (e.g. confidence descending) for stable UI/testing.
- Count detections by canonical category.

## 8. Evaluation metrics

Report:
- Precision and recall.
- mAP@50.
- mAP@50–95.
- Per-class precision/recall/AP.
- Confusion matrix where appropriate.
- Inference time and image size/hardware.
- Error examples: false positives, false negatives, duplicate boxes, localization errors.

Do not use “accuracy” as the only metric for object detection. Never fabricate numbers. A metric is meaningful only with a named dataset split, evaluation procedure, model version and date.

## 9. Robustness test set

Include varied:
- Indoor/outdoor backgrounds.
- Daylight and artificial lighting.
- Transparent and reflective packaging.
- Crushed, folded and partially hidden objects.
- Wet/dirty items.
- Small objects and clutter.
- Multiple objects touching or overlapping.
- Different camera distances and angles.
- Local waste types not overrepresented in public data.

## 10. Model limitations

A visual detector may confuse materials based on appearance. It cannot reliably infer hidden layers, exact polymer/resin, food contamination, safety hazards or local recycling acceptance. UI guidance must preserve these limitations.

## 11. Model artifact management

Track:
- Model architecture/checkpoint source and license.
- Fine-tuned weights identifier and checksum.
- Training config and random seed.
- Dataset version and split manifest.
- Metrics and evaluation date.
- Inference package versions.

Do not commit large weights or datasets to Git by default. Use an approved artifact store or release asset if needed.
