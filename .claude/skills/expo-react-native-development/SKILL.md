---
name: expo-react-native-development
description: Build EcoSort AI's React Native and Expo mobile application using TypeScript, camera/gallery workflows, API integration, navigation, and maintainable app structure.
---

# Expo React Native Development

## Product experience

The MVP flow should support:
1. Launch and clear explanation of the app
2. Capture an image or select one from the gallery
3. Preview and confirm the image
4. Submit it for detection
5. Show loading, success, empty-result, and error states
6. Display multiple detections, bounding boxes, labels, confidence, and counts
7. Allow the user to scan another image

Do not add accounts, social features, scan history, or complex gamification unless approved.

## Engineering standards

- Use TypeScript with strict types where practical.
- Keep screens, reusable components, API clients, hooks, and domain types separated.
- Use environment configuration for API base URLs; never hard-code private endpoints or secrets.
- Validate permissions and handle denial/revocation gracefully.
- Handle network timeouts, offline state, oversized images, unsupported formats, and server errors.
- Avoid blocking the UI during image processing or upload.
- Provide accessible labels, readable contrast, touch targets, and responsive layouts.
- Avoid unnecessary dependencies; explain why each native dependency is needed.

## Expo constraints

Before using a native ML/runtime package, check whether it works in Expo Go or requires a development build/prebuild and native configuration. Do not promise on-device inference without validating the package and build workflow.

## API integration

Use a typed API client and a shared response schema. Normalize server errors into user-friendly states without hiding diagnostic details from development logs. Do not fabricate detections when the API is unavailable.

## Image handling

Respect orientation metadata, image dimensions, upload limits, and supported MIME types. Avoid retaining image copies longer than needed. Make the displayed result correspond to the exact submitted image.

## Required checks

Run available lint, typecheck, unit tests, and platform builds. If a physical-device test is unavailable, say so. Include exact commands and results.
