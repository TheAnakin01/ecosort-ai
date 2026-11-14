# Dataset and Annotation Plan

## 1. Data requirements

The model requires object-detection annotations: each visible supported object needs a bounding box and class. A folder of images with one label per image is not sufficient for the primary task.

## 2. Candidate sources

- **TACO (Trash Annotations in Context):** https://tacodataset.org/ and https://github.com/pedropro/TACO
- **Roboflow Universe:** https://universe.roboflow.com/
- **CVAT:** https://www.cvat.ai/
- Custom photographs captured with permission and without unnecessary personal information.

These are candidate sources, not pre-approved datasets. Before use, inspect the exact dataset version, annotation format, license, attribution and usage restrictions. Record the source URL and retrieval date.

## 3. Taxonomy mapping

TACO has many fine-grained litter labels. They do not automatically map perfectly to paper/plastic/metal/organic. Create a reviewed mapping table with:
- Source dataset and source class.
- Target EcoSort class or `exclude/ambiguous`.
- Mapping rationale.
- Reviewer and review date.
- Known edge cases.

Do not map an item based only on its product name if the material is visually uncertain. Multi-material packaging should follow a written annotation policy.

## 4. Annotation policy

- Draw a tight box around the visible object.
- Avoid including unrelated background.
- Annotate distinct objects separately when they can reasonably be distinguished.
- Do not invent hidden object boundaries.
- Use consistent treatment of heavily occluded objects.
- Exclude objects too ambiguous to map reliably.
- Review boxes that are truncated, tiny, overlapping or low quality.
- Maintain an annotation guide with examples for every class.

## 5. Data quality checks

- Image decodes successfully.
- Annotation coordinates are valid and within image bounds.
- Width and height are positive.
- Class IDs exist in the canonical mapping.
- No unintended duplicate image paths.
- No train/validation/test leakage from the same scene.
- Class counts and image counts are reported.
- Visual spot-check of labels and boxes in every split.

## 6. Split strategy

Use a grouped split where possible: images from the same source scene, capture session or near-duplicate cluster must not be spread across train and test. A provisional 70/20/10 split is a starting point, not a fixed law. Preserve a held-out test set.

## 7. Dataset documentation

Create a dataset card recording:
- Dataset name/version/source/license.
- Download date and preprocessing steps.
- Included/excluded classes.
- Mapping decisions.
- Number of images and instances per class and split.
- Known biases and gaps.
- Privacy considerations for custom images.
- Reproducible split manifest or random seed.

## 8. Data augmentation

Use realistic augmentations that preserve object identity and box correctness: moderate scale, translation, horizontal flip where semantically valid, brightness/contrast and mild blur/noise. Avoid transformations that create unrealistic materials or make labels invalid. Review augmentations visually.

## 9. Do not

- Scrape images without checking rights and terms.
- Commit raw datasets to Git.
- split near-duplicate frames across train and test.
- silently relabel difficult objects to force balance.
- report performance on training data as generalization.
