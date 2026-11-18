# Dataset card

**Dataset built:** 2026-11-15T07:30:44+00:00 (UTC), in Google Colab, by the project owner.
**Used for:** training run `ecosort-baseline-2`.

The numbers below come from that build's `dataset_report.json`. Where something was not recorded, this card says so.

## Sources

### `ecosort-baseline-2` build (2026-11-15, historical — 3 sources)

| Dataset | Link | Version | License | Downloaded on |
|---------|------|---------|---------|---------------|
| Trash Detection (`trash-detection`) | https://universe.roboflow.com/amongus-o6ilp/trash-detection-1fjjc-ipij8 | Newest at download; **not recorded** | UNKNOWN — not checked | 2026-11-15 |
| TrashNet: annotated images of trash (`trashnet`) | https://universe.roboflow.com/polygence-project/trashnet-a-set-of-annotated-images-of-trash-that-can-be-used-for-object-detection | Newest at download; **not recorded** | CC BY 4.0 (per its Roboflow page, read 2026-11-14) | 2026-11-15 |
| Neat Now (`neat-now`) | https://universe.roboflow.com/fyp-gojku/neat-now | Newest at download; **not recorded** | UNKNOWN — not checked | 2026-11-15 |

### Current build preparation (2026-11-18, 4 sources — pinned)

Versions verified via Roboflow API on 2026-11-18 and pinned in `ai-model/configs/datasets.yaml`. Do not silently update.

| Dataset | Link | Pinned version | License | Status |
|---------|------|----------------|---------|--------|
| Trash Detection (`trash-detection`) | https://universe.roboflow.com/amongus-o6ilp/trash-detection-1fjjc-ipij8 | **v1** (only available) | UNKNOWN — not checked on Roboflow page | Not cleared for commercial use, public redistribution, or competition submission |
| TrashNet: annotated images of trash (`trashnet`) | https://universe.roboflow.com/polygence-project/trashnet-a-set-of-annotated-images-of-trash-that-can-be-used-for-object-detection | **v20** (newest of 18 available) | CC BY 4.0 (per its Roboflow page, read 2026-11-14) | License confirmed on source page; verify terms before submission |
| Neat Now (`neat-now`) | https://universe.roboflow.com/fyp-gojku/neat-now | **v10** (newest of 8 available) | UNKNOWN — not checked on Roboflow page | Not cleared for commercial use, public redistribution, or competition submission |
| GARBAGE CLASSIFICATION 3 (`garbage-cls-3`) | https://universe.roboflow.com/objectdetection-z2zn1/garbage-classification-3-bjcgp | **v5** (newest of 5 available) | UNKNOWN for this copy — not checked. The original it copies, [material-identification/garbage-classification-3](https://universe.roboflow.com/material-identification/garbage-classification-3), is CC BY 4.0, but **a copied dataset does not automatically inherit the original's license** | Copy-license uncertainty recorded separately; not cleared for commercial use, public redistribution, or competition submission |

The copy first chosen (ginas-workspace/garbage-classification-3-p5ly0) has no downloadable version on Roboflow, so this copy was used instead.

### Version pinning (reproducibility)

Dataset versions are configured centrally in `ai-model/configs/datasets.yaml`.
Each of the four datasets may pin an explicit version:

- If `version` is set, `scripts/download_datasets.py` downloads exactly that
  version. If the version is unavailable on Roboflow, the download fails with a
  clear error — it never silently substitutes another version.
- If `version` is null or unset (current state for all four datasets), the
  script downloads the newest downloadable version and prints a warning that
  the build is not reproducible.

After a download, the script writes `downloads/download_manifest.json`
recording, for each dataset: workspace, project, requested version, selected
version, dataset identifier, and download timestamp. `scripts/prepare_dataset.py`
reads this manifest and records `source_versions` in
`datasets/ecosort/dataset_report.json`, so every build record shows exactly
which dataset versions were used.

**Current state (2026-11-18):** All four dataset versions are **pinned** in `configs/datasets.yaml` (trash-detection v1, trashnet v20, neat-now v10, garbage-cls-3 v5) based on Roboflow API availability checks on 2026-11-18. For trashnet and neat-now, the versions used in `ecosort-baseline-2` were not recorded, so the newest available versions at rebuild time were pinned for reproducibility of the new build. Do not silently update pinned versions.

Never assume a dataset is commercially usable without evidence. Licenses marked
UNKNOWN must be checked on each dataset's Roboflow page before the model is
used in a submission.

### Pre-submission license check

Before using the trained model in any submission, confirm the license of every
dataset. The following licenses are **UNKNOWN** and must be verified:

- Trash Detection (`amongus-o6ilp/trash-detection-1fjjc-ipij8`)
- Neat Now (`fyp-gojku/neat-now`)
- GARBAGE CLASSIFICATION 3 copy
  (`objectdetection-z2zn1/garbage-classification-3-bjcgp`)

TrashNet (`polygence-project/trashnet-a-set-of-annotated-images-of-trash-that-can-be-used-for-object-detection`)
is CC BY 4.0 (confirmed on its Roboflow page, 2026-11-14). The original that
GARBAGE CLASSIFICATION 3 copies
(`material-identification/garbage-classification-3`) is CC BY 4.0, but **a
copied dataset does not automatically inherit the original's license** — the
copy's own license must be checked separately.

## Size

49,385 labelled boxes on 22,199 images.

| Split | Images | Images with no boxes | paper | plastic | metal | organic |
|---|---|---|---|---|---|---|
| train | 15,518 | 9 | 9,793 | 10,669 | 8,646 | 5,574 |
| val | 4,525 | 1 | 2,764 | 3,051 | 2,461 | 1,962 |
| test | 2,156 | not recorded | 1,342 | 1,145 | 1,233 | 745 |
| **all** | **22,199** | | **13,899** | **14,865** | **12,340** | **8,281** |

Share of boxes: paper 28%, plastic 30%, metal 25%, organic 17%. Organic is the smallest class but is not rare.

## How it was built

### `ecosort-baseline-2` (2026-11-15, historical)

```
python scripts/prepare_dataset.py downloads/trash-detection downloads/trashnet downloads/neat-now --resplit
```

- `--resplit` was used: the sources' own splits were ignored and one fresh 70/20/10 split was made, keeping copies of a photo and look-alike pictures together.
- Identical image files removed: 596. The three sources contain each other's photos under different names.
- Of those, 585 had label lines that differed between the two copies. It is not known whether the classes differed or only the box positions. The first copy's labels were kept.
- Photos left out because every item in them was excluded: 18,408.
- Boxes dropped because their class was excluded: 47,366.
- Invalid boxes removed: 1. Boxes listed twice and kept once: 7.

## Checks

- [x] `validate_dataset.py` finished with 0 errors (reported by the project owner; the output was not saved).
- [x] No identical file or same-named photo in more than one split (enforced by the check above).
- [ ] A sample of images from every class and split looked at by a person.
- [ ] Every source's license recorded.
- [ ] Class mapping reviewed and signed off by the team (see below).

An earlier build without `--resplit` failed this check with 436 errors: 263 identical files and 173 same-named photos in more than one split.

## Class mapping

This is the mapping the first model was trained with. It was produced by keyword matching, with one manual override (`cardboard` to `paper`). It was reviewed after training, on 2026-11-15, and the review found two wrong mappings.

"Boxes dropped" is filled in for excluded classes. Box counts for included classes were not recorded per source class.

| Source dataset | Source class | EcoSort class | Boxes dropped | Review notes |
|---|---|---|---|---|
| trash-detection | Aerosol | exclude | 10 |  |
| trash-detection | Aluminium blister pack | metal |  | Review: foil and plastic. |
| trash-detection | Aluminium foil | metal |  |  |
| trash-detection | Battery | exclude | 2 |  |
| trash-detection | Broken glass | exclude | 138 |  |
| trash-detection | Carded blister pack | exclude | 1 |  |
| trash-detection | Cigarette | exclude | 667 |  |
| trash-detection | Clear plastic bottle | plastic |  |  |
| trash-detection | Corrugated carton | paper |  |  |
| trash-detection | Crisp packet | exclude | 39 |  |
| trash-detection | Disposable food container | organic |  | **Wrong.** A container, not food. Fixed to `exclude` for the next run. |
| trash-detection | Disposable plastic cup | plastic |  |  |
| trash-detection | Drink can | metal |  |  |
| trash-detection | Drink carton | paper |  | Review: paper, plastic and foil layers. |
| trash-detection | Egg carton | paper |  |  |
| trash-detection | Foam cup | exclude | 13 | Suggest `plastic`. Team to decide. |
| trash-detection | Foam food container | organic |  | **Wrong.** A foam container, not food. Fixed to `exclude` for the next run. |
| trash-detection | Food Can | exclude | 34 | A metal can. Will be `metal` in the next run. |
| trash-detection | Food waste | organic |  |  |
| trash-detection | Garbage bag | exclude | 31 |  |
| trash-detection | Glass | exclude | 227 |  |
| trash-detection | Glass bottle | exclude | 104 |  |
| trash-detection | Glass cup | exclude | 6 |  |
| trash-detection | Glass jar | exclude | 6 |  |
| trash-detection | Magazine paper | paper |  |  |
| trash-detection | Meal carton | paper |  |  |
| trash-detection | Metal | metal |  |  |
| trash-detection | Metal bottle cap | metal |  |  |
| trash-detection | Metal lid | metal |  |  |
| trash-detection | Normal paper | paper |  |  |
| trash-detection | Other carton | paper |  |  |
| trash-detection | Other plastic | plastic |  |  |
| trash-detection | Other plastic bottle | plastic |  |  |
| trash-detection | Other plastic container | plastic |  |  |
| trash-detection | Other plastic cup | plastic |  |  |
| trash-detection | Other plastic wrapper | plastic |  |  |
| trash-detection | Paper | paper |  |  |
| trash-detection | Paper bag | paper |  |  |
| trash-detection | Paper cup | paper |  | Review: usually has a plastic lining. |
| trash-detection | Paper straw | paper |  |  |
| trash-detection | Pizza box | exclude | 3 | Suggest `paper`. Team to decide. |
| trash-detection | Plastic | plastic |  |  |
| trash-detection | Plastic bottle cap | plastic |  |  |
| trash-detection | Plastic film | plastic |  |  |
| trash-detection | Plastic glooves | plastic |  |  |
| trash-detection | Plastic lid | plastic |  |  |
| trash-detection | Plastic straw | plastic |  |  |
| trash-detection | Plastic utensils | plastic |  |  |
| trash-detection | Polypropylene bag | exclude | 3 | Suggest `plastic`. Team to decide. |
| trash-detection | Pop tab | exclude | 99 | Suggest `metal`. Team to decide. |
| trash-detection | Rope - strings | exclude | 29 |  |
| trash-detection | Scrap metal | metal |  |  |
| trash-detection | Shoe | exclude | 7 |  |
| trash-detection | Single-use carrier bag | exclude | 61 | Suggest `plastic`. Team to decide. |
| trash-detection | Six pack rings | exclude | 5 |  |
| trash-detection | Spread tub | exclude | 9 |  |
| trash-detection | Squeezable tube | exclude | 7 |  |
| trash-detection | Styrofoam piece | plastic |  | Polystyrene foam, counted as plastic. |
| trash-detection | Tissues | exclude | 42 |  |
| trash-detection | Toilet tube | exclude | 5 | Suggest `paper`. Team to decide. |
| trash-detection | Tupperware | exclude | 4 |  |
| trash-detection | Unlabeled litter | exclude | 517 |  |
| trash-detection | Waste | exclude | 10 |  |
| trash-detection | Wrapping paper | paper |  |  |
| trashnet | cardboard | paper |  |  |
| trashnet | glass | exclude | 3,266 |  |
| trashnet | metal | metal |  |  |
| trashnet | paper | paper |  |  |
| trashnet | plastic | plastic |  |  |
| trashnet | trash | exclude | 884 |  |
| neat-now | Animal Waste | exclude | 8,191 | Not food or garden waste, so not our organic class. |
| neat-now | Construction Waste | exclude | 4,770 |  |
| neat-now | Garbage Bag | exclude | 8,615 |  |
| neat-now | Glass | exclude | 8,385 |  |
| neat-now | Metal | metal |  |  |
| neat-now | Organic | organic |  |  |
| neat-now | Paper | paper |  |  |
| neat-now | Plastic | plastic |  |  |
| neat-now | waste | exclude | 11,176 |  |

### What the review found

- **Two classes were taught as organic by mistake:** "Disposable food container" and "Foam food container". The keyword "food" matched them. The model in run `ecosort-baseline-2` therefore saw some containers labelled as organic waste. How many boxes is not recorded.
- **Fixed for the next run:** both are now excluded, and the mapper no longer treats packaging that held food as organic. "Food Can" will be mapped to metal.
- **Waiting for a team decision:** the rows marked "Suggest" and "Review". They are listed in `ai-model/configs/class_overrides.yaml`.

Rules used when mapping:

- Glass, batteries, e-waste and general "trash" or "waste" are excluded. They are none of the four classes.
- A class naming two materials, or none, is excluded unless a reviewer decides otherwise.
- Packaging is never organic, whatever it contained.
- Nothing is relabelled to balance the classes.

## Known gaps

- **Overlap that cannot be detected.** The sources share photos. Identical and look-alike copies were handled, but the same photo with different augmentations in two sources (flipped in one, rotated in the other) cannot be found. Validation and test scores may be somewhat optimistic.
- **Wrong labels in the first model's training data:** see the review above.
- **Mixed materials.** Paper cups, drink cartons and blister packs are counted as one material.
- **Local conditions.** None of the photos were taken by the team. Indian packaging, mixed household waste and indoor lighting may be under-represented.
- **Excluded items stay in the photos.** A photo can show glass or general litter with no box on it. The model is taught to ignore those, which is intended, but it means the app says nothing about them.

## Our own photos

None added yet. If the team adds photos: take them with permission, keep people and personal details out of frame, and annotate them in Roboflow as one more source.
