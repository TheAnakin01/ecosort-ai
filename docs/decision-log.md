# Decision log

Approved project decisions, newest last. These rank above the specification and the existing code when they conflict.

## 2026-11-14 — Detector stays YOLO nano

- **Decision:** Keep the pretrained Ultralytics YOLO nano detector. Any other model family needs explicit approval before code changes.
- **Reason:** The documentation pack, the repo, the notebook and the first training attempt all use it. Round 1 is about a week away.
- **Alternatives considered:** SSD/SSDLite with a MobileNet backbone. Discussed, not approved.
- **Affected:** `ai-model/` training pipeline and model documentation.
- **Migration needed:** No.

## 2026-11-14 — Keep on-device scan history

- **Decision:** Keep the History screen. Scans and a copy of each photo are stored on the device only, and the app says so.
- **Reason:** It is built and tested, and nothing leaves the device.
- **Alternatives considered:** Keep history without photos; hide history until the scan flow is proven with a real model.
- **Affected:** `mobile/src/app/(tabs)/history.tsx`, `mobile/src/lib/store.tsx`, `mobile/src/lib/photo-store*.ts`.
- **Note:** This departs from the documentation pack, which leaves history out of the core MVP and says not to keep images by default. The backend still stores nothing.
- **Migration needed:** No.

## 2026-11-14 — Keep the general sorting guidance

- **Decision:** Keep the current tips, including the "Dry waste" and "Wet waste" bin names, shown with the local-rules caveat.
- **Reason:** They are useful as general guidance.
- **Alternatives considered:** One cautious line per material; no bin names until verified.
- **Affected:** `backend/app/guidance.py`, `mobile/src/lib/categories.ts`.
- **Known limitation:** The wording comes from general knowledge. It has not been checked against a municipal source, so it must not be presented as official local rules.
- **Migration needed:** No.

## 2026-11-14 — Keep Expo ImagePicker for the camera

- **Decision:** Use Expo ImagePicker for both camera capture and gallery selection.
- **Reason:** One dependency covers both, and it already works.
- **Alternatives considered:** Expo Camera, for a camera view inside the app.
- **Affected:** `mobile/src/app/scan.tsx`.
- **Migration needed:** No.

## 2026-11-14 — Demo runs against a public hosted backend

- **Decision:** For the Round 1 demo, host the backend publicly over HTTPS so the web app can scan from any phone.
- **Reason:** Round 1 is an online submission; a laptop on shared Wi-Fi cannot be reached by judges.
- **Alternatives considered:** Laptop backend on the same Wi-Fi; both.
- **Affected:** Deployment (Phase 8). The host is not chosen yet; the documentation pack says to choose it after measuring the model's memory and speed.
- **Migration needed:** No.

## 2026-11-15 — Serve the trained model as ONNX on onnxruntime

- **Decision:** The backend can load either `best.pt` (PyTorch/Ultralytics) or `best.onnx` (onnxruntime), chosen by the `MODEL_PATH` file extension. Deployment uses ONNX. The detector is still the same trained YOLO nano model; only the inference engine changes.
- **Reason:** Free 512 MB hosts cannot hold PyTorch (about 760 MB). The ONNX runtime path idles at about 176 MB.
- **Evidence (measured 2026-11-15, 2 vCPU Linux test machine, CPU):** raw model output differs from PyTorch by at most 0.004. Detections on the two Ultralytics sample images match PyTorch exactly (same classes, confidence within 0.01, boxes within 2 px; these are not waste photos). Peak RSS 360 MB for a 12 MP photo and 479 MB for a 24 MP photo, with no failures in a 512 MB cgroup. Warm latency 75-90 ms for a 0.9 MP photo, 230-290 ms for 12-24 MP.
- **Alternatives considered:** Keep PyTorch and pay for a larger host; laptop with a tunnel (kept as a demo fallback).
- **Not verified:** Parity on real waste photos (none available yet). Behaviour on a 0.1 vCPU free instance, where inference will be much slower. The Docker image build (later built successfully on Render, 2026-11-18).
- **Affected:** `backend/app/onnx_detector.py`, `backend/app/detector.py`, `backend/app/main.py` (fewer image copies), `backend/Dockerfile`, `backend/requirements-onnx.txt`, `ai-model/scripts/export_onnx.py`.
- **Migration needed:** No. The API contract is unchanged and PyTorch remains the default for `.pt` files.

## 2026-11-15 — Add GARBAGE CLASSIFICATION 3 as a fourth source

- **Decision:** Add [GARBAGE CLASSIFICATION 3](https://universe.roboflow.com/objectdetection-z2zn1/garbage-classification-3-bjcgp) (objectdetection-z2zn1 copy, version 5, object detection) to the merged dataset, downloaded as `garbage-cls-3`. Its BIODEGRADABLE class maps to `organic`.
- **Reason:** More variety in photos and more labelled boxes per image, to improve localisation. Plastic and metal were the weakest classes in `ecosort-baseline-2`.
- **Changed the same day:** the ginas-workspace copy picked first has no downloadable version, so the objectdetection-z2zn1 copy is used. Both copy material-identification/garbage-classification-3.
- **Alternatives considered:** Another copy of a dataset with the same name (Roboflow Universe has more than 20); dropping BIODEGRADABLE; reviewing sample photos before mapping it.
- **Affected:** `ai-model/notebooks/train_ecosort.ipynb`, `ai-model/README.md`, `docs/dataset-card.md`.
- **Known risk:** BIODEGRADABLE may contain paper or leaves as well as food. If the dry run or a sample review shows that, change it with one line in `configs/class_overrides.yaml`.
- **Migration needed:** No. The dataset must be rebuilt and the model retrained.

## 2026-11-15 — Do not use the "Waste Classification by YOLOv8" dataset for now

- **Decision:** Leave it out.
- **Reason:** It is an image-classification dataset: one label per photo, no bounding boxes. The detector needs a box for every object, so it cannot be merged as it is.
- **Alternatives considered:** Drawing boxes on it with the current model (pseudo-labelling) and reviewing a sample; finding a version of it with boxes.
- **Affected:** Nothing.
- **Migration needed:** No.

## 2026-11-15 — Guard against overtraining and check for false detections

- **Decision:** Every training run is checked for overtraining and for false detections ("hallucinations") before it is used.
- **How:** `train.py` stops after 10 epochs without improvement (was 15) and runs `overfit_check.py` at the end. `check_hallucinations.py` runs the model on the validation split with the backend's thresholds (confidence 0.35, overlap 0.7) and counts boxes where there is no labelled item.
- **Reason:** Asked for by the product owner. mAP is measured at a very low confidence threshold, so it does not show what the app will actually display.
- **Affected:** `ai-model/scripts/train.py`, `ai-model/scripts/overfit_check.py`, `ai-model/scripts/check_hallucinations.py`, the notebook, `docs/training-log.md`.
- **Migration needed:** No.

## 2026-11-15 — Keep organic to at most 30% of boxes

- **Decision:** Build the dataset with `--max-share organic=0.3`. Photos that show only organic items are left out, the most crowded first, until organic is at most 30% of all boxes.
- **Reason:** The first dry run with GARBAGE CLASSIFICATION 3 gave organic 114,043 of 204,521 boxes (56%). Its BIODEGRADABLE class has 105,816 boxes in 5,493 photos (median 6 boxes per photo, up to 358): piles of fruit and vegetables. The mapping is right (checked on sample photos by the product owner), but at that share the model would learn to guess organic, adding organic false detections. Plastic, the weakest class, would have fallen to 14%.
- **Alternatives considered:** Train as it is; drop BIODEGRADABLE (and every photo that contains it).
- **Affected:** `ai-model/scripts/prepare_dataset.py`, the notebook, `ai-model/README.md`.
- **Migration needed:** No.

## 2026-11-18 — Pin all four Roboflow dataset versions for rebuild

- **Decision:** Pin exact Roboflow versions for the 4-source rebuild: `trash-detection` v1, `trashnet` v20, `neat-now` v10, `garbage-cls-3` v5. Versions verified via Roboflow API on 2026-11-18 and recorded in `ai-model/configs/datasets.yaml`. Do not silently update.
- **Reason:** `ecosort-baseline-2` did not record source versions. `trash-detection` has only v1; `garbage-cls-3` v5 matches the prior decision log. For `trashnet` (18 versions available) and `neat-now` (8 available), newest available versions were pinned for a clean, reproducible rebuild because historical versions were unknown. All are object-detection projects.
- **Affected:** `ai-model/configs/datasets.yaml`, `ai-model/scripts/download_datasets.py` (fallback defaults), `ai-model/tests/test_download_datasets.py`, `docs/dataset-card.md`.
- **Migration needed:** No. Dataset must be rebuilt and model retrained.

## 2026-11-18 — Record dataset licenses as unresolved for internal prep

- **Decision:** Proceed with dataset download and internal training preparation while recording licenses accurately. TrashNet CC BY 4.0 (confirmed 2026-11-14 on source page). Trash Detection, Neat Now, and the `garbage-cls-3` copy (objectdetection-z2zn1) have UNKNOWN licenses; the original material-identification copy is CC BY 4.0 but a copy does not automatically inherit that license.
- **Reason:** Licenses cannot be fully verified without Roboflow page access in this environment; user approved proceeding for internal research/training preparation only.
- **Constraint:** Never mark unknown licenses as verified. Do not claim the dataset is cleared for commercial use, public redistribution, or competition submission. Source and copy-license uncertainty recorded separately.
- **Affected:** `docs/dataset-card.md`.
- **Migration needed:** No. License verification remains required before submission.

- **Decision:** The backend's default `MODEL_PATH` is now `ai-model/weights/best.onnx` (was `best.pt`, which does not exist locally). `.env.example` updated to match. The `.pt`/`.onnx` dispatch in `detector.py` is unchanged: `.onnx` loads via onnxruntime, `.pt` via Ultralytics.
- **Reason:** Only `best.onnx` (sha256 `0e38fc74...`, from run `ecosort-baseline-2`, best.pt sha256 `f2e7a74a...`) is committed. Defaulting to the missing `best.pt` left the backend unable to load its model (`/health` reported `model_loaded=false`, `/api/v1/detect` returned 503). Verified: `OnnxDetector` loads `best.onnx`, `image_size=640`, classes `paper/plastic/metal/organic`; backend tests 52 passed/6 skipped, ruff clean, pip clean.
- **Affected:** `backend/app/config.py`, `backend/.env.example`
- **Migration needed:** No. API contract unchanged.

## 2026-11-15 — Train on Kaggle when Colab's GPU is unavailable

- **Decision:** Add a Kaggle notebook (`ai-model/notebooks/train_ecosort_kaggle.ipynb`) that runs the same build and training without anyone watching.
- **Reason:** Run 2 hit Colab's free GPU limit after 4 epochs (`ecosort-baseline-3`). At about 17 minutes per epoch a 30-epoch run takes 8 to 9 hours, longer than Colab's free tier reliably allows. Kaggle has a weekly GPU quota and longer sessions.
- **How:** Same scripts and settings: four sources, `--resplit`, `--max-share organic=0.3`, 30 epochs with early stopping, then the overtraining and false-detection checks. `scripts/download_datasets.py` reads the Roboflow key from a Kaggle secret. Every step runs as its own process (no Pillow clash), and a failed step sends an ntfy notification.
- **Not resumed:** `ecosort-baseline-3` is not continued. Its checkpoint stores Colab's paths, and a fresh run keeps the comparison with run 1 clean.
- **Verified:** The whole notebook ran end to end in a simulated Kaggle setup (stand-in secrets and GPU check, synthetic datasets, 2 epochs on CPU). Not verified: an actual Kaggle session.
- **Affected:** `ai-model/notebooks/train_ecosort_kaggle.ipynb`, `ai-model/scripts/download_datasets.py`, `ai-model/README.md`.
- **Migration needed:** No.


## 2026-11-16 — Compare run 1 and run 2 before changing the app's model

- **Decision:** Do not merge run 2's `best.zip` into `main` and do not replace `ai-model/weights/best.onnx` yet. First score both models on the same validation photos, leaving out photos run 1 trained on, with `notebooks/compare_models_kaggle.ipynb`. The better model, judged on accuracy per class and on false detections at the app's settings, is then converted to ONNX and committed as `ai-model/weights/best.onnx` with its record.
- **Reason:** Run 2 scored lower than run 1 (mAP@50-95 0.564 against 0.690), but on its own, harder validation split, so the numbers cannot be compared. Run 2's validation photos can include photos run 1 trained on, because adding a dataset regroups look-alike photos. `.pt` files are kept out of Git by `.gitignore`; only the deployable ONNX model is stored.
- **Also:** The Kaggle training notebook cloned the `feature/kaggle-training-preparation` branch (from PR #5). It clones `main` again, so runs use the reviewed code. Markdown cells no longer carry an invalid `outputs` field.
- **Affected:** `ai-model/notebooks/compare_models_kaggle.ipynb`, `ai-model/scripts/make_comparison_split.py`, `ai-model/notebooks/train_ecosort_kaggle.ipynb`, `docs/training-log.md`.
- **Migration needed:** No.

## 2026-11-16 — Run 2's checkpoint kept in the repo as best.zip

- **Decision (team, PR #6):** Run 2's `best.pt` is stored in `main` as `best.zip` at the top of the repo, to preserve it. This replaces the earlier plan of keeping it on its branch only.
- **Effect on the app:** none. The backend still serves `ai-model/weights/best.onnx`, which is run 1's model, until the comparison picks a winner.
- **Comparison notebook:** downloads run 2 from `main` (same file, SHA-256 `e57748e9bdcab9d4d41bda3c0e6b502d5dada0946dc0403c3abf1f74491f6669`), so deleting the `Exit0Hero-patch-1` branch does not break it.
- **Affected:** `best.zip`, `ai-model/notebooks/compare_models_kaggle.ipynb`.

## 2026-11-17 — The app serves run 2's model

- **Decision:** `ai-model/weights/best.onnx` is now run 2's model (converted from `best.zip`, SHA-256 `e57748e9…`). Run 1's ONNX model stays in Git history at commit `042b1a3`.
- **Reason:** On 7,501 validation photos neither model trained on, run 2 beat run 1 on every accuracy score (mAP@50-95 0.550 against 0.386, recall 0.622 against 0.466, better AP for every class) and had a lower share of boxes on nothing at the app's settings (5.8% against 7.5%). Organic false detections rose (4.0% to 7.6%). See `training-log.md`.
- **Checked:** The backend's ONNX detector and the PyTorch model gave the same 555 boxes (same class, IoU above 0.95, confidence gap 0.0000) on the 24 real photos in PR #9; the backend tests and the ONNX parity test pass with it.
- **Affected:** `ai-model/weights/best.onnx`, `ai-model/weights/best.onnx.json`, `ai-model/notebooks/compare_models_kaggle.ipynb` (run 1 now downloaded from commit `042b1a3`).
- **Migration needed:** None in the repo. Any running backend loads the model at start-up, so restart or redeploy it to pick up the new file.
