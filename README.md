# EcoSort AI

EcoSort AI finds several waste items in one photo, labels each one as **paper, plastic, metal or organic**, draws a box around it and tells you which bin it goes in. Built for Srujan 2026.

## Try it

- **Android app:** download the APK from the [`apk-latest` release](https://github.com/TheAnakin01/ecosort-ai/releases/tag/apk-latest) and install it (allow installs from your browser when asked).
- **In a browser:** https://theanakin01.github.io/ecosort-ai/ (works on a phone too).
- The server runs on a free plan and sleeps when idle, so the **first scan can take up to a minute**. Opening https://ecosort-ai-srujan26.onrender.com/health first wakes it up.

## What it does

- Take a photo or pick one from the gallery.
- Every item found gets a box, a category and a confidence score; uncertain detections are marked.
- Counts per category and general sorting tips (dry and wet waste).
- History of past scans, kept only on the phone.
- No accounts, and the server does not store photos.

## How it works

```
Phone app  ──photo──▶  FastAPI backend  ──▶  YOLO11n detector (ONNX Runtime)
   ▲                                              │
   └──── items, boxes, confidence, counts, tips ◀─┘
```

| Part | Technology |
|---|---|
| Detector | Ultralytics YOLO11n (nano), fine-tuned by transfer learning on four public waste datasets, exported to ONNX |
| Backend | Python, FastAPI, ONNX Runtime; Docker, hosted on Render |
| App | React Native, Expo, TypeScript; Android APK and web build |
| Automation | GitHub Actions: tests, web deploy, APK build |

## Results

Measured on 7,501 validation photos the model did not train on (details in [docs/training-log.md](docs/training-log.md)):

| Precision | Recall | mAP@50 | mAP@50-95 |
|---|---|---|---|
| 0.776 | 0.622 | 0.711 | 0.550 |

About 4 in 5 boxes are correct, and it finds about 3 in 5 items. Limitations, such as no glass class and items missed in crowded piles, are listed in [docs/KNOWN_LIMITATIONS.md](docs/KNOWN_LIMITATIONS.md).

## Repository

```
ai-model/   dataset preparation, training, evaluation and export scripts; notebooks; the trained model
backend/    FastAPI server that runs the model
mobile/     React Native + Expo app
docs/       specification, project status, decisions, training log, dataset card
```

## Run it yourself

1. **Dataset and model:** [ai-model/README.md](ai-model/README.md) (training runs on Colab or Kaggle).
2. **Backend:** [backend/README.md](backend/README.md).
3. **App:** [mobile/README.md](mobile/README.md).

The trained model (`ai-model/weights/best.onnx`) is included; datasets are downloaded by the scripts.

## Documentation

- [Project status](docs/PROJECT_STATUS.md): what is done and what is open
- [Specification](docs/specification/README.md): requirements, architecture, API, UI
- [Decision log](docs/decision-log.md) and [dataset card](docs/dataset-card.md)
