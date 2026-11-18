# EcoSort AI — release notes and known limitations

For the Srujan 2026 Round 1 submission. Last updated 2026-11-18.

## What it does

Take or pick a photo of waste. EcoSort AI finds each item in the photo, draws a box around it, labels it **paper, plastic, metal or organic**, shows how sure the model is, counts each category and gives general sorting tips.

## Versions

| Part | Version |
|---|---|
| Model | YOLO11n fine-tuned on four public datasets, "run 2" (2026-11-16). File `ai-model/weights/best.onnx`; size and SHA-256 in `best.onnx.json`. |
| Backend | FastAPI 0.2.0, ONNX Runtime, hosted on Render (free tier). |
| App | Expo SDK 58, React Native. Web version on GitHub Pages; Android APK built with EAS. |

## How well it works

Measured on 7,501 validation photos the model never trained on (details in `docs/training-log.md`):

| | Precision | Recall | mAP@50 | mAP@50-95 |
|---|---|---|---|---|
| Run 2 | 0.776 | 0.622 | 0.711 | 0.550 |

Precision 0.78 means about 4 in 5 boxes are right. Recall 0.62 means it finds about 3 in 5 items. These are validation numbers; the held-out test split has not been scored yet.

## Known limitations

- **Detections are AI estimates.** Check before you sort. Uncertain boxes are marked.
- **Only four classes.** Glass, e-waste, cloth and hazardous waste have no class. Glass bottles and jars are often missed or mislabelled.
- **It misses items.** About 2 in 5 items get no box, more often in crowded piles, small items and unusual angles.
- **Weakest on plastic.** Plastic has the most boxes on nothing (8.6%). Organic false detections rose in run 2 (7.6%).
- **Trained on dataset photos, not your street.** A quick test on three stock images (with run 1) found it struggled with staged flat-lays and infographics. Real phone photos of a few items on a plain surface work best.
- **Sorting tips are general.** "Dry waste" and "Wet waste" follow common Indian practice, but local rules vary; they are not official municipal guidance.
- **The free server sleeps.** After about 15 minutes idle, the first scan can take up to a minute while it wakes. Later scans are faster, but slower than on a laptop.
- **Upload limits.** JPEG, PNG or WebP up to 10 MB and 12 megapixels. Scans are limited to 60 per minute per network to protect the free server.
- **Confidence thresholds** (0.35 shown, below 0.5 marked uncertain) are first guesses; `ai-model/scripts/tune_thresholds.py` will set them from validation data.

## Privacy

- The server does **not** store photos. Each photo is analysed in memory and discarded.
- Scan history is kept **only on your device** (photos included) and can be deleted from the History screen.
- No accounts, no analytics, no tracking.

## Licences

- The detector is built with Ultralytics YOLO (AGPL-3.0).
- TrashNet is CC BY 4.0. The licences of Trash Detection, Neat Now and the GARBAGE CLASSIFICATION 3 copy are still to be confirmed (see `docs/dataset-card.md`).

## Demo script (2 minutes)

1. Open `https://<your-service>.onrender.com/health` a minute before, to wake the server.
2. Open the app (APK or https://theanakin01.github.io/ecosort-ai/). The home screen shows the server is reachable.
3. Scan a prepared photo with three or four items of different types on a plain table. Show the boxes, labels, confidence and counts.
4. Open one category's tips; point out the local-rules note.
5. Show History, then mention: no photos stored on the server.
6. Close with one honest limitation (only four classes; misses some items) and the next step (own photos and a third training run).
