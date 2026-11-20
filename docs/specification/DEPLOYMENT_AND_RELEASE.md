# Deployment and Release Plan

## 1. Environments

Maintain separate:
- Local development.
- Staging/test.
- Production.

Use distinct API URLs and credentials. Never point a development build at production data by accident.

## 2. Backend deployment

Choose a host that supports the model runtime, memory requirements, request duration and (if needed) GPU access. Do not select a provider solely because it is free. Measure model startup time, inference latency, memory and concurrency.

Deployment requirements:
- HTTPS.
- Environment-based configuration.
- Health/readiness endpoint.
- Model artifact available at startup.
- Upload size and request timeout limits.
- Safe logging and error handling.
- Restart policy and basic monitoring.
- Documented model version.

Do not assume a serverless platform can run the chosen model efficiently without testing cold starts and runtime limits.

## 3. Mobile configuration

- Configure API base URL per build environment.
- Do not hard-code local `localhost` for a physical device or production build.
- Keep app permissions minimal.
- Use Expo-compatible packages.
- Test Android camera/gallery permission behavior.
- Use EAS Build when a distributable Android build is needed.

## 4. Android release steps

1. Confirm MVP acceptance checklist.
2. Confirm production API is deployed and HTTPS works.
3. Configure app identifier, version and icons.
4. Configure EAS build profiles.
5. Build Android preview/release artifact.
6. Install on a physical device.
7. Test camera, gallery, scan, result overlay and error states.
8. Record build version and backend model version.
9. Prepare release notes and known limitations.

## 5. Release notes must state

- Supported material classes.
- That detections are AI estimates.
- That local waste and recycling rules vary.
- Whether images are stored (default: no).
- Known limitations and supported image formats.
- App/backend/model versions.

## 6. Rollback

Keep the previous known-good backend model artifact and deployment configuration. If a new model causes severe regression, revert the model version. Keep API response compatibility across mobile/backend versions where possible.
