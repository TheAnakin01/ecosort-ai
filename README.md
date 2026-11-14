# EcoSort AI

An app that finds several waste items in one photo, labels each one as paper, plastic, metal or organic, and tells you which bin it goes in. Built for Srujan 2026.

The approved specification is the documentation pack in [docs/EcoSort-AI-Agent-Harness/](docs/EcoSort-AI-Agent-Harness/README.md). The earlier blueprint is [Smart waste ai.md](Smart%20waste%20ai.md).

Working on this repo with Claude: [CLAUDE.md](CLAUDE.md) holds the project instructions, and `.claude/skills/` holds ten task-specific skills that Claude loads automatically.

## Open it

- **App in a browser:** https://theanakin01.github.io/ecosort-ai/ (works on a phone; scanning stays off until a backend is hosted and its address is set, see [mobile/README.md](mobile/README.md))
- **Train the model:** [open the notebook in Colab](https://colab.research.google.com/github/TheAnakin01/ecosort-ai/blob/main/ai-model/notebooks/train_ecosort.ipynb)

## Status

| Part | State |
|---|---|
| Backend API (`backend/`) | Matches the API specification. Tested with a stand-in detector, and against a real YOLO model trained on synthetic shapes. Not yet run with a waste model. |
| Dataset and training scripts (`ai-model/`) | All scripts run end to end on a synthetic dataset. No real dataset has been merged and checked, and no waste model has been trained. |
| Mobile app (`mobile/`) | All five screens work in the web version, including real inference through the backend with the synthetic-shapes model. Not yet run as an app on an Android phone. |

## How the parts fit

1. The phone app sends a photo to the backend.
2. The backend runs the trained YOLO model on it.
3. The backend replies with every item found: category, confidence and box position, plus counts per category.
4. The app draws the boxes and shows the sorting tips.

## Folders

```
ai-model/   dataset merge, training and prediction scripts, Colab notebook
backend/    FastAPI server that serves the model
mobile/     React Native + Expo phone app
docs/       training log
```

## Start here

1. **Dataset and model:** follow [ai-model/README.md](ai-model/README.md).
2. **Backend:** follow [backend/README.md](backend/README.md).
3. **Mobile app:** follow [mobile/README.md](mobile/README.md).

Datasets and model weights are not stored in this repo. They are too large for GitHub.

Approved project decisions are recorded in [docs/decision-log.md](docs/decision-log.md).
