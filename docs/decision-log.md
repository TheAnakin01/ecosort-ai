# Decision log

Approved project decisions, newest last. These rank above the documentation pack and the existing code when they conflict (see `CLAUDE.md`).

## 2026-11-14 — Detector stays YOLO nano

- **Decision:** Keep the pretrained Ultralytics YOLO nano detector. Any other model family needs explicit approval before code changes.
- **Reason:** The documentation pack, the repo, the notebook and the first training attempt all use it. Round 1 is about a week away.
- **Alternatives considered:** SSD/SSDLite with a MobileNet backbone. Discussed, not approved.
- **Affected:** `CLAUDE.md`, `.claude/skills/yolo-waste-detection/`.
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
- **Evidence (measured 2026-11-15, 2 vCPU sandbox, CPU):** raw model output differs from PyTorch by at most 0.004. Detections on the two Ultralytics sample images match PyTorch exactly (same classes, confidence within 0.01, boxes within 2 px; these are not waste photos). Peak RSS 360 MB for a 12 MP photo and 479 MB for a 24 MP photo, with no failures in a 512 MB cgroup. Warm latency 75-90 ms for a 0.9 MP photo, 230-290 ms for 12-24 MP.
- **Alternatives considered:** Keep PyTorch and pay for a larger host; laptop with a tunnel (kept as a demo fallback).
- **Not verified:** Parity on real waste photos (none available yet). Behaviour on a 0.1 vCPU free instance, where inference will be much slower. The Docker image build, because Docker Hub was unreachable from the sandbox; the Dockerfile is written but untested.
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
