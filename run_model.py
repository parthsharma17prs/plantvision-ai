#!/usr/bin/env python3
"""
run_model.py

Run inference using the PlantVision AI model and Tri-Engine Diagnostic Suite:
1. YOLOv8 foliar pathology detection (bounding boxes, disease classification, confidence, severity)
2. Pest Detection Adapter (pest damage analysis, IPM biocontrols & chemical recommendations)
3. Nutrition Deficiency Engine (7-element canopy balance: N, P, K, Mg, Fe, Ca, Zn)

Usage:
  python run_model.py                                      # Runs on a random test image
  python run_model.py --source datasets/plantdoc/test/images/sample.jpg
  python run_model.py --source datasets/plantdoc/test/images/ --num-samples 3
"""

from __future__ import annotations

import argparse
import random
import sys
from pathlib import Path

from PIL import Image

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
if hasattr(sys.stderr, "reconfigure"):
    sys.stderr.reconfigure(encoding="utf-8", errors="replace")

ROOT = Path(__file__).resolve().parent

# Import Tri-Engine modules
from pest_adapter import PestDetectionAdapter
from nutrition_engine import NutritionDeficiencyEngine

CLASS_NAME_MAPPING = {
    "Potato leaf early blight": "Early Blight",
    "Tomato Early blight leaf": "Early Blight",
    "Potato leaf late blight": "Late Blight",
    "Tomato leaf late blight": "Late Blight",
    "Tomato Septoria leaf spot": "Leaf Spot",
    "Bell_pepper leaf spot": "Leaf Spot",
    "Tomato leaf bacterial spot": "Bacterial Spot",
    "Tomato mold leaf": "Leaf Mold",
    "Tomato two spotted spider mites leaf": "Spider Mites",
    "Tomato leaf yellow virus": "Yellow Leaf Curl Virus",
    "Tomato leaf mosaic virus": "Mosaic Virus",
    "Squash Powdery mildew leaf": "Powdery Mildew",
    "Corn Gray leaf spot": "Gray Leaf Spot",
    "Corn leaf blight": "Leaf Blight",
    "Corn rust leaf": "Rust",
    "Apple Scab Leaf": "Apple Scab",
    "Apple rust leaf": "Apple Rust",
    "grape leaf black rot": "Black Rot",
    "Tomato Target Spot": "Target Spot",
    "Pepper__bell___Bacterial_spot": "Bacterial Spot",
    "Pepper__bell___healthy": "Healthy",
    "Potato___Early_blight": "Early Blight",
    "Potato___Late_blight": "Late Blight",
    "Potato___healthy": "Healthy",
    "Tomato_Bacterial_spot": "Bacterial Spot",
    "Tomato_Early_blight": "Early Blight",
    "Tomato_Late_blight": "Late Blight",
    "Tomato_Leaf_Mold": "Leaf Mold",
    "Tomato_Septoria_leaf_spot": "Leaf Spot",
    "Tomato_Spider_mites_Two_spotted_spider_mite": "Spider Mites",
    "Tomato__Target_Spot": "Target Spot",
    "Tomato__Tomato_YellowLeaf__Curl_Virus": "Yellow Leaf Curl Virus",
    "Tomato__Tomato_mosaic_virus": "Mosaic Virus",
    "Tomato_healthy": "Healthy",
    "Healthy": "Healthy",
}


def pick_weights() -> Path:
    for cand in [
        ROOT / "best.pt",
        ROOT / "runs" / "detect" / "train" / "weights" / "best.pt",
        ROOT / "yolov8n.pt",
    ]:
        if cand.exists():
            return cand
    return ROOT / "yolov8n.pt"


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Run PlantVision AI model inference.")
    parser.add_argument(
        "--source",
        type=str,
        default="",
        help="Path to an image file or directory of images. If empty, picks sample from test set.",
    )
    parser.add_argument(
        "--weights",
        type=str,
        default="",
        help="Path to model weights (.pt). Default: best.pt or yolov8n.pt.",
    )
    parser.add_argument(
        "--conf",
        type=float,
        default=0.15,
        help="Confidence threshold for YOLO detections (default: 0.15).",
    )
    parser.add_argument(
        "--num-samples",
        type=int,
        default=1,
        help="Number of images to process if source is a directory (default: 1).",
    )
    parser.add_argument(
        "--save",
        action="store_true",
        default=True,
        help="Save annotated images with bounding boxes to runs/detect/predict (default: True).",
    )
    return parser.parse_args()


def find_sample_images(source_path: str, count: int) -> list[Path]:
    if source_path:
        p = Path(source_path)
        if p.is_file():
            return [p]
        if p.is_dir():
            imgs = [f for f in p.glob("*.*") if f.suffix.lower() in {".jpg", ".jpeg", ".png", ".bmp"}]
            if imgs:
                return random.sample(imgs, min(count, len(imgs)))

    # Fallback to test split
    candidates = [
        ROOT / "datasets" / "combined" / "val" / "images",
        ROOT / "datasets" / "plantdoc" / "test" / "images",
        ROOT / "datasets" / "plantvillage" / "val" / "images",
        ROOT / "datasets" / "plantdoc" / "valid" / "images",
    ]
    for c in candidates:
        if c.exists():
            imgs = [f for f in c.glob("*.*") if f.suffix.lower() in {".jpg", ".jpeg", ".png", ".bmp"}]
            if imgs:
                return random.sample(imgs, min(count, len(imgs)))

    return []


def run_inference_on_image(img_path: Path, model, conf: float, save: bool) -> None:
    print("\n" + "=" * 65)
    print(f"🌿 Processing Image: {img_path.name}")
    print("=" * 65)

    pil_img = Image.open(img_path).convert("RGB")
    w, h = pil_img.size
    print(f"- Image Dimensions: {w} x {h}")

    # 1. YOLOv8 Pathology Detection
    results = model.predict(source=str(img_path), conf=conf, save=save, verbose=False)
    r = results[0]
    boxes = r.boxes
    names = model.names

    print(f"\n[1. YOLOv8 Foliar Pathology Engine]")
    if len(boxes) == 0:
        print("  - Detection: No disease lesions detected above threshold. Plant appears healthy.")
        top_disease = "Healthy"
    else:
        print(f"  - Detected {len(boxes)} lesion/leaf region(s):")
        top_disease = "Healthy"
        max_conf = 0.0
        for i, box in enumerate(boxes):
            cls_id = int(box.cls[0])
            raw_name = names.get(cls_id, str(cls_id))
            display_name = CLASS_NAME_MAPPING.get(raw_name, raw_name)
            box_conf = float(box.conf[0]) * 100.0
            x1, y1, x2, y2 = box.xyxy[0].tolist()
            area_pct = ((x2 - x1) * (y2 - y1)) / (w * h) * 100.0
            print(f"    [{i + 1}] {display_name} | Conf: {box_conf:.1f}% | Area: {area_pct:.1f}% | Box: [{x1:.0f}, {y1:.0f}, {x2:.0f}, {y2:.0f}]")
            if box_conf > max_conf and not display_name.lower().endswith("healthy"):
                max_conf = box_conf
                top_disease = display_name

    # 2. Pest Detection Adapter
    print(f"\n[2. Pest Detection Adapter (IPM Suite)]")
    pest_adapter = PestDetectionAdapter()
    pest_res = pest_adapter.analyze(pil_img, top_disease)
    top_pest = pest_res.get("top_pest", "None detected")
    pest_risk = pest_res.get("risk_level", "Low")
    pest_score = pest_res.get("confidence", 0.0)
    print(f"  - Target Pest: {top_pest}")
    print(f"  - Infestation Risk: {pest_risk} (Index: {pest_score}%)")
    ipm = pest_res.get("ipm_recommendations", {})
    if ipm.get("chemical"):
        print(f"  - Chemical Active: {ipm['chemical']}")
    if ipm.get("biological"):
        print(f"  - Biological Control: {ipm['biological']}")

    # 3. Nutrition Deficiency Engine
    print(f"\n[3. Nutrition Deficiency Engine (7-Element Canopy Spectrum)]")
    nutr_engine = NutritionDeficiencyEngine()
    nutr_res = nutr_engine.analyze(pil_img, top_disease)
    primary_def = nutr_res.get("primary_deficiency", "None")
    nutr_conf = nutr_res.get("confidence", 0.0)
    print(f"  - Primary Deficiency: {primary_def} (Severity: {nutr_conf}%)")
    if nutr_res.get("prescription", {}).get("foliar_spray"):
        print(f"  - Foliar Prescription: {nutr_res['prescription']['foliar_spray']}")
    if nutr_res.get("prescription", {}).get("soil_amendment"):
        print(f"  - Soil Amendment: {nutr_res['prescription']['soil_amendment']}")

    if save and hasattr(r, "save_dir"):
        print(f"\n[Saved Output]")
        print(f"  - Annotated bounding boxes saved to: {Path(r.save_dir).resolve()}")


def main() -> int:
    args = parse_args()

    weights_path = Path(args.weights).resolve() if args.weights else pick_weights()
    if not weights_path.exists():
        print(f"[ERROR] Weights file not found: {weights_path}")
        return 1

    print("=" * 65)
    print("🌾 PlantVision AI — Model Inference & Tri-Engine Diagnostics")
    print("=" * 65)
    print(f"- Model Weights: {weights_path.name} ({weights_path})")

    try:
        from ultralytics import YOLO
    except ImportError:
        print("[ERROR] ultralytics is required. Run: pip install ultralytics")
        return 1

    print(f"Loading YOLO model...")
    model = YOLO(str(weights_path))

    images = find_sample_images(args.source, args.num_samples)
    if not images:
        print("[ERROR] No images found to run model on.")
        print("Specify an image with: python run_model.py --source path/to/image.jpg")
        return 2

    for img in images:
        run_inference_on_image(img, model, args.conf, args.save)

    print("\n" + "=" * 65)
    print("✅ Model inference complete!")
    print("💡 To test live in the interactive web UI, visit: http://localhost:5173/scan")
    print("=" * 65)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
