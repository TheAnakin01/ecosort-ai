# 05 Backend and Database Audit — EcoSort AI

**Audit date:** 2026-11-17  
**Repository:** `TheAnakin01/ecosort-ai`  
**Branch:** `feature/kaggle-kaggle-notebook-setup`

---

## Backend Implementation Status

The backend (`backend/`) is a **skeleton/prototype only**. No inference API is functional. The mobile app points to `https://api.example.com` (placeholder — no real backend exists).

### Backend Files Present

| File | Purpose | Status |
|------|---------|--------|
| `app/main.py` | FastAPI app skeleton | Exists; endpoints planned, not wired |
| `app/config.py` | Configuration | Exists; not connected to any service |
| `app/detector.py` | Detector service interface | Exists; not connected to model |
| `app/onnx_detector.py` | ONNX-based detector | Exists; not integrated |
| `app/schemas.py` | Pydantic request/response schemas | Exists; defines contracts |
| `app/errors.py` | Error response contract | Exists; defines error shapes |
| `app/guidance.py` | Rules-based sorting guidance | Exists; not connected to API |
| `app/__init__.py` | Package init | Exists |
| `tests/test_api.py` | API endpoint tests | Exists; tests against placeholder |
| `tests/test_onnx_detector.py` | ONNX detector tests | Exists; needs weights |
| `tests/test_onnx_parity.py` | PyTorch vs ONNX parity | Exists; needs weights |
| `tests/test_real_model.py` | Real model test | Exists; needs weights |
| `requirements.txt` | Backend dependencies | Exists |
| `requirements-dev.txt` | Backend dev dependencies | Exists |
| `requirements-base.txt` | Base dependencies | Exists |
| `requirements-onnx.txt` | ONNX runtime dependencies | Exists |
| `Dockerfile` | Container build | Exists; not tested |
| `.env.example` | Environment variables template | Exists |
| `pytest.ini` | Pytest config | Exists |
| `README.md` | Backend setup | Exists |

### API Endpoints (Specified, Not Implemented)

Per `docs/EcoSort-AI-Agent-Harness/BACKEND_API.md`:

| Endpoint | Method | Status | Implementation |
|----------|--------|--------|----------------|
| `GET /health` | GET | Not implemented | Planned; returns `{"status": "ok", "model_loaded": true}` |
| `GET /api/v1/model-info` | GET | Not implemented | Planned; returns model metadata |
| `GET /api/v1/categories` | GET | Not implemented | Planned; returns canonical categories |
| `POST /api/v1/detect` | POST | Not implemented | Planned; accepts multipart image upload |

### Response Contract (Specified, Not Implemented)

Per `BACKEND_API.md`, a successful detect response should include:
- `success`, `image_width`, `image_height`, `total_objects`, `counts`, `detections[]`, `model_version`
- Each detection: `id`, `category`, `confidence`, `bbox [x1,y1,x2,y2]`

None of this is implemented in code.

### Error Contract (Specified, Not Implemented)

| Status Code | Condition | Implemented? |
|-------------|-----------|-------------|
| 400 | Malformed request | No |
| 413 | Upload too large | No |
| 415 | Unsupported media/decoded format | No |
| 422 | Image cannot be decoded | No |
| 429 | Rate limit exceeded | No |
| 500 | Unexpected server error | No |
| 503 | Model unavailable/not ready | No |
| 504 | Inference timeout | No |

### Validation (Specified, Not Implemented)

Per `BACKEND_API.md` section 5:
- Approved raster formats (JPEG, PNG, WebP) — **not implemented**
- Validate decoded content, not just MIME type — **not implemented**
- Maximum upload size and pixel dimensions — **not implemented**
- Reject empty/corrupt/decompression-bomb images — **not implemented**
- EXIF orientation handling — **not implemented**
- Grayscale/RGBA inputs — **not implemented**
- Safe temporary file handling — **not implemented**
- No logging of image bytes — **not implemented**

### Inference Service Design (Specified, Not Implemented)

Per `BACKEND_API.md` section 6:
- Model loaded once at startup — **not implemented**
- Model invocation isolated behind service class — **not implemented**
- Thresholds and image size in validated configuration — **not implemented**
- Boxes converted to original oriented-image coordinates — **not implemented**
- Expected inference errors caught — **not implemented**
- No mock detections on model failure — **not implemented**

---

## Database Implementation Status

**No database exists.** The project explicitly defers database to a later phase.

Per `docs/EcoSort-AI-Agent-Harness/DATABASE_DESIGN.md`:
- MVP is scan-only; no database required
- Supabase/Postgres proposed for later phase (auth, history, feedback)
- Proposed entities: `profiles`, `scans`, `scan_detections`, `detection_feedback`
- Row Level Security proposed for user isolation
- Data minimization: no raw images stored by default

**Status:** Not implemented. Not required for MVP scan-only flow.

---

## Security Issues (Backend)

| Issue | Severity | Evidence | Required Fix |
|-------|----------|----------|-------------|
| No image upload validation | Critical | Backend not implemented | Implement file size/type validation, decoded content check |
| No CORS configuration | High | Not implemented | Restrict CORS origins |
| No HTTPS configuration | High | Not deployed | Enable HTTPS in production |
| No rate limiting | Medium | Not implemented | Add rate limits if needed |
| No secrets management | Medium | `.env.example` only; no production secrets | Use environment variables or secret manager |
| No structured logging | Medium | No logging implemented | Add safe logging (no image content) |
| No request IDs | Medium | Not implemented | Add request IDs for diagnostics |
| No timeouts | Medium | Not implemented | Configure request timeouts |
| No model-unavailable handling | High | Not implemented | Return 503 when model not loaded |
| No path traversal protection | Critical | Not implemented | Safe file handling if uploads written to disk |

---

## Performance Concerns (Backend)

| Concern | Status |
|---------|--------|
| Model loading once at startup | Not implemented |
| CPU inference blocking event loop | Not implemented |
| Concurrent inference limit | Not implemented |
| Request timeout | Not implemented |
| Memory usage per request | Not measured |
| Cold start time | Not measured |

Per `DEPLOYMENT_AND_RELEASE.md`: "Do not assume a serverless platform can run the chosen model efficiently without testing cold starts and runtime limits." Not yet tested.

---

## Missing Backend Functionality

| Feature | Priority | Required Work |
|---------|----------|---------------|
| `GET /health` endpoint | Critical | Implement health check |
| `GET /api/v1/model-info` endpoint | Critical | Implement model metadata endpoint |
| `GET /api/v1/categories` endpoint | Critical | Implement categories endpoint |
| `POST /api/v1/detect` endpoint | Critical | Implement image upload + inference |
| Model loading at startup | Critical | Load ONNX/PyTorch model once |
| Image upload validation | Critical | File size, type, decoded content |
| Error handling middleware | Critical | Safe error responses, no stack traces |
| CORS configuration | High | Restrict origins |
| HTTPS configuration | High | Enable in production |
| Request logging | Medium | Structured logging without image content |
| Rate limiting | Medium | Add if needed for production |
| Request timeouts | Medium | Configure timeouts |
| Model-unavailable (503) | High | Return 503 when model not ready |

---

## Database (Deferred by Design)

| Feature | Status | Notes |
|---------|--------|-------|
| Database engine | Not implemented | Supabase/Postgres proposed for later phase |
| Schema | Not implemented | Proposed entities documented |
| Migrations | Not implemented | Versioned SQL migrations planned |
| RLS | Not implemented | Planned for user isolation |
| Backups | Not implemented | Not required for MVP |
| Data retention | Not defined | To be defined before cloud history |

**Assessment:** Correctly deferred. The MVP is scan-only and does not require persistence. Adding a database now would be premature complexity.

---

## Test Coverage (Backend)

| Test File | Status | Dependencies |
|-----------|--------|--------------|
| `test_api.py` | Exists; tests against placeholder API | FastAPI test client |
| `test_onnx_detector.py` | Exists; needs ONNX weights | ONNX Runtime |
| `test_onnx_parity.py` | Exists; needs PyTorch + ONNX weights | PyTorch, ONNX, weights |
| `test_real_model.py` | Exists; needs real weights | PyTorch, weights |

**Cannot be executed** — Python is not available in this environment, and no model weights exist to test against.

---

## Integration Points

| Integration | Status | Notes |
|-------------|--------|-------|
| Mobile app → Backend | Not connected | Mobile uses `https://api.example.com` placeholder |
| Backend → Model | Not implemented | No model loading code |
| Backend → Database | Not implemented | Deferred to later phase |
| Backend → Secrets | Not implemented | `.env.example` only; no production secrets |
