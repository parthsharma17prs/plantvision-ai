"""Production-ready prediction module for YOLOv8 plant disease detection."""

from __future__ import annotations

import argparse
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Dict, List, Optional

import numpy as np
import pandas as pd
from PIL import Image


# Map model class labels to cleaner disease names.
CLASS_NAME_MAPPING: Dict[str, str] = {
    "Potato leaf early blight": "Early Blight",
    "Tomato Early blight leaf": "Early Blight",
    "Potato leaf late blight": "Late Blight",
    "Tomato leaf late blight": "Late Blight",
    "Tomato Septoria leaf spot": "Leaf Spot",
    "Bell_pepper leaf spot": "Leaf Spot",
    "Tomato leaf bacterial spot": "Leaf Spot",
}

# Recommendation dictionary requested by you.
PESTICIDE_RECOMMENDATIONS: Dict[str, str] = {
    "Early Blight": "Use Mancozeb or Chlorothalonil",
    "Late Blight": "Use Copper fungicide",
    "Leaf Spot": "Use Neem oil or fungicide spray",
}


@dataclass
class DetectionSummary:
    disease: str
    confidence_pct: float
    severity: str
    health_pct: float
    recommendation: str
    bbox_xyxy: tuple[float, float, float, float]
    infected_area_pct: float


def _auto_find_weights(default_rel: str = "runs/detect/train/weights/best.pt") -> Path:
    """Find best.pt, including fallback nested runs path."""
    root = Path.cwd()
    cand1 = (root / default_rel).resolve()
    if cand1.exists():
        return cand1

    cand2 = (root / "runs" / "detect" / "runs" / "detect" / "train" / "weights" / "best.pt").resolve()
    if cand2.exists():
        return cand2

    runs_dir = root / "runs"
    if runs_dir.exists():
        for p in runs_dir.rglob("best.pt"):
            return p.resolve()
    return cand1


def _pick_best_weights_by_map(root: Path) -> Optional[Path]:
    """
    Choose the best checkpoint by highest validation mAP50-95 if results.csv exists.
    Falls back to mAP50 if mAP50-95 is unavailable.
    """
    best_weight: Optional[Path] = None
    best_score = -1.0
    for csv_path in root.rglob("results.csv"):
        try:
            df = pd.read_csv(csv_path)
            if df.empty:
                continue
            metric_col = None
            for c in df.columns:
                if "metrics/mAP50-95(B)" in c:
                    metric_col = c
                    break
            if metric_col is None:
                for c in df.columns:
                    if "metrics/mAP50(B)" in c:
                        metric_col = c
                        break
            if metric_col is None:
                continue
            score = float(df.iloc[-1][metric_col])
            candidate = csv_path.parent / "weights" / "best.pt"
            if candidate.exists() and score > best_score:
                best_score = score
                best_weight = candidate.resolve()
        except Exception:
            continue
    return best_weight


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="YOLOv8 plant disease prediction module.")
    parser.add_argument(
        "--weights",
        type=str,
        default="auto",
        help="Path to trained model weights.",
    )
    parser.add_argument(
        "--image",
        type=str,
        default="",
        help="Path to input image. If empty, script asks with input().",
    )
    parser.add_argument(
        "--output-dir",
        type=str,
        default="inference_outputs",
        help="Directory to save annotated output image.",
    )
    parser.add_argument("--imgsz", type=int, default=960, help="Inference image size.")
    parser.add_argument("--conf", type=float, default=0.20, help="Confidence threshold.")
    parser.add_argument(
        "--augment",
        action="store_true",
        help="Enable test-time augmentation for potentially better predictions.",
    )
    parser.add_argument("--device", type=str, default="", help='Device: "cpu", "0", etc.')
    return parser.parse_args()


def resolve_image_path(image_arg: str) -> Path:
    """Resolve image from CLI arg or terminal input()."""
    image_input = image_arg.strip()
    if not image_input:
        image_input = input("Enter input image path: ").strip()
    if not image_input:
        raise ValueError("No image path provided.")
    image_path = Path(image_input)
    if not image_path.is_absolute():
        image_path = (Path.cwd() / image_path).resolve()
    return image_path


def load_model(weights_path: Path | str):
    """Load YOLOv8 model and handle import/path errors."""
    try:
        from ultralytics import YOLO  # type: ignore
    except Exception as e:
        raise RuntimeError(
            "Ultralytics import failed. Install with: pip install -r requirements.txt"
        ) from e

    if isinstance(weights_path, str) and weights_path.lower() == "auto":
        best_from_metrics = _pick_best_weights_by_map(Path.cwd() / "runs")
        if best_from_metrics and best_from_metrics.exists():
            weights_path = best_from_metrics
        else:
            auto = _auto_find_weights()
            if not auto.exists():
                raise FileNotFoundError("Model weights not found. Expected best.pt under runs/")
            weights_path = auto
    else:
        weights_path = Path(weights_path)
    if not weights_path.exists():
        auto = _auto_find_weights()
        if not auto.exists():
            raise FileNotFoundError(f"Model weights not found: {weights_path}")
        weights_path = auto

    return YOLO(str(weights_path)), weights_path


def map_class_to_disease(raw_class_name: str) -> str:
    """Map raw class labels to more meaningful disease names."""
    return CLASS_NAME_MAPPING.get(raw_class_name, raw_class_name)


def recommend_pesticide(disease_name: str) -> str:
    """Return recommendation for known diseases, else fallback."""
    return PESTICIDE_RECOMMENDATIONS.get(
        disease_name,
        "No specific recommendation available. Consult local agronomist.",
    )


def compute_infected_area_pct(bbox_xyxy: tuple[float, float, float, float], image_w: int, image_h: int) -> float:
    """Compute infected area % using bounding box area / total image area."""
    x1, y1, x2, y2 = bbox_xyxy
    box_w = max(0.0, x2 - x1)
    box_h = max(0.0, y2 - y1)
    bbox_area = box_w * box_h
    image_area = float(max(1, image_w * image_h))
    return min(100.0, max(0.0, (bbox_area / image_area) * 100.0))


def compute_severity(confidence_pct: float, infected_area_pct: float) -> str:
    """
    Compute severity using confidence + infected area.
    Combined score is average of the two signals.
    """
    combined = (confidence_pct + infected_area_pct) / 2.0
    if combined < 10.0:
        return "Low"
    if combined < 30.0:
        return "Medium"
    return "Severe"


def summarize_detections(result: Any, model: Any) -> List[DetectionSummary]:
    """Extract class, confidence, bbox, and derive severity + health + recommendation."""
    summaries: List[DetectionSummary] = []
    boxes = result.boxes
    if boxes is None or len(boxes) == 0:
        return summaries

    img_h, img_w = result.orig_shape
    model_names = getattr(model, "names", {})

    for box in boxes:
        cls_id = int(box.cls[0]) if box.cls is not None else -1
        raw_name = str(model_names.get(cls_id, cls_id))
        disease_name = map_class_to_disease(raw_name)

        conf = float(box.conf[0]) if box.conf is not None else 0.0
        confidence_pct = max(0.0, min(100.0, conf * 100.0))

        coords = box.xyxy[0].tolist()
        bbox_xyxy = (float(coords[0]), float(coords[1]), float(coords[2]), float(coords[3]))
        infected_area_pct = compute_infected_area_pct(bbox_xyxy, img_w, img_h)
        severity = compute_severity(confidence_pct, infected_area_pct)
        health_pct = max(0.0, min(100.0, 100.0 - infected_area_pct))
        recommendation = recommend_pesticide(disease_name)

        summaries.append(
            DetectionSummary(
                disease=disease_name,
                confidence_pct=confidence_pct,
                severity=severity,
                health_pct=health_pct,
                recommendation=recommendation,
                bbox_xyxy=bbox_xyxy,
                infected_area_pct=infected_area_pct,
            )
        )

    return summaries


def save_annotated_image(result: Any, image_path: Path, output_dir: Path) -> Path:
    """Save image with YOLO bounding boxes."""
    output_dir.mkdir(parents=True, exist_ok=True)
    annotated_bgr = result.plot()
    if not isinstance(annotated_bgr, np.ndarray):
        raise RuntimeError("Unexpected output type while plotting detections.")
    annotated_rgb = annotated_bgr[:, :, ::-1]
    annotated_image = Image.fromarray(annotated_rgb)
    out_path = output_dir / f"{image_path.stem}_predicted{image_path.suffix}"
    annotated_image.save(out_path)
    return out_path


def print_report(summary: DetectionSummary) -> None:
    """Print final report in required clean format."""
    print(f"Disease: {summary.disease}")
    print(f"Confidence: {summary.confidence_pct:.2f}%")
    print(f"Severity: {summary.severity}")
    print(f"Health: {summary.health_pct:.2f}%")
    print(f"Recommendation: {summary.recommendation}")


def run_prediction(
    model: Any,
    image_path: Path,
    output_dir: Path,
    imgsz: int,
    conf: float,
    augment: bool,
    device: Optional[str],
) -> tuple[List[DetectionSummary], Path]:
    """Run YOLO predict, build summaries, and save annotated image."""
    if not image_path.exists() or not image_path.is_file():
        raise FileNotFoundError(f"Invalid image path: {image_path}")

    kwargs: Dict[str, Any] = {
        "source": str(image_path),
        "imgsz": int(imgsz),
        "conf": float(conf),
        "augment": bool(augment),
        "verbose": False,
    }
    if device and device.strip():
        kwargs["device"] = device.strip()

    results = model.predict(**kwargs)
    if not results:
        raise RuntimeError("No prediction result returned by model.")

    result = results[0]
    summaries = summarize_detections(result, model)
    out_path = save_annotated_image(result, image_path, output_dir)
    return summaries, out_path


def main() -> int:
    args = parse_args()
    try:
        image_path = resolve_image_path(args.image)
        output_dir = (Path.cwd() / args.output_dir).resolve()
        weights_arg: Path | str = "auto" if args.weights.strip().lower() == "auto" else (Path.cwd() / args.weights).resolve()
        model, used_weights = load_model(weights_arg)

        summaries, output_image = run_prediction(
            model=model,
            image_path=image_path,
            output_dir=output_dir,
            imgsz=args.imgsz,
            conf=args.conf,
            augment=args.augment,
            device=args.device,
        )

        print(f"Using model weights: {used_weights}")
        if not summaries:
            print("No detection found.")
            print(f"Annotated output saved at: {output_image}")
            return 0

        # Report highest-confidence detection first for clean single-result output.
        best = max(summaries, key=lambda s: s.confidence_pct)
        print_report(best)
        print(f"Annotated output saved at: {output_image}")
        return 0

    except Exception as e:
        print(f"ERROR: {e}")
        return 1


if __name__ == "__main__":
    raise SystemExit(main())

