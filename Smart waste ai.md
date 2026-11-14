---

# EcoSort AI — Master Project Blueprint

> [!abstract] Project Vision  
> EcoSort AI is an AI-powered waste detection and segregation assistant that identifies multiple waste objects in a single photograph, classifies them by material, displays their locations using bounding boxes, and provides appropriate disposal guidance.

## 1. Project Overview

### Problem Statement

People often struggle to identify the correct waste category for disposal. When several types of waste are mixed together, manually identifying and separating them becomes inconvenient.

Traditional image classification systems generally classify an entire image into one category. This is insufficient when a photograph contains several different waste objects.

### Our Solution

Build a mobile application that uses computer vision to detect multiple waste objects independently within a single image.

The application will:

1. Capture an image or select one from the gallery.
    
2. Detect individual waste objects.
    
3. Draw bounding boxes around detected objects.
    
4. Classify each object into a material category.
    
5. Display confidence scores.
    
6. Calculate category-wise object counts.
    
7. Provide sorting and disposal guidance.
    
8. Optionally maintain scan history and statistics.
    

### Core Differentiator

**Multi-object waste detection rather than single-image classification.**

---

## 2. Project Scope

### 2.1 Initial Classification Categories

|Category|Example Objects|
|---|---|
|Paper|Newspaper, cardboard, paper sheets, paper packaging|
|Plastic|Bottles, containers, wrappers, plastic packaging|
|Metal|Aluminium cans, tins, metal containers, foil|
|Organic|Fruit peels, vegetable scraps, food waste, leaves|

The first model will contain four material classes.

Object-level names can be added later if the dataset supports them reliably.

### 2.2 Minimum Viable Product (MVP)

- Camera image capture
    
- Gallery image selection
    
- Image preview and retake
    
- Multiple object detection
    
- Four-category classification
    
- Bounding-box visualization
    
- Confidence scores
    
- Category-wise counts
    
- No-detection handling
    
- Low-confidence handling
    
- Basic disposal guidance
    
- Android application build
    

### 2.3 Advanced Features — Future Scope

- Scan history
    
- User accounts
    
- Waste segregation statistics
    
- User feedback on incorrect detections
    
- Improved detection of overlapping objects
    
- Offline AI inference
    
- Multilingual interface
    
- Location-specific municipal disposal guidance
    
- Educational waste segregation content
    

**Development principle:** Complete and evaluate the MVP before introducing advanced features.

---

# 3. Technology Stack

## 3.1 AI and Machine Learning

|Technology|Purpose|
|---|---|
|Python|Main ML programming language|
|PyTorch|Deep learning framework|
|Ultralytics YOLO|Object detection|
|OpenCV|Image processing|
|NumPy|Numerical operations|
|Roboflow / CVAT|Dataset annotation|
|Matplotlib|Training visualization and evaluation|

## 3.2 Backend

|Technology|Purpose|
|---|---|
|Python|Backend language|
|FastAPI|REST API|
|Uvicorn|ASGI server|
|Pydantic|Data validation|
|OpenCV|Image processing|
|PyTorch / Ultralytics|Model inference|

## 3.3 Mobile Application

|Technology|Purpose|
|---|---|
|React Native|Mobile application framework|
|Expo|Development and native tooling|
|TypeScript|Programming language|
|Expo Router|Navigation|
|Expo Camera|Camera access|
|Expo ImagePicker|Gallery selection|
|NativeWind|Styling|
|Fetch / Axios|API communication|
|EAS Build|Android and iOS builds|

## 3.4 Database and Infrastructure

|Technology|Purpose|
|---|---|
|Supabase|Optional authentication and scan history|
|PostgreSQL|Relational database|
|Git and GitHub|Version control|
|EAS Build|Mobile application packaging|
|Cloud hosting|Backend deployment|

### Final Technology Decision

- AI: YOLO + PyTorch
    
- Backend: FastAPI
    
- Mobile: React Native + Expo
    
- Database: Supabase, introduced after the MVP works
    

Flutter is a valid alternative, but React Native + Expo is our selected mobile framework.

---

# 4. AI Architecture

## 4.1 Why Object Detection Instead of Image Classification?

A conventional classifier predicts one label for an entire image.

For example:

Image containing:

- Plastic bottle
    
- Cardboard box
    
- Metal can
    
- Banana peel
    

A conventional classifier may return just one dominant category.

Our application needs to detect all four objects independently.

Therefore, we need **object detection**.

Object detection provides:

- Object location
    
- Object category
    
- Confidence score
    
- Bounding-box coordinates
    

## 4.2 Model Selection

### Primary Model: YOLO Nano Detector

Start with a pretrained Ultralytics YOLO nano detection model, using a supported version available when development begins.

Why YOLO nano?

- Lightweight starting point.
    
- Fast inference relative to larger models.
    
- Suitable for transfer learning.
    
- Good development baseline.
    
- Potential for later edge/mobile optimization.
    

We will compare a larger model only if the nano model cannot meet our detection requirements.

### Model Architecture

The detector uses a convolutional neural network-based architecture with:

1. Backbone — extracts image features.
    
2. Neck — combines features at different scales.
    
3. Detection head — predicts object classes, bounding boxes and confidence.
    

We are not initially building a custom CNN or a CNN-transformer hybrid.

### Transfer Learning Strategy

1. Obtain pretrained YOLO weights.
    
2. Load the pretrained detector.
    
3. Configure the detection head for four categories.
    
4. Fine-tune on our waste detection dataset.
    
5. Validate during training.
    
6. Save the best-performing checkpoint.
    
7. Evaluate using an independent test dataset.
    
8. Export the trained model for inference.
    

MobileNetV2 may be considered later as a single-object classification baseline, but it is not our primary architecture.

## 4.3 Detection Classes

Dataset configuration:

```
names:
  0: paper
  1: plastic
  2: metal
  3: organic
```

The actual training configuration will also define dataset paths and other required settings.

## 4.4 AI Inference Pipeline

```
Input Image
    |
    v
Image Decoding
    |
    v
Preprocessing
    |
    v
Trained YOLO Detector
    |
    v
Object Detection
    |
    v
Confidence Filtering
    |
    v
Non-Maximum Suppression
    |
    v
Bounding Box Coordinate Mapping
    |
    v
Category-wise Counting
    |
    v
Sorting Guidance
    |
    v
Structured API Response
```

### Important Technical Details

- Confidence threshold must be tuned using validation data.
    
- Non-Maximum Suppression (NMS) helps remove duplicate predictions.
    
- Bounding boxes must be mapped back to original image dimensions.
    
- Image resizing and letterboxing must be handled correctly.
    
- The model must be able to return zero detections without failing.
    
- Low-confidence predictions should not be presented as certain identifications.
    

## 4.5 Illustrative Model Output

Input image: five different waste objects.

Expected output:

|Category|Detected count|
|---|---|
|Plastic|2|
|Paper|1|
|Metal|1|
|Organic|1|
|**Total**|**5**|

These numbers are examples, not measured model results.

---

# 5. Dataset Strategy

## 5.1 Dataset Requirements

We need an object detection dataset containing:

- Images of waste objects.
    
- Bounding-box annotations.
    
- Class labels.
    
- Real-world backgrounds.
    
- Multiple objects in some images.
    

A folder containing images classified into four categories is not sufficient for training the selected object detector.

## 5.2 Potential Data Sources

### TACO — Trash Annotations in Context

Purpose:

- Real-world litter images.
    
- Object-level annotations.
    
- Useful for detecting waste in natural environments.
    

Website:  
[https://tacodataset.org/](https://tacodataset.org/)

GitHub:  
[https://github.com/pedropro/TACO](https://github.com/pedropro/TACO)

Important: TACO's original labels do not directly correspond to our four categories. We must inspect and validate the mapping.

### Roboflow Universe

Purpose:

- Discover additional waste detection datasets.
    
- Review annotations.
    
- Prepare and export compatible datasets.
    

[https://universe.roboflow.com/](https://universe.roboflow.com/)

### CVAT

Purpose:

- Manually annotate bounding boxes.
    
- Review incorrect annotations.
    
- Create additional training examples.
    

[https://www.cvat.ai/](https://www.cvat.ai/)

### Custom Dataset

Collect photographs of:

- Plastic bottles.
    
- Plastic containers.
    
- Wrappers.
    
- Cardboard.
    
- Newspapers.
    
- Paper packaging.
    
- Metal cans.
    
- Tins.
    
- Fruit peels.
    
- Vegetable waste.
    

Prioritize realistic photographs rather than only clean product images.

## 5.3 Dataset Preparation Pipeline

1. Download potential datasets.
    
2. Inspect annotation formats.
    
3. Inspect image quality.
    
4. Map source labels into four material classes.
    
5. Remove irrelevant or corrupt images.
    
6. Review ambiguous labels.
    
7. Annotate additional images.
    
8. Remove duplicate and near-duplicate images.
    
9. Split into training, validation and testing sets.
    
10. Inspect class distribution.
    

### Initial Dataset Split

|Split|Approximate proportion|
|---|---|
|Training|70%|
|Validation|20%|
|Testing|10%|

Adjust these proportions according to dataset size and source grouping.

Avoid placing near-identical images from the same scene or capture session in different splits.

## 5.4 Important Dataset Challenges

- Transparent plastic.
    
- Crushed bottles.
    
- Dirty or wet waste.
    
- Partially hidden objects.
    
- Overlapping objects.
    
- Small objects.
    
- Mixed-material packaging.
    
- Different camera angles.
    
- Low lighting.
    
- Complex backgrounds.
    

We should specifically test these cases instead of relying on clean images alone.

---

# 6. Model Training and Evaluation

## 6.1 Training Workflow

```
Dataset Collection
       |
       v
Annotation Review
       |
       v
Label Mapping
       |
       v
Dataset Cleaning
       |
       v
Train / Validation / Test Split
       |
       v
Load Pretrained YOLO
       |
       v
Fine-tuning
       |
       v
Validation
       |
       v
Best Model Checkpoint
       |
       v
Independent Test Evaluation
       |
       v
Model Export
```

## 6.2 Training Experiments

Start with a baseline and conduct controlled experiments.

Potential variables:

- Image resolution.
    
- Batch size.
    
- Learning rate.
    
- Number of epochs.
    
- Data augmentation.
    
- Model size.
    
- Confidence threshold.
    

Do not change many variables simultaneously without recording the experiment.

Keep a training log with:

- Model version.
    
- Dataset version.
    
- Configuration.
    
- Training duration.
    
- Validation metrics.
    
- Test metrics.
    
- Known weaknesses.
    

## 6.3 Evaluation Metrics

|Metric|Meaning|
|---|---|
|Precision|Proportion of predicted detections that are correct|
|Recall|Proportion of actual objects detected|
|mAP@50|Mean average precision at IoU 0.50|
|mAP@50–95|Average performance across IoU thresholds|
|Per-class precision and recall|Category-specific performance|
|Inference time|Time taken to process an image|

### Evaluation Priorities

- Does the model detect all objects?
    
- Does it confuse paper and cardboard?
    
- Does it confuse plastic and transparent packaging?
    
- Does it detect small objects?
    
- Does it handle overlapping objects?
    
- Does it produce false detections?
    
- Does it work on photographs not used during training?
    

Never claim an accuracy figure without actual evaluation results.

---

# 7. Backend Architecture — FastAPI

## 7.1 Backend Responsibilities

The backend connects the mobile application with the trained model.

Responsibilities:

1. Receive image uploads.
    
2. Validate image type and dimensions.
    
3. Decode and preprocess images.
    
4. Run YOLO inference.
    
5. Apply post-processing.
    
6. Map bounding boxes to original dimensions.
    
7. Calculate category counts.
    
8. Attach sorting guidance.
    
9. Return structured JSON.
    
10. Handle errors safely.
    

## 7.2 API Endpoints

|Endpoint|Method|Purpose|
|---|---|---|
|`/health`|GET|Backend health|
|`/api/v1/detect`|POST|Multi-object detection|
|`/api/v1/categories`|GET|Supported material categories|
|`/api/v1/guidance/{category}`|GET|Sorting information|
|`/api/v1/model-info`|GET|Model version and configuration|

## 7.3 Detection API Response

Illustrative response:

```
{
  "success": true,
  "image_width": 1280,
  "image_height": 960,
  "total_objects": 5,
  "counts": {
    "paper": 1,
    "plastic": 2,
    "metal": 1,
    "organic": 1
  },
  "detections": [
    {
      "id": 1,
      "category": "plastic",
      "confidence": 0.96,
      "bbox": [120, 80, 250, 390]
    },
    {
      "id": 2,
      "category": "paper",
      "confidence": 0.91,
      "bbox": [400, 120, 650, 500]
    }
  ]
}
```

Bounding-box convention:

`[x1, y1, x2, y2]`

Coordinates refer to pixels in the original image.

The real response will contain all detections.

## 7.4 Backend Engineering Requirements

- File size limits.
    
- Supported image format validation.
    
- Image dimension limits.
    
- Request timeouts.
    
- Useful error responses.
    
- Model loading and failure handling.
    
- Model instance reuse.
    
- API versioning.
    
- No unnecessary image retention.
    
- No logging of private image contents.
    

Initially, inference will run on the server rather than directly on the phone.

---

# 8. Mobile Application — React Native + Expo

## 8.1 Why React Native + Expo?

We selected React Native + Expo because:

- It supports Android and iOS.
    
- Expo simplifies camera and gallery integration.
    
- TypeScript improves maintainability.
    
- REST API integration is straightforward.
    
- It supports rapid prototyping.
    
- It keeps mobile development separate from AI training.
    

The first release will prioritize Android.

## 8.2 Application Screens

### Screen 1 — Home

- EcoSort AI branding.
    
- Scan waste button.
    
- Short application introduction.
    
- Recent scan summary.
    
- Material category overview.
    

### Screen 2 — Scanner

- Open camera.
    
- Upload from gallery.
    
- Capture photograph.
    
- Preview photograph.
    
- Retake or confirm.
    
- Scanning instructions.
    

### Screen 3 — Results

- Photograph with bounding boxes.
    
- Object labels.
    
- Confidence scores.
    
- Total object count.
    
- Category-wise counts.
    
- Individual object list.
    
- Sorting guidance.
    

### Screen 4 — History

- Previous scans.
    
- Scan timestamps.
    
- Detection counts.
    
- Category distribution.
    
- Open previous results.
    

### Screen 5 — Learn

- Material categories.
    
- Examples.
    
- Common segregation mistakes.
    
- Waste sorting instructions.
    

## 8.3 Mobile Folder Structure

```
ecosort-mobile/
│
├── app/
│   ├── _layout.tsx
│   ├── index.tsx
│   ├── scan.tsx
│   ├── results.tsx
│   ├── history.tsx
│   └── learn.tsx
│
├── src/
│   ├── components/
│   │   ├── DetectionOverlay.tsx
│   │   ├── CategoryCard.tsx
│   │   ├── ScanButton.tsx
│   │   └── LoadingState.tsx
│   │
│   ├── features/
│   │   ├── scanner/
│   │   ├── results/
│   │   ├── history/
│   │   └── learning/
│   │
│   ├── services/
│   │   └── api.ts
│   │
│   ├── hooks/
│   ├── types/
│   ├── constants/
│   └── utils/
│
├── assets/
├── package.json
└── tsconfig.json
```

## 8.4 Mobile Detection Overlay

The application must draw bounding boxes over the original image.

Important:

- Correct coordinate scaling.
    
- Correct aspect-ratio handling.
    
- Correct image cropping calculations.
    
- Category-specific labels.
    
- Confidence display.
    
- Tap-to-view object information, if useful.
    

Do not simply scale coordinates by screen width without accounting for the image's actual display mode.

---

# 9. Database Architecture — Supabase

Database integration is optional for the first working scan.

The AI detection endpoint must function without user authentication or database access.

## 9.1 Suggested Tables

### profiles

- id
    
- display_name
    
- created_at
    

### scans

- id
    
- user_id
    
- total_objects
    
- created_at
    
- model_version
    

### detections

- id
    
- scan_id
    
- category
    
- confidence
    
- bbox
    

### feedback

- id
    
- scan_id
    
- detection_id
    
- feedback_type
    
- created_at
    

## 9.2 Relationships

```
profiles
   |
   | one-to-many
   v
scans
   |
   | one-to-many
   v
detections

scans
   |
   | one-to-many
   v
feedback
```

## 9.3 Privacy

- Avoid saving original photographs by default.
    
- Store detection results when required.
    
- Provide a way to delete user history.
    
- Protect user-specific records with database access policies.
    
- Do not collect unnecessary personal information.
    

---

# 10. Waste Disposal Guidance System

The AI model identifies material categories.

It should not independently invent disposal instructions.

We will use a separate rules-based guidance layer.

|Material|General guidance|
|---|---|
|Paper|Keep clean and dry; separate from wet waste|
|Plastic|Empty and clean where appropriate; follow local dry-waste rules|
|Metal|Separate recyclable metal containers|
|Organic|Separate food and biodegradable waste|

### Important Limitations

- Composite materials may contain multiple materials.
    
- Food-contaminated packaging may not be recyclable.
    
- Local municipal rules can differ.
    
- Material identification alone does not determine recyclability.
    

Future improvement:

Build a location-aware disposal guidance system using verified municipal information.

Do not claim that every object in a material category is universally recyclable.

---

# 11. Complete Development Roadmap

## Phase 1 — Research and Project Setup

**Objective:** Understand the existing solutions and establish the development environment.

- Inspect relevant GitHub waste detection projects.
    
- Compare YOLO model variants.
    
- Review TACO dataset.
    
- Find additional annotated datasets.
    
- Check dataset licenses.
    
- Confirm four-category label mapping.
    
- Create GitHub repository.
    
- Create project directory structure.
    
- Set up Python environment.
    
- Set up React Native + Expo environment.
    

**Deliverable:** Project foundation and dataset/model selection report.

## Phase 2 — Dataset Preparation

**Objective:** Build a clean, annotated dataset.

- Download candidate datasets.
    
- Inspect images and labels.
    
- Map source labels.
    
- Clean the dataset.
    
- Annotate missing bounding boxes.
    
- Review annotation quality.
    
- Remove duplicates.
    
- Create training split.
    
- Create validation split.
    
- Create test split.
    
- Inspect class imbalance.
    

**Deliverable:** Four-category YOLO-compatible dataset.

## Phase 3 — AI Model Development

**Objective:** Train the first multi-object waste detector.

- Load pretrained YOLO weights.
    
- Configure four classes.
    
- Train baseline model.
    
- Monitor training and validation.
    
- Save best checkpoint.
    
- Evaluate test performance.
    
- Generate confusion and error analysis.
    
- Test difficult real-world images.
    
- Tune confidence threshold.
    
- Record model version.
    

**Deliverable:** Working and evaluated YOLO model.

## Phase 4 — Backend Development

**Objective:** Make the model accessible through an API.

- Create FastAPI project.
    
- Implement health endpoint.
    
- Load trained model.
    
- Implement image upload endpoint.
    
- Implement validation.
    
- Implement inference.
    
- Implement post-processing.
    
- Map bounding boxes.
    
- Calculate category counts.
    
- Return structured JSON.
    
- Add error handling.
    
- Test using Postman or automated tests.
    

**Deliverable:** Working image detection API.

## Phase 5 — Mobile Development

**Objective:** Build the EcoSort AI Android application.

- Initialize Expo project.
    
- Configure TypeScript.
    
- Set up Expo Router.
    
- Build home screen.
    
- Implement camera.
    
- Implement gallery upload.
    
- Build image preview.
    
- Implement API service.
    
- Build results screen.
    
- Implement bounding-box overlay.
    
- Add category cards and counts.
    
- Build history screen.
    
- Build learn screen.
    
- Implement loading and error states.
    

**Deliverable:** Working mobile interface connected to the backend.

## Phase 6 — Integration

**Objective:** Connect the entire system.

- Connect mobile app to FastAPI.
    
- Test image upload.
    
- Test model inference.
    
- Verify JSON response.
    
- Verify coordinate mapping.
    
- Verify bounding boxes.
    
- Verify category counts.
    
- Test no-detection cases.
    
- Test low-confidence cases.
    
- Test network failure cases.
    

**Deliverable:** Complete end-to-end EcoSort AI MVP.

## Phase 7 — Database and Advanced Features

**Objective:** Improve the application after the core workflow is stable.

- Integrate Supabase.
    
- Add optional authentication.
    
- Save scan history.
    
- Save detection metadata.
    
- Build scan statistics.
    
- Add feedback system.
    
- Improve educational content.
    
- Add multilingual support if time permits.
    

**Deliverable:** Enhanced EcoSort AI application.

## Phase 8 — Testing and Deployment

**Objective:** Prepare a reliable demonstration and release.

- Test on physical Android devices.
    
- Test different image sizes.
    
- Test difficult lighting.
    
- Test overlapping objects.
    
- Test small objects.
    
- Measure inference latency.
    
- Measure API response time.
    
- Optimize image upload.
    
- Deploy backend.
    
- Configure production API URL.
    
- Build Android APK.
    
- Test the release build.
    
- Prepare project documentation.
    
- Prepare demo video.
    

**Deliverable:** Demonstrable and deployable application.

---

# 12. Suggested GitHub Repository Structure

I recommend a monorepo initially so that the complete project is easy to manage.

```
EcoSort-AI/
│
├── ai-model/
│   ├── datasets/
│   ├── configs/
│   ├── notebooks/
│   ├── scripts/
│   ├── training/
│   ├── evaluation/
│   ├── weights/
│   └── README.md
│
├── backend/
│   ├── app/
│   │   ├── main.py
│   │   ├── api/
│   │   ├── core/
│   │   ├── services/
│   │   ├── schemas/
│   │   └── utils/
│   ├── tests/
│   ├── requirements.txt
│   └── README.md
│
├── mobile/
│   ├── app/
│   ├── src/
│   ├── assets/
│   ├── package.json
│   └── README.md
│
├── docs/
│   ├── architecture.md
│   ├── dataset.md
│   ├── api.md
│   ├── model-evaluation.md
│   └── user-guide.md
│
├── .gitignore
├── LICENSE
└── README.md
```

Do not commit large datasets, private credentials or unnecessary model checkpoints to GitHub. Use appropriate storage for datasets and model artifacts, and document how to obtain them.

---

# 13. Testing Strategy

## 13.1 AI Testing

|Scenario|Expected behavior|
|---|---|
|One object|Detect and classify it|
|Multiple objects|Detect each independently|
|No waste|Return no detections|
|Overlapping objects|Detect visible objects where possible|
|Small objects|Evaluate detection limitations|
|Low light|Measure performance degradation|
|Transparent plastic|Evaluate false negatives|
|Composite packaging|Avoid unsupported material certainty|

## 13.2 Backend Testing

- Invalid file.
    
- Oversized image.
    
- Unsupported format.
    
- Corrupt image.
    
- Model unavailable.
    
- No detections.
    
- Multiple detections.
    
- Invalid request.
    
- API timeout.
    

## 13.3 Mobile Testing

- Camera permission denied.
    
- Gallery permission denied.
    
- Image upload failure.
    
- Slow network.
    
- Backend unavailable.
    
- Empty result.
    
- Incorrect image orientation.
    
- Bounding-box alignment.
    
- Navigation and screen responsiveness.
    

---

# 14. Risks and Technical Challenges

|Risk|Mitigation|
|---|---|
|Incorrect label mapping|Manually review source labels|
|Poor dataset diversity|Add real-world photographs|
|Class imbalance|Analyze and address training distribution|
|Small object detection|Experiment with resolution and model variants|
|Overlapping objects|Improve data and evaluate detection limitations|
|Composite materials|Add uncertainty and user guidance|
|Poor generalization|Maintain independent test data|
|Slow API inference|Optimize model and image handling|
|Misaligned boxes|Correct coordinate transformation|
|Incorrect disposal advice|Use verified rules-based guidance|

### Important Technical Decision

We should not immediately attempt on-device YOLO inference.

First:

1. Train and evaluate the model.
    
2. Serve it using FastAPI.
    
3. Complete the mobile integration.
    
4. Measure performance.
    
5. Investigate mobile model export and inference only if offline operation is necessary.
    

---

# 15. Milestones and Definition of Done

|Milestone|Completion criteria|
|---|---|
|M1: Setup|Repositories and environments work|
|M2: Dataset|Four classes with reviewed bounding boxes|
|M3: Model|Trained model produces valid multi-object detections|
|M4: Backend|API returns structured results|
|M5: Mobile|Camera and gallery workflows work|
|M6: Integration|Mobile app displays actual model predictions|
|M7: Enhancement|History and optional feedback work|
|M8: Release|Android build tested on physical device|

### MVP Acceptance Criteria

The MVP is complete when:

- A user can capture or upload an image.
    
- The backend can process the image.
    
- The AI model can return multiple object detections.
    
- Each detection includes a category, confidence and bounding box.
    
- The application draws correctly aligned boxes.
    
- The application calculates category counts.
    
- Empty and uncertain results are handled properly.
    
- The application works on a physical Android device.
    

---

# 16. Development Order — What We Should Actually Do First

Do not start building all three modules simultaneously.

The order matters.

### Step 1 — Validate the AI approach

Research existing repositories, pretrained models and datasets.

### Step 2 — Build the dataset

Confirm that we can obtain enough correctly annotated examples for all four classes.

### Step 3 — Train a baseline model

Get YOLO detecting waste objects before spending time on the mobile interface.

### Step 4 — Build a local inference script

Test images locally and inspect bounding boxes and predictions.

### Step 5 — Build FastAPI

Expose the trained model through a working endpoint.

### Step 6 — Build React Native + Expo

Create the application screens and camera/gallery functionality.

### Step 7 — Integrate the mobile app

Connect the app to the backend and render the actual detections.

### Step 8 — Polish, test and deploy

Improve the UI, evaluate difficult scenarios and prepare the Android build.

---

# 17. Official Documentation and Resources

|Resource|Link|
|---|---|
|Ultralytics|[https://docs.ultralytics.com/](https://docs.ultralytics.com/)|
|PyTorch|[https://pytorch.org/docs/stable/index.html](https://pytorch.org/docs/stable/index.html)|
|TACO Dataset|[https://tacodataset.org/](https://tacodataset.org/)|
|TACO GitHub|[https://github.com/pedropro/TACO](https://github.com/pedropro/TACO)|
|Roboflow|[https://roboflow.com/](https://roboflow.com/)|
|CVAT|[https://www.cvat.ai/](https://www.cvat.ai/)|
|FastAPI|[https://fastapi.tiangolo.com/](https://fastapi.tiangolo.com/)|
|React Native|[https://reactnative.dev/](https://reactnative.dev/)|
|Expo|[https://docs.expo.dev/](https://docs.expo.dev/)|
|Expo Camera|[https://docs.expo.dev/versions/latest/sdk/camera/](https://docs.expo.dev/versions/latest/sdk/camera/)|
|Expo ImagePicker|[https://docs.expo.dev/versions/latest/sdk/imagepicker/](https://docs.expo.dev/versions/latest/sdk/imagepicker/)|
|Supabase|[https://supabase.com/docs](https://supabase.com/docs)|

Check dataset and model licensing before using them in a public or commercial release.

---

# 18. Final Architecture Decision

```
                 ECOSORT AI
                     |
          React Native + Expo
                     |
                Image Upload
                     |
                     v
               FastAPI Backend
                     |
              Image Processing
                     |
                     v
              YOLO + PyTorch
                     |
            Multi-Object Detection
                     |
          +----------+----------+
          |          |          |
        Paper     Plastic     Metal
          |          |          |
          +----------+----------+
                     |
                  Organic
                     |
                     v
            Structured Results
                     |
              Sorting Guidance
                     |
                     v
             Mobile Results UI
                     |
              Optional Supabase
```

## Final Decisions

|Decision|Selected approach|
|---|---|
|Project type|Multi-object waste detection|
|AI architecture|Pretrained YOLO detector + fine-tuning|
|ML framework|PyTorch|
|Initial classes|Paper, plastic, metal, organic|
|Annotation|Roboflow / CVAT|
|Backend|FastAPI|
|Mobile framework|React Native + Expo|
|Mobile language|TypeScript|
|Database|Supabase, optional initially|
|Initial deployment|Backend hosting + Android build|
|Inference location|Backend/server|
|Development strategy|AI → Backend → Mobile → Integration|

> [!success] First Development Target  
> Before building the complete mobile application, we must demonstrate that our YOLO model can reliably detect multiple waste objects in a single photograph.
> 
> Our first meaningful technical milestone is a locally running model that accepts an image and returns correctly labelled bounding boxes for multiple objects.

**Project philosophy:** Build the intelligence first, build the interface around it, and validate the complete system using real-world images.