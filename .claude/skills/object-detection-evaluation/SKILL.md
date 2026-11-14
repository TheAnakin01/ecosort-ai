---
name: object-detection-evaluation
description: Evaluate EcoSort AI object detectors with appropriate detection metrics, per-class analysis, threshold selection, and failure analysis.
---

# Object Detection Evaluation

## Goal

Measure whether EcoSort AI detects and classifies multiple waste objects reliably. Do not substitute image-classification accuracy for object-detection metrics.

## Required metrics

Use metrics appropriate to the selected evaluation library and report definitions precisely:
- mAP at IoU 0.50 (`mAP@0.50`)
- mAP averaged across IoU thresholds 0.50:0.95 (`mAP@0.50:0.95`) when supported
- Per-class precision and recall
- Per-class AP
- Confusion/error analysis, including background false positives and missed detections
- Inference latency and model size as separate deployment metrics

State the IoU thresholds, confidence threshold, matching policy, class averaging method, and evaluation implementation.

## Evaluation protocol

1. Freeze the test split before model selection.
2. Tune confidence and NMS settings on validation data only.
3. Run final evaluation once the model/configuration is selected.
4. Evaluate all four classes independently and overall.
5. Inspect qualitative predictions for each class, including crowded scenes and small/occluded objects.
6. Compare against a simple, clearly defined baseline.
7. Record hardware, runtime, batch size, image size, and preprocessing in latency reports.

## Error analysis

Create a categorized error set:
- False positive material predictions
- Missed small objects
- Overlapping/crowded objects
- Transparent or reflective items
- Poor lighting and motion blur
- Occlusion and truncation
- Composite or contaminated waste
- Confusion between visually similar classes

Report class imbalance and sample counts alongside metrics. A strong aggregate score can hide poor performance on a minority class.

## Confidence and product behavior

Choose confidence thresholds using validation evidence and product trade-offs. Explain the impact of false positives versus missed objects. Do not present low-confidence detections as certain recycling instructions.

## Integrity rules

- Never fabricate, estimate, or round metrics to make results look better.
- Never report training metrics as test metrics.
- Never call image-level accuracy “detection accuracy” without a precise definition.
- Do not compare metrics from incompatible datasets, splits, IoU thresholds, or evaluation protocols as if directly comparable.
- Include uncertainty and limitations.

## Deliverables

Provide a reproducible evaluation command/script, machine-readable results, per-class table, plots where useful, qualitative examples, and a short honest interpretation.
