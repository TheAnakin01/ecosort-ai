# EcoSort AI — Product and Engineering Specification

This folder is the product and engineering source of truth for building **EcoSort AI**, a mobile application that detects multiple waste objects in one image and helps users sort them into material categories.

## How to use this specification

1. Start with `PRODUCT_REQUIREMENTS.md`, `MVP_SCOPE.md` and `ARCHITECTURE.md`.
2. Read the relevant specialist document before implementing a phase.
3. Follow the phase order in `ROADMAP.md`.
4. Treat decisions marked **Proposed** as defaults that require validation, not as implemented facts.
5. Never claim model accuracy, dataset provenance, local recycling rules or deployment status without evidence.
6. Keep this documentation updated when an approved decision changes; record it in `../decision-log.md`.

## Document index

| File | Purpose |
|---|---|
| `PRODUCT_REQUIREMENTS.md` | Product vision, users, problems, functional and non-functional requirements |
| `MVP_SCOPE.md` | Exact MVP boundaries, priorities, acceptance criteria, exclusions |
| `ARCHITECTURE.md` | System architecture, components, data flow, deployment boundaries |
| `AI_MODEL.md` | Detection architecture, training, inference, evaluation, model lifecycle |
| `DATASET_AND_ANNOTATION.md` | Dataset sourcing, label taxonomy, annotation, splits, quality controls |
| `MOBILE_UI_UX.md` | Navigation, screens, interaction states, visual system, accessibility |
| `BACKEND_API.md` | FastAPI service design, endpoints, schemas, validation and errors |
| `DATABASE_DESIGN.md` | Supabase/Postgres proposal, entities, schema, privacy and migrations |
| `SECURITY_PRIVACY.md` | Threat model, image handling, secrets, data minimization |
| `TESTING_AND_ACCEPTANCE.md` | Test strategy, quality gates and end-to-end acceptance |
| `ROADMAP.md` | Phased implementation plan and definition of done |
| `DEPLOYMENT_AND_RELEASE.md` | Environments, hosting, Android builds and release checklist |
| `OPEN_QUESTIONS.md` | Decisions that require product-owner confirmation |

## Current agreed direction

- Product: **multiple waste classification/detection** — one photo can contain several separate waste objects.
- Initial material classes: `paper`, `plastic`, `metal`, `organic`.
- Main model direction: pretrained YOLO nano object detector, fine-tuned on reviewed bounding-box annotations.
- AI stack: Python, PyTorch, Ultralytics, OpenCV.
- Backend: FastAPI; inference initially runs on the backend.
- Mobile: React Native + Expo + TypeScript, Android-first.
- Database: Supabase/Postgres is optional for MVP; add only when history/accounts/cloud persistence are in scope.
- Do not claim universal recyclability. Disposal guidance must be cautious and location-aware only when verified.

## Important status note

This is a **build specification**, not evidence that a feature exists. For the current state of the project see `../PROJECT_STATUS.md`.
