---
name: yolo-waste-detection
description: Train and fine-tune the approved YOLO nano object detector for EcoSort AI by transfer learning. Use for training pipelines, fine-tuning decisions, reproducibility, and for writing up any proposal to change the model architecture.
---

# YOLO Waste Detection for EcoSort AI

## Goal

Build a lightweight model that detects **several waste objects in one image** and assigns each object one of the canonical classes: `paper`, `plastic`, `metal`, `organic`.

## Non-negotiable distinction

Image classification returns a label for an entire image. Object detection returns multiple instances with bounding boxes and labels. EcoSort AI requires object detection. An image classifier alone, MobileNet or otherwise, is not an acceptable final model.

## Approved baseline

The approved detector is a pretrained **Ultralytics YOLO nano** model, fine-tuned for the four classes. The existing pipeline lives in `ai-model/`:

- `configs/data.yaml` — dataset paths and the class-index mapping
- `scripts/prepare_dataset.py` — merges source datasets into the four classes
- `scripts/train.py` — fine-tunes from pretrained weights
- `scripts/predict.py` — runs the trained model on one image
- `notebooks/train_ecosort.ipynb` — the same steps for Google Colab

Work within this pipeline. Do not replace YOLO with another model family and do not rewrite the training pipeline.

Before changing training code, check the current official Ultralytics documentation for the installed package version. Record the exact model variant and package version with every experiment.

## Proposing a different architecture

A change of model family needs the product owner's explicit approval. Other lightweight detectors, such as SSD/SSDLite with a MobileNet backbone, have been discussed but are not approved. If the evidence suggests an alternative is worth considering, write it up as a separate proposal and change no code until it is approved.

For every candidate in a proposal, verify:
1. Current official documentation and maintenance status
2. Supported training framework and versions
3. Availability and license of pretrained detection weights
4. Dataset annotation format expected
5. Transfer-learning procedure and supported detection head
6. Export path to the intended runtime
7. CPU/mobile/backend inference compatibility
8. Model size, expected latency, and hardware requirements

Compare each candidate against measured results from the YOLO nano baseline, not against expectations. Do not propose a model solely because an old tutorial or GitHub example exists, and document the risk of any deprecated or dependency-fragile API.

## Transfer-learning procedure

For the approved YOLO nano baseline:
1. Load verified pretrained **detection** weights.
2. Configure the detector for the four project classes through the dataset configuration; follow the framework's own convention for background handling.
3. Verify label-index conventions. Keep a single documented mapping across training, API, and app.
4. Establish a reproducible baseline before fine-tuning.
5. Initially freeze the backbone if appropriate for the selected implementation.
6. Train the detection head and inspect loss curves and validation predictions.
7. Unfreeze selected backbone layers gradually only if validation evidence supports it.
8. Use a conservative learning rate for fine-tuning.
9. Apply early stopping or checkpoint selection using validation metrics, not test-set performance.
10. Save the exact configuration, checkpoint, class mapping, and environment versions.

Do not prescribe exact layer names or freeze counts until the installed model implementation has been inspected.

## Training hygiene

- Split by source/image identity before augmentation to prevent leakage.
- Keep train, validation, and test sets separate.
- Apply augmentation only to training data.
- Ensure bounding boxes are transformed consistently with image augmentation.
- Track class counts and object counts per split.
- Inspect examples and predictions, not just aggregate losses.
- Record seeds, package versions, hardware, batch size, image size, optimizer, learning rate, epochs, and checkpoint-selection rule.
- Do not use test data for hyperparameter tuning.

## Class and label handling

Canonical app classes are `paper`, `plastic`, `metal`, `organic`. Dataset source labels must be mapped deliberately. Do not silently map ambiguous materials or contaminated/mixed items. Keep an explicit mapping file and document excluded labels.

## Required outputs

For each experiment, produce:
- Model/architecture name and exact implementation source
- Pretrained checkpoint provenance and license
- Dataset version and split manifest
- Training configuration
- Training and validation curves
- Best checkpoint selection rationale
- Per-class evaluation
- Known failure cases
- Export compatibility findings

## Stop conditions

Stop and ask for a decision if:
- A task would require changing the model family or rewriting the training pipeline.
- The candidate is only an image classifier.
- No reliable pretrained detection checkpoint or viable training route exists.
- The training API is unmaintained or incompatible with supported dependencies.
- Dataset annotations cannot represent multiple boxes per image.
- The deployment target is unclear and materially changes architecture choice.
