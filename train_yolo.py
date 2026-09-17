"""
train_yolo.py

Train a YOLOv8 detection model (Ultralytics) on the prepared plant disease datasets:
- PlantDoc (Object Detection with 30 classes and bounding boxes) via data_plantdoc.yaml
- PlantVillage (PlantVillage dataset with 15 classes) via data_plantvillage.yaml

Outputs / metrics:
- runs/detect/train/weights/best.pt
- Automatically updates root best.pt for app.py
"""

from __future__ import annotations

import argparse
import os
import shutil
import sys
from pathlib import Path

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
if hasattr(sys.stderr, "reconfigure"):
    sys.stderr.reconfigure(encoding="utf-8", errors="replace")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Train YOLOv8 on plant disease dataset.")
    parser.add_argument(
        "--dataset",
        type=str,
        choices=["plantdoc", "plantvillage"],
        default="plantdoc",
        help="Dataset preset: 'plantdoc' (default) or 'plantvillage'.",
    )
    parser.add_argument(
        "--data",
        type=str,
        default="",
        help="Custom path to YOLO data.yaml (overrides --dataset preset).",
    )
    parser.add_argument(
        "--model",
        type=str,
        default="yolov8n.pt",
        help="Pretrained YOLOv8 model to start from (default: yolov8n.pt).",
    )
    parser.add_argument("--epochs", type=int, default=50, help="Number of training epochs (default: 50).")
    parser.add_argument("--imgsz", type=int, default=640, help="Image size for training (default: 640).")
    parser.add_argument(
        "--batch",
        type=int,
        default=-1,
        help="Batch size. -1 lets Ultralytics auto-select (default: -1).",
    )
    parser.add_argument(
        "--device",
        type=str,
        default="",
        help='Device, e.g. "cpu" or "0" for GPU 0. Empty lets Ultralytics auto-select.',
    )
    parser.add_argument(
        "--workers",
        type=int,
        default=4,
        help="Dataloader workers (default: 4).",
    )
    parser.add_argument(
        "--quick-test",
        action="store_true",
        help="Quick smoke-test run (1 epoch, reduced images) to verify the training pipeline on CPU.",
    )
    return parser.parse_args()


def _count_images(dir_path: Path) -> int:
    """Count image files in a directory (non-recursive)."""
    exts = {".jpg", ".jpeg", ".png", ".bmp", ".tif", ".tiff", ".webp"}
    if not dir_path.exists() or not dir_path.is_dir():
        return 0
    return sum(1 for p in dir_path.iterdir() if p.is_file() and p.suffix.lower() in exts)


def _resolve_data_paths(data_yaml_path: Path) -> tuple[Path, Path, Path, Path]:
    import yaml  # provided via ultralytics dependency (PyYAML)

    data = yaml.safe_load(data_yaml_path.read_text(encoding="utf-8"))
    if not isinstance(data, dict):
        raise ValueError("Invalid data.yaml: expected a YAML mapping.")

    raw_path = str(data.get("path", "")).strip()
    if raw_path:
        dataset_root = Path(raw_path)
        if not dataset_root.is_absolute():
            dataset_root = (data_yaml_path.parent / dataset_root).resolve()
    else:
        dataset_root = data_yaml_path.parent.resolve()

    def resolve_split(key: str) -> Path:
        v = data.get(key)
        if not isinstance(v, str) or not v.strip():
            return Path()
        p = Path(v)
        return (dataset_root / p).resolve() if not p.is_absolute() else p.resolve()

    train_dir = resolve_split("train")
    val_dir = resolve_split("val")
    test_dir = resolve_split("test")
    return dataset_root, train_dir, val_dir, test_dir


def main() -> int:
    args = parse_args()

    # ---- Step 1: Resolve dataset configuration path ----
    repo_root = Path.cwd()
    if args.data:
        data_path = (repo_root / args.data).resolve()
    else:
        if args.dataset == "plantvillage":
            data_path = repo_root / "data_plantvillage.yaml"
        else:
            data_path = repo_root / "data_plantdoc.yaml"

    if not data_path.exists():
        print(f"[ERROR] Dataset configuration not found at: {data_path}")
        print("Please run `python setup_datasets.py` first to extract and generate the configs.")
        return 2

    # ---- Step 2: Validate image paths and counts ----
    try:
        dataset_root, train_dir, val_dir, test_dir = _resolve_data_paths(data_path)
    except Exception as e:
        print(f"[ERROR] Failed to parse {data_path}: {e}")
        return 3

    n_train = _count_images(train_dir)
    n_val = _count_images(val_dir)
    n_test = _count_images(test_dir) if test_dir and test_dir.exists() else 0

    if n_train == 0:
        print(f"[ERROR] No training images found in: {train_dir}")
        return 4

    print("=" * 60)
    print("🌿 PlantVision AI — YOLOv8 Training Pipeline")
    print("=" * 60)
    print(f"- Dataset Config: {data_path.name}")
    print(f"- Dataset Root:   {dataset_root}")
    print(f"- Train Images:   {n_train}")
    print(f"- Val Images:     {n_val}")
    print(f"- Test Images:    {n_test}")

    # ---- Step 3: Load pretrained model ----
    try:
        from ultralytics import YOLO
    except ImportError:
        print("[ERROR] ultralytics package is missing. Install with: pip install ultralytics")
        return 1

    print(f"\n[INFO] Loading base model: {args.model}")
    model = YOLO(args.model)

    # ---- Step 4: Configure Training Parameters ----
    epochs = 1 if args.quick_test else args.epochs
    imgsz = 320 if args.quick_test else args.imgsz
    batch = 4 if args.quick_test else args.batch

    train_kwargs = {
        "data": str(data_path).replace("\\", "/"),
        "epochs": epochs,
        "imgsz": imgsz,
        "batch": batch,
        "workers": args.workers,
        "project": "runs",
        "name": "detect/train",
        "exist_ok": True,
        "verbose": True,
        "plots": True,
    }

    if args.quick_test:
        train_kwargs["fraction"] = 0.02  # Use only 2% of images for quick pipeline validation
        print("[INFO] --quick-test active: training on 2% subset for 1 epoch.")

    if args.device.strip():
        train_kwargs["device"] = args.device.strip()

    print("\nStarting training run...")
    results = model.train(**train_kwargs)

    # ---- Step 5: Report Results and Export Weights ----
    run_dir = getattr(results, "save_dir", None)
    if run_dir is None:
        run_dir = repo_root / "runs" / "detect" / "train"
    else:
        run_dir = Path(str(run_dir))

    best_pt = run_dir / "weights" / "best.pt"
    last_pt = run_dir / "weights" / "last.pt"

    print("\n" + "=" * 60)
    print("🎉 Training process finished successfully!")
    print(f"- Run directory: {run_dir.resolve()}")
    if best_pt.exists():
        print(f"- Best weights:  {best_pt.resolve()}")
        # Copy to root best.pt for automatic pick up by app.py
        target_best = repo_root / "best.pt"
        shutil.copy2(best_pt, target_best)
        print(f"[OK] Automatically copied best.pt to project root: {target_best}")
    elif last_pt.exists():
        print(f"- Last weights:  {last_pt.resolve()}")
        target_best = repo_root / "best.pt"
        shutil.copy2(last_pt, target_best)
        print(f"[OK] Copied last.pt to project root as best.pt: {target_best}")
    print("=" * 60)

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
