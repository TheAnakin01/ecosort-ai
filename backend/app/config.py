"""Backend settings. Each one can be overridden with an environment variable."""

import os
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]

# Trained weights. Copy best.pt from training into ai-model/weights/.
MODEL_PATH = Path(os.getenv("MODEL_PATH", REPO_ROOT / "ai-model" / "weights" / "best.pt"))
MODEL_VERSION = os.getenv("MODEL_VERSION", "baseline")

# Detections below this confidence are not returned at all.
CONFIDENCE_THRESHOLD = float(os.getenv("CONFIDENCE_THRESHOLD", "0.35"))
# Detections below this are returned but flagged as uncertain.
LOW_CONFIDENCE_THRESHOLD = float(os.getenv("LOW_CONFIDENCE_THRESHOLD", "0.5"))

MAX_UPLOAD_BYTES = int(os.getenv("MAX_UPLOAD_MB", "10")) * 1024 * 1024
MAX_IMAGE_SIDE = int(os.getenv("MAX_IMAGE_SIDE", "6000"))
ALLOWED_FORMATS = {"JPEG", "PNG", "WEBP"}

CATEGORIES = ["paper", "plastic", "metal", "organic"]
