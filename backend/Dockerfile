# EcoSort AI backend, ONNX runtime (no PyTorch). Build from the repo root:
#   docker build -f backend/Dockerfile -t ecosort-backend .
# Needs ai-model/weights/best.onnx in the build context (see docs/PROJECT_STATUS.md).
FROM python:3.13-slim

ENV PYTHONUNBUFFERED=1 PIP_NO_CACHE_DIR=1 PIP_DISABLE_PIP_VERSION_CHECK=1

WORKDIR /srv
COPY backend/requirements-base.txt backend/requirements-onnx.txt ./
RUN pip install -r requirements-onnx.txt

COPY backend/app ./app
COPY ai-model/weights/best.onnx /models/best.onnx

ENV MODEL_PATH=/models/best.onnx
RUN useradd --no-create-home appuser
USER appuser

# Hosts such as Render set PORT; default to 8000 locally.
EXPOSE 8000
CMD ["sh", "-c", "uvicorn app.main:app --host 0.0.0.0 --port ${PORT:-8000}"]
