# Testing Strategy and Acceptance Tests

## 1. Testing layers

### AI/data tests
- Annotation parser tests.
- Label-map validation.
- Bounding-box validity tests.
- Dataset split leakage checks.
- Reproducibility/config validation.
- Model evaluation on held-out test set.

### Backend unit tests
- Image validation.
- EXIF orientation behavior.
- Class mapping.
- Bounding-box clipping and coordinate conversion.
- Category counts.
- Error mapping.
- Model service initialization/injection.

### Backend API tests
- Health endpoint.
- Valid image upload.
- Multiple detections.
- Zero detections.
- Invalid/corrupt image.
- Unsupported file type.
- Oversized image.
- Model unavailable.
- Timeout/error response shape.

### Mobile tests
- Navigation.
- Camera permission states.
- Gallery selection.
- Preview/replace.
- API request and response parsing.
- Result counts.
- Overlay coordinate transformation.
- Loading/error/empty states.

### End-to-end tests
- Real Android device captures/selects an image.
- Image reaches deployed/local API.
- Real detector returns output.
- UI displays aligned boxes and correct counts.
- Retry works after a network/server error.

## 2. Critical coordinate test cases

Test:
- Landscape image in portrait phone view.
- Portrait image in landscape container.
- Square image.
- Image with EXIF rotation.
- `contain` letterboxing.
- Cropped `cover` mode if used.
- Boxes touching each image boundary.
- Very small boxes.

Use synthetic test images with known boxes to verify transforms independently from model quality.

## 3. AI evaluation protocol

- Evaluate only on held-out test data after all tuning.
- Report per-class precision, recall and AP.
- Include mAP@50 and mAP@50–95.
- Inspect false positives, false negatives, duplicates and localization errors.
- Record confidence threshold and image size.
- Record model, dataset and code version.
- State hardware and inference timing method.
- Do not report training metrics as test performance.

## 4. Acceptance checklist

### Product
- [ ] Multi-object scan works.
- [ ] Four canonical classes are used consistently.
- [ ] No fake detections in production.
- [ ] Guidance includes local-rule caveat.

### Backend
- [ ] Model loads once.
- [ ] Upload validation works.
- [ ] Response schema is stable.
- [ ] Counts equal detection totals.
- [ ] Boxes are valid and in original-image coordinates.
- [ ] Errors are safe and actionable.

### Mobile
- [ ] Camera and gallery work.
- [ ] Preview and retake work.
- [ ] Overlay alignment is verified.
- [ ] Loading, empty, uncertainty and error states work.
- [ ] Physical Android test passes.

### Security
- [ ] No committed secrets.
- [ ] Upload limits enabled.
- [ ] Images are not retained by default.
- [ ] Production uses HTTPS.

### Documentation
- [ ] Setup steps tested.
- [ ] Actual metrics documented.
- [ ] Known limitations documented.
- [ ] Screenshots/demo reflect actual implementation.

## 5. Bug severity guide

- **Blocker:** app cannot launch/scan, data exposure, fake result presented as real, severe coordinate mismatch.
- **High:** core flow fails for common images, wrong counts, crashes, API unusable.
- **Medium:** edge-case errors, confusing recovery, accessibility issue.
- **Low:** cosmetic spacing, minor visual inconsistency.

Fix blockers/high severity before adding optional features.
