---
name: waste-dataset-engineering
description: Find, inspect, license-check, normalize, annotate, split, and validate waste object-detection datasets for EcoSort AI.
---

# Waste Dataset Engineering

## Goal

Prepare a legally usable, quality-controlled object-detection dataset for four canonical classes: `paper`, `plastic`, `metal`, `organic`.

## Dataset discovery

Potential sources may include TACO, Roboflow Universe datasets, and images collected with permission. For each source, verify:
- Original dataset page and maintainer
- License and commercial/redistribution restrictions
- Image count and annotation count
- Annotation type (image-level labels vs bounding boxes or masks)
- Class taxonomy and ambiguous categories
- Image quality, duplicates, and domain relevance
- Whether annotations can be converted to the selected detector's format

Never assume that a dataset is free for any use merely because it is downloadable.

## Taxonomy mapping

Create a version-controlled mapping table:
- Source dataset
- Original label
- Canonical label (`paper`, `plastic`, `metal`, `organic`) or `exclude`
- Mapping rationale
- Ambiguity notes

Do not force an uncertain label into a canonical class. Keep an explicit `unknown/excluded` policy. Define how composite, dirty, crushed, transparent, or partially occluded objects are handled.

## Annotation requirements

- Use object-level bounding boxes for every visible target instance.
- Preserve multiple instances of the same class in one image.
- Use one coordinate convention internally and document it.
- Validate positive width/height and image-bound constraints.
- Define treatment of truncated, occluded, tiny, and ambiguous objects.
- Prefer double review or adjudication for uncertain labels.
- Keep annotation guidelines and version them.

## Splitting and leakage prevention

- Split by original image/source group before augmentation.
- Detect exact and near duplicates where feasible.
- Do not allow augmented variants of one source image across different splits.
- Keep a held-out test set untouched until final evaluation.
- Report image counts and object counts per class for every split.

## Quality checks

Automate checks for:
- Missing or unreadable images
- Missing annotation files
- Invalid class IDs
- Out-of-bounds or zero-area boxes
- Duplicate boxes
- Empty annotations
- Unexpected image dimensions
- Class imbalance
- Duplicate/near-duplicate images

Manually inspect a representative sample from every class and split.

## Augmentation

Use realistic training-only augmentation. Consider lighting, scale, crop, rotation, blur, compression, and background variation. Transform boxes with every geometric operation. Avoid transformations that make material identity unrealistic or destroy small objects.

## Deliverables

Produce:
- Dataset source and license register
- Taxonomy mapping
- Annotation guide
- Train/validation/test manifest
- Dataset statistics
- Validation script and report
- A small visualized annotation sample
- Known coverage gaps

Do not report a dataset as ready until the annotation format matches the chosen detector and automated validation passes.
