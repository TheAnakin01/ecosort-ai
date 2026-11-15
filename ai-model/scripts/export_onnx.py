"""Export trained weights (best.pt) to ONNX so the backend can run without PyTorch.

Example:
    python ai-model/scripts/export_onnx.py --weights ai-model/weights/best.pt

Writes best.onnx next to the weights, plus best.onnx.json with the size, SHA-256
and export settings, so the artifact can be traced to the checkpoint it came from.
The .pt file is never modified.
"""

import argparse
import hashlib
import json
from pathlib import Path


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1 << 20), b""):
            digest.update(block)
    return digest.hexdigest()


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--weights", type=Path, required=True)
    parser.add_argument(
        "--imgsz", type=int, default=640, help="Longest-side size used by the backend; use the training size."
    )
    parser.add_argument("--opset", type=int, default=17)
    args = parser.parse_args()

    from ultralytics import YOLO
    from ultralytics import __version__ as ultralytics_version

    model = YOLO(str(args.weights))
    # Dynamic input shape so the backend can letterbox exactly like Ultralytics
    # (minimal padding, not a fixed square); FP32; no NMS inside the graph: NMS
    # is done in the backend so thresholds stay configurable.
    exported = Path(
        model.export(
            format="onnx", imgsz=args.imgsz, opset=args.opset, dynamic=True, half=False, simplify=True, nms=False
        )
    )

    record = {
        "source_weights": args.weights.name,
        "source_sha256": sha256(args.weights),
        "onnx_file": exported.name,
        "onnx_size_bytes": exported.stat().st_size,
        "onnx_sha256": sha256(exported),
        "imgsz": args.imgsz,
        "opset": args.opset,
        "class_names": [model.names[i] for i in sorted(model.names)],
        "ultralytics_version": ultralytics_version,
    }
    record_path = exported.with_suffix(".onnx.json")
    record_path.write_text(json.dumps(record, indent=2) + "\n")
    print(json.dumps(record, indent=2))


if __name__ == "__main__":
    main()
