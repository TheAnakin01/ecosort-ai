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
