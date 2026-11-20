# Mobile UI/UX Specification

## 1. UX principles

- The primary action — scan waste — should be obvious on the home screen.
- Keep the scan journey short and forgiving.
- Results should explain what the model saw, not imply certainty beyond the evidence.
- Prioritize image clarity and accurate box overlays over decorative animations.
- Make error, loading, empty and low-confidence states first-class screens/states.
- Use accessible contrast, readable type and comfortable touch targets.

## 2. Navigation

Proposed bottom navigation:
- **Home** — primary scan entry and short explanation.
- **Learn** — four material categories and limitations.
- **History** — optional; hide until local or cloud history is implemented.

Do not show a non-functional tab. The MVP can use a simpler stack with Home, Scan and Results if history/learn are not ready.

## 3. Screen specifications

### Home
Purpose: explain value and start scanning.
Components:
- EcoSort AI title/brand.
- Short description: “Scan a photo to identify visible waste materials.”
- Primary button: “Scan waste”.
- Secondary action: “Choose from gallery”.
- Brief caveat: “Results are AI estimates. Local sorting rules vary.”
States:
- Normal.
- Camera permission denied.
- API unavailable (do not block selecting an image if only API is unavailable).

### Scan / camera
Purpose: capture a useful image.
Components:
- Camera preview.
- Capture button.
- Gallery alternative.
- Permission explanation and settings recovery.
Guidance:
- Encourage good lighting and visible separation between objects.
- Do not require a perfect background.
States:
- Permission loading/granted/denied.
- Camera unavailable.
- Capture in progress.

### Image preview
Purpose: let user confirm before upload.
Components:
- Selected image.
- Retake/choose another.
- “Analyze image” primary action.
- Cancel/back.
States:
- Image loading.
- Unsupported file.
- File too large.
- Image decode failure.

### Results
Purpose: show model output transparently.
Components:
- Original image with detection overlays.
- Category-colored but accessible labels.
- Confidence percentage or qualitative confidence, clearly named “model confidence” (not accuracy).
- Total object count.
- Counts by category.
- Short sorting guidance.
- “Scan another” action.
States:
- Loading with progress copy that does not imply fake model stages.
- Results with detections.
- No detections.
- Low-confidence/uncertain result.
- API/network/server error with retry.
- Partial or unsupported detections only if API contract explicitly supports them.

### Learn
Purpose: explain broad categories and limitations.
- Paper: examples and clean/dry separation reminder.
- Plastic: examples; local acceptance varies by type and contamination.
- Metal: examples; sharp/hazardous items require separate safe handling guidance.
- Organic: food scraps/green waste examples.
- Explain composite/ambiguous items and model limitations.

### History (later)
Do not implement until persistence behavior is agreed. If local-only, make that clear. If cloud-backed, include account, consent, deletion and retention behavior.

## 4. Results layout

Suggested hierarchy:
1. Image/result canvas.
2. “N objects detected” summary.
3. Category count chips/cards.
4. Detection list (tap/highlight corresponding box if implemented).
5. Sorting guidance and disclaimer.
6. Scan another button.

Avoid overwhelming the user with long technical explanations. Provide confidence details without implying certainty.

## 5. Overlay coordinate math

The API returns coordinates in original oriented image pixels. If the image is displayed using `contain` in a view of width `viewW` and height `viewH`:

- `scale = min(viewW / imageW, viewH / imageH)`
- `renderW = imageW * scale`
- `renderH = imageH * scale`
- `offsetX = (viewW - renderW) / 2`
- `offsetY = (viewH - renderH) / 2`
- `left = offsetX + x1 * scale`
- `top = offsetY + y1 * scale`
- `width = (x2 - x1) * scale`
- `height = (y2 - y1) * scale`

Apply the same transform to labels and boxes. Account for safe areas and actual image container dimensions. If using `cover`, cropping offsets must also be included. Test with known synthetic boxes and images of portrait, landscape and square aspect ratios.

## 6. Visual direction

Proposed direction: clean, modern, nature-inspired utility app; not a cluttered “green dashboard”.

Suggested tokens (initial proposal; validate in implementation):
- Primary: deep forest green.
- Accent: fresh leaf green.
- Background: warm off-white/light neutral.
- Surface: white or dark neutral depending on theme.
- Text: high-contrast charcoal.
- Semantic colors: category labels must remain distinguishable without relying only on color.

Use consistent spacing, corner radii, typography and icon style. Avoid excessive gradients, glassmorphism and animations that reduce readability.

## 7. Accessibility

- Minimum comfortable touch targets (aim around 44–48 dp).
- Text contrast meeting WCAG AA where feasible.
- Accessible labels for camera, gallery, retry and navigation controls.
- Do not encode categories only by color; include text/icon.
- Support system font scaling without clipping.
- Respect safe areas and screen reader focus order.
- Announce scan completion and errors accessibly.

## 8. UX copy examples

- Primary action: “Scan waste”
- Gallery action: “Choose a photo”
- Submit: “Analyze image”
- Loading: “Analyzing your photo…”
- Empty: “No supported waste items were detected. Try a clearer photo with objects fully visible.”
- Error: “We couldn't analyze this photo. Check your connection and try again.”
- Uncertainty: “Some items may be difficult to identify. Treat these results as estimates.”
- Disclaimer: “Sorting and recycling rules vary by location. Check your local waste guidelines.”

## 9. UX anti-patterns

- Do not label confidence as “accuracy”.
- Do not show hard-coded demo detections as real model output.
- Do not imply a category guarantees recyclability.
- Do not hide retry/back actions.
- Do not crop the image in a way that invalidates detection boxes.
- Do not show history/account controls that do nothing.
