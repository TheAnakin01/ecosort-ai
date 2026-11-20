# System Architecture

## 1. Proposed architecture

The MVP uses a mobile client, an HTTP inference API and a model service. Inference runs on the backend initially so the model can be updated without shipping a new mobile binary.

```text
┌──────────────────────────┐
│ React Native + Expo App  │
│                          │
│ Camera / Gallery         │
│ Preview                  │
│ API client               │
│ Results + box overlay    │
└────────────┬─────────────┘
             │ HTTPS multipart image upload
             ▼
┌──────────────────────────┐
│ FastAPI Backend          │
│                          │
│ Request validation       │
│ Image decoding           │
│ Inference service        │
│ Post-processing          │
│ Guidance rules           │
│ Response schemas         │
└────────────┬─────────────┘
             ▼
┌──────────────────────────┐
│ YOLO detector            │
│                          │
│ Pretrained baseline      │
│ Fine-tuned weights       │
│ Four mapped classes      │
└──────────────────────────┘

Optional later:
FastAPI ──► Supabase/Postgres (metadata/history only)
```

## 2. Technology choices

| Layer | Choice | Reason |
|---|---|---|
| Mobile | React Native + Expo + TypeScript | Cross-platform development and camera/gallery ecosystem |
| Navigation | Expo Router | File-based navigation |
| Camera | Expo Camera | Camera capture |
| Gallery | Expo ImagePicker | Image selection |
| Backend | Python + FastAPI + Uvicorn | Typed, testable inference API |
| Model | PyTorch + Ultralytics YOLO nano detector | Practical multi-object detection baseline |
| Image processing | OpenCV + Pillow as needed | Decode, orientation and preprocessing |
| Annotation | CVAT or Roboflow | Bounding-box annotation/review |
| Dataset | TACO plus carefully reviewed supplementary/custom data | Real-world litter context; requires taxonomy mapping |
| Database later | Supabase/Postgres | Managed relational persistence if needed |

## 3. Monorepo layout

```text
EcoSort-AI/
├── ai-model/
│   ├── configs/
│   ├── datasets/              # ignored by Git; document acquisition
│   ├── notebooks/
│   ├── scripts/
│   ├── training/
│   ├── evaluation/
│   ├── weights/               # large weights ignored or stored externally
│   └── README.md
├── backend/
│   ├── app/
│   │   ├── api/
│   │   ├── core/
│   │   ├── schemas/
│   │   ├── services/
│   │   └── main.py
│   ├── tests/
│   ├── requirements.txt
│   └── README.md
├── mobile/
│   ├── app/
│   ├── src/
│   │   ├── components/
│   │   ├── features/
│   │   ├── hooks/
│   │   ├── services/
│   │   ├── theme/
│   │   └── types/
│   ├── assets/
│   └── README.md
├── docs/                      # this documentation pack
├── .gitignore
├── LICENSE
└── README.md
```

Adapt to the existing repository rather than forcing this exact layout if a sound structure already exists.

## 4. End-to-end data flow

1. Mobile obtains a local image URI.
2. User confirms preview.
3. Mobile sends multipart form-data to `POST /api/v1/detect`.
4. Backend validates MIME type, decoded format, file size and dimensions.
5. Backend decodes image and applies EXIF orientation consistently.
6. Detector runs with configured confidence and IoU thresholds.
7. Post-processing maps model coordinates back to original oriented image dimensions.
8. Backend maps model class IDs to canonical category strings.
9. Backend calculates counts and attaches rules-based guidance metadata.
10. Backend returns JSON.
11. Mobile displays the original preview and maps original pixel coordinates to the rendered image content rectangle.
12. User can scan again.

## 5. Coordinate contract

The API must return bounding boxes in the coordinate system of the **oriented, decoded image** that the client displays.

- Image width/height refer to the oriented image dimensions.
- Box format: `[x1, y1, x2, y2]`.
- Origin is top-left.
- `x2 > x1` and `y2 > y1`.
- Coordinates are clipped to `[0, width]` and `[0, height]`.
- If the mobile view uses `contain`, calculate the displayed image content rectangle including letterbox offsets. Do not scale boxes against the full container blindly.
- If the image is cropped, rotated or otherwise transformed client-side, apply the corresponding transform to boxes or display an untransformed image.

## 6. Runtime boundaries

- Model weights are loaded once at backend startup.
- Mobile contains no model secret or service-role key.
- API URL is environment-configured.
- Local development and production environments must be distinct.
- The backend should be stateless for the scan-only MVP.

## 7. Scalability path

For early student-project usage, one FastAPI process and one model instance may be sufficient. Measure memory, throughput and latency before scaling. If traffic grows, consider a separate inference worker/service, request limits, queueing and autoscaling. Do not add distributed infrastructure prematurely.
