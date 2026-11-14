---
name: model-export-optimization
description: Export and optimize EcoSort AI object-detection models for a verified inference runtime, including LiteRT/TensorFlow Lite or server-side deployment.
---

# Model Export and Optimization

## Goal

Export the approved multi-object detector without silently changing model behavior or deployment assumptions.

## First decide the inference target

The current plan uses FastAPI for initial inference. On-device inference is not approved by default. Before selecting an export path, confirm:
- Server inference or on-device inference
- Target devices and operating systems
- Offline requirement
- Network/privacy expectations
- Latency and memory budget
- Whether Expo native modules or a custom development build are acceptable

## Compatibility verification

For the exact model and framework versions, verify official support for:
- Export operation
- Supported operators
- Dynamic/static input shapes
- Output tensor structure
- Non-maximum suppression behavior
- Quantization support
- Runtime availability on target devices
- License and redistribution terms

Do not assume every PyTorch/TensorFlow model exports cleanly to LiteRT/TFLite or that a model can run inside Expo Go.

## Optimization workflow

1. Preserve the validated full-precision checkpoint.
2. Export a baseline artifact.
3. Verify numerical and detection parity on a fixed representative test set.
4. Benchmark model size, peak memory, warm and cold latency, and throughput.
5. Evaluate post-training quantization where supported.
6. Consider representative calibration data for integer quantization.
7. Re-evaluate detection metrics after each optimization.
8. Compare accuracy/latency/size trade-offs and retain the best acceptable artifact.

Do not optimize before a reliable baseline exists.

## Preprocessing and output contract

Document and test:
- Color channel order
- Pixel range and normalization
- Resize/letterbox policy
- Padding values and coordinate transforms
- Input tensor layout and dtype
- Output tensor names/shapes
- Box coordinate convention
- Class-index mapping
- Confidence and NMS behavior

## Deliverables

- Export script and exact command
- Runtime/dependency versions
- Model artifact checksum and size
- Preprocessing/postprocessing specification
- Parity test results
- Accuracy/latency/memory comparison
- Known unsupported operations or runtime limitations

Never claim mobile-ready until tested on representative physical devices or a clearly documented target runtime.
