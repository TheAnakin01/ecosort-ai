# Product Requirements Document (PRD)

## 1. Product summary

**Name:** EcoSort AI  
**Product type:** AI-assisted waste identification and sorting mobile app  
**Initial platform:** Android, built with React Native + Expo  
**Primary capability:** Detect several waste objects in one image and classify each into a broad material category.

EcoSort AI helps a user understand what material types appear in a waste photo. It is an assistive recognition tool, not a certified waste audit, municipal authority, or guarantee that an object is recyclable.

## 2. Problem statement

People often dispose of mixed waste without knowing which material groups are present. A single photo may contain multiple objects, making a one-label image classifier inadequate. Users need object-level detection, clear category counts and practical, cautious sorting guidance.

## 3. Product vision

Make waste sorting easier by turning a photo of mixed waste into a transparent list of detected objects and likely material categories.

## 4. Target users

- Household users sorting everyday waste.
- Students and educators demonstrating waste segregation.
- Environment-focused communities and volunteers.
- Users who need a quick first-pass indication of material categories.

The MVP is not designed for industrial waste facilities, hazardous waste identification, legal compliance, or precise material-composition analysis.

## 5. Core user journey

1. User opens the app.
2. User chooses camera or gallery.
3. User captures/selects a photo containing one or more waste objects.
4. User previews and confirms the image.
5. App uploads it to the inference API.
6. API detects objects and returns categories, confidence scores and bounding boxes.
7. App overlays boxes and labels on the image.
8. App shows total objects and counts per category.
9. App presents simple sorting guidance with uncertainty/local-rule caveats.
10. User can scan another image.

## 6. Product goals

- Correctly support more than one detection per image.
- Make results understandable at a glance.
- Preserve alignment between detection boxes and the displayed photo.
- Communicate uncertainty honestly.
- Work reliably on a physical Android device.
- Keep the first release small enough to test with real users.

## 7. Non-goals

- Identifying every object or every waste subtype.
- Detecting hazardous chemicals, batteries, medical waste or e-waste as safe categories.
- Determining whether an item is clean, contaminated or accepted by a specific recycling facility.
- Guaranteeing recyclability from appearance.
- Real-time video detection.
- Offline inference in the first MVP.
- Social feed, gamification, leaderboards or marketplace.
- User accounts, cloud history or analytics in the first scan-only MVP unless separately approved.

## 8. Functional requirements

### FR-01 Image input
The user can capture an image or choose one from the device gallery.

### FR-02 Image preview
The user can inspect the selected image and retake/replace it before scanning.

### FR-03 Multi-object detection
The system detects zero, one or multiple objects in a single image.

### FR-04 Material categories
Each supported detection is mapped to one of:
- `paper`
- `plastic`
- `metal`
- `organic`

### FR-05 Detection metadata
Each detection includes a unique response-local ID, class/category, confidence score and bounding box in original-image pixel coordinates.

### FR-06 Results visualization
The app overlays bounding boxes and labels on the correct image locations.

### FR-07 Category summary
The app displays total detections and count per category, including zero counts where useful.

### FR-08 Uncertainty
Low-confidence or unsupported cases must not be presented as certain. The app must be able to show an inconclusive/no-detection state.

### FR-09 Sorting guidance
The app provides short rules-based guidance for the broad category and states that local collection rules vary.

### FR-10 Error handling
The app handles invalid image, upload failure, timeout, server error, no detections and unavailable model states.

### FR-11 Accessibility
Controls have accessible labels; text and controls are readable and usable on common phone sizes.

## 9. Non-functional requirements

- **Reliability:** no crash for ordinary valid images or expected API errors.
- **Performance:** measure end-to-end scan latency; do not promise a target until tested on representative devices and hosting.
- **Security:** validate uploads, restrict file size/type, keep secrets server-side.
- **Privacy:** do not persist raw images by default.
- **Maintainability:** typed API contracts, modular code, automated tests and documented setup.
- **Compatibility:** Android-first; keep implementation compatible with Expo-supported iOS paths where practical.
- **Observability:** log request IDs, durations and safe error metadata without storing image contents.

## 10. Success measures

MVP success should be assessed through:
- Successful end-to-end scan rate.
- Detection precision/recall and mAP on a held-out test set.
- Per-class performance and confusion/error analysis.
- Bounding-box overlay alignment.
- Median and percentile inference/round-trip latency on documented conditions.
- User ability to understand the results in a short usability test.

Do not define success as an arbitrary “99% accuracy” target. Set numeric targets only after baseline measurement and product-owner review.

## 11. Risks and limitations

- Material categories can be visually ambiguous.
- Composite products may contain multiple materials.
- Transparent, dirty, crushed or occluded objects may be difficult.
- Public datasets may be imbalanced or not representative of local waste.
- Broad material labels do not determine local recyclability.
- Network/backend availability affects scans in the initial architecture.
