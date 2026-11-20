# MVP Scope and Acceptance Boundaries

## 1. MVP objective

Deliver one reliable end-to-end workflow: capture/select a photo with multiple waste items, run real object detection, and show object-level results in the mobile app.

## 2. Must-have (P0)

- Expo + React Native + TypeScript app launches on Android.
- Camera capture and gallery selection.
- Image preview, replace and confirm.
- FastAPI backend health endpoint.
- Real YOLO-based inference endpoint (not hard-coded mock data).
- Four initial material classes: paper, plastic, metal, organic.
- Multiple bounding-box detections per image.
- Confidence score and original-image pixel coordinates for every detection.
- Category counts and total object count.
- Correct overlay alignment on the displayed image.
- Loading, empty, low-confidence, invalid-image, timeout and server-error states.
- Basic rules-based category guidance with a local-rules disclaimer.
- Tests for core API and coordinate transformation logic.
- README with setup and run instructions.

## 3. Should-have (P1, only after P0 works)

- Scan history stored locally on device.
- Improved guidance content and educational category pages.
- Feedback control for incorrect detection (do not silently retrain from feedback).
- Model/version details in a debug or about screen.
- Basic accessibility and localization foundation.

## 4. Could-have (P2)

- Supabase account system and cloud history.
- User profile and preferences.
- Usage statistics.
- Multiple language support.
- Verified location-specific waste guidance.
- Offline/on-device model inference.
- Video/live camera detection.

## 5. Explicitly out of MVP

- Payments, subscriptions or ads.
- Social network/community feed.
- Rewards, points, leaderboards.
- Admin dashboard unless required for dataset review.
- Hazardous-waste safety advice.
- Exact polymer/resin identification.
- Guaranteed recyclability decision.
- Automatic municipal pickup scheduling.

## 6. MVP acceptance criteria

### Image flow
- User can choose an image from gallery and capture a photo.
- User can preview, cancel and replace an image.
- Unsupported or oversized files receive a clear message.

### Inference
- Backend loads model once at process startup.
- Valid image produces a valid response with image dimensions and a detections array.
- A scene containing several supported objects can return several detections.
- No detections returns an empty array and zero counts, not a fake result.
- Each box uses `[x1, y1, x2, y2]` in original image pixel coordinates.
- Coordinates are bounded by image dimensions and have positive width/height.
- Confidence is a numeric value from 0 to 1.

### UI
- Boxes align with objects after image scaling and letterboxing.
- Labels remain readable and do not obscure the whole image.
- Counts match the detections array.
- Low-confidence results are visibly qualified.
- Empty/error states are understandable and offer a retry or new scan.

### Quality
- Automated tests pass.
- Android physical-device test is completed.
- No secrets are committed.
- Documentation accurately describes actual setup and limitations.

## 7. Demo checklist

1. Launch app.
2. Select a prepared mixed-waste photo.
3. Preview it.
4. Run scan.
5. Show multiple boxes and labels.
6. Show category counts.
7. Show sorting guidance and caveat.
8. Demonstrate a no-detection or API error state.
9. Explain model metrics using actual evaluation results only.
