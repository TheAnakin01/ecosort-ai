---
name: mobile-ui-ux-design
description: Design EcoSort AI's mobile experience, visual system, interaction states, accessibility, and waste-sorting result presentation.
---

# Mobile UI/UX Design

## Product principles

The app should feel clear, trustworthy, fast, and approachable. The primary job is to help users understand what waste items were detected and how to sort them. Avoid visual clutter and unsupported environmental claims.

## Core screens

- Welcome/onboarding (minimal)
- Scan home with camera and gallery actions
- Image preview/confirmation
- Scanning/loading state
- Results with annotated image, per-class counts, and detection list
- Error/empty-result states

## Result hierarchy

1. Annotated image with clear bounding boxes
2. Total detected objects
3. Counts by canonical class
4. Per-object labels and confidence where useful
5. Cautious sorting guidance

Do not imply that the model can determine local recycling rules unless the app has a verified location-specific rules source. Material classification is not the same as determining recyclability.

## Visual and interaction standards

- Establish typography, spacing, color, icon, and component tokens.
- Ensure class identity is not communicated by color alone.
- Maintain readable contrast and large touch targets.
- Design loading, permission-denied, no-detection, network-error, and retry states.
- Respect safe areas, keyboard behavior, and small-screen layouts.
- Avoid excessive animations that delay scanning or obscure results.
- Use realistic content and real model/API states; label mockups as mockups.

## Validation

Review screens at multiple screen sizes and accessibility settings. Test with long labels, many detections, zero detections, overlapping labels, and slow network conditions. Obtain product-owner approval before introducing major navigation or scope changes.
