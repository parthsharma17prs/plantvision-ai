"""
train_yolo.py

Train a YOLOv8 detection model (Ultralytics) on the prepared plant disease dataset.

This script:
- Installs nothing automatically (best practice), but prints the exact pip command if needed.
- Loads a pretrained YOLOv8 nano model: yolov8n.pt
- Trains using your `data.yaml`
- Uses 50 epochs and image size 640
- Saves weights to: runs/detect/train/weights/best.pt

Outputs / metrics:
- Ultralytics writes training logs and metrics into the run directory.
  Common files include:
  - runs/detect/train/results.csv
  - runs/detect/train/results.png
  - runs/detect/train/weights/best.pt
  - runs/detect/train/weights/last.pt
"""

from __future__ import annotations

import argparse
from pathlib import Path


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Train YOLOv8 on plant disease dataset.")
    parser.add_argument(
        "--data",
        type=str,
        default="data.yaml",
        help="Path to YOLO data.yaml (default: data.yaml).",
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
        default=8,
        help="Dataloader workers (default: 8; lower if you hit RAM issues).",
    )
    return parser.parse_args()


def _count_images(dir_path: Path) -> int:
    """Count image files in a directory (non-recursive)."""
    exts = {".jpg", ".jpeg", ".png", ".bmp", ".tif", ".tiff", ".webp"}
    if not dir_path.exists() or not dir_path.is_dir():
        return 0
    return sum(1 for p in dir_path.iterdir() if p.is_file() and p.suffix.lower() in exts)


def _resolve_data_paths(data_yaml_path: Path) -> tuple[Path, Path, Path, Path]:
    """
    Resolve (dataset_root, train_images_dir, val_images_dir, test_images_dir) from data.yaml.

    Ultralytics supports:
    - path: dataset_root
    - train/val/test: paths relative to dataset_root (or absolute)
    """
    import yaml  # provided via ultralytics dependency (PyYAML)

    data = yaml.safe_load(data_yaml_path.read_text(encoding="utf-8"))
    if not isinstance(data, dict):
        raise ValueError("Invalid data.yaml: expected a YAML mapping.")

    dataset_root = data_yaml_path.parent / str(data.get("path", ""))
    dataset_root = dataset_root.resolve()

    def resolve_split(key: str) -> Path:
        v = data.get(key)
        if not isinstance(v, str) or not v.strip():
            raise ValueError(f"Invalid data.yaml: missing or invalid '{key}' entry.")
        p = Path(v)
        return (dataset_root / p).resolve() if not p.is_absolute() else p.resolve()

    train_dir = resolve_split("train")
    val_dir = resolve_split("val")
    test_dir = resolve_split("test")
    return dataset_root, train_dir, val_dir, test_dir


def main() -> int:
    args = parse_args()

    # ---- Step 1: Import Ultralytics (and guide install if missing) ----
    try:
        from ultralytics import YOLO  # type: ignore
    except Exception as e:
        print("Ultralytics is not installed (or failed to import).")
        print("Install it with:")
        print("  pip install -r requirements.txt")
        print("Or directly:")
        print("  pip install ultralytics")
        print("\nImport error:")
        print(f"  {e}")
        return 1

    # ---- Step 2: Validate paths ----
    repo_root = Path.cwd()
    data_path = (repo_root / args.data).resolve()
    if not data_path.exists():
        print(f"ERROR: data.yaml not found at: {data_path}")
        return 2

    # Validate that the YOLO dataset folders actually contain images before we start training.
    # This prevents a long stack trace and gives a clear actionable error.
    try:
        dataset_root, train_dir, val_dir, test_dir = _resolve_data_paths(data_path)
    except Exception as e:
        print("ERROR: Failed to parse/resolve paths from data.yaml.")
        print(f"- data.yaml: {data_path}")
        print(f"- reason:   {e}")
        return 3

    n_train = _count_images(train_dir)
    n_val = _count_images(val_dir)
    n_test = _count_images(test_dir)
    if n_train == 0:
        print("ERROR: No training images found. YOLO expects images in:")
        print(f"- {train_dir}")
        print("\nFix:")
        print("- Run dataset preparation AFTER you have YOLO label .txt files, so it can populate")
        print("  dataset/images/train and dataset/labels/train with paired data.")
        print("- Or point your data.yaml to the correct prepared dataset location.")
        return 4

    print("Dataset check:")
    print(f"- dataset root: {dataset_root}")
    print(f"- train images: {train_dir} ({n_train})")
    print(f"- val images:   {val_dir} ({n_val})")
    print(f"- test images:  {test_dir} ({n_test})")

    # ---- Step 3: Load pretrained model ----
    # If `args.model` is a filename like "yolov8n.pt", Ultralytics will download it automatically.
    print(f"Loading pretrained model: {args.model}")
    model = YOLO(args.model)

    # ---- Step 4: Train ----
    # Progress logging + metrics:
    # - Ultralytics prints a live progress table to stdout while training
    # - It also writes results to: runs/detect/train/results.csv (and other artifacts)
    #
    # We set project/name so the output path matches your requested location:
    #   runs/detect/train/weights/best.pt
    train_kwargs = {
        "data": str(data_path),
        "epochs": int(args.epochs),
        "imgsz": int(args.imgsz),
        "batch": int(args.batch),
        "workers": int(args.workers),
        # Ultralytics creates output as: <project>/<name>/...
        # Set these so the final path is: runs/detect/train/weights/best.pt
        "project": "runs",
        "name": "detect/train",
        "exist_ok": True,  # reuse the folder if you re-run training
        "verbose": True,
        "plots": True,  # saves metric plots into the run directory
    }
    if args.device.strip():
        train_kwargs["device"] = args.device.strip()

    print("\nStarting training with settings:")
    for k in sorted(train_kwargs.keys()):
        print(f"- {k}: {train_kwargs[k]}")

    results = model.train(**train_kwargs)

    # ---- Step 5: Report key artifacts/metrics ----
    run_dir = getattr(results, "save_dir", None)
    if run_dir is None:
        # Ultralytics should always set save_dir; keep a safe fallback.
        run_dir = Path("runs/detect/train")
    else:
        run_dir = Path(str(run_dir))

    best_pt = run_dir / "weights" / "best.pt"
    last_pt = run_dir / "weights" / "last.pt"
    results_csv = run_dir / "results.csv"

    print("\nTraining complete.")
    print(f"- Run directory: {run_dir.resolve()}")
    print(f"- Best weights:  {best_pt.resolve()}{' (missing!)' if not best_pt.exists() else ''}")
    print(f"- Last weights:  {last_pt.resolve()}{' (missing!)' if not last_pt.exists() else ''}")
    print(f"- Metrics CSV:   {results_csv.resolve()}{' (missing!)' if not results_csv.exists() else ''}")

    # Some useful metrics are available on `results` depending on Ultralytics version.
    # We print what’s safely accessible without assuming exact attribute names.
    metrics = getattr(results, "results_dict", None)
    if callable(metrics):
        try:
            md = metrics()
            if isinstance(md, dict) and md:
                print("\nFinal metrics snapshot (from Ultralytics):")
                for k in sorted(md.keys()):
                    print(f"- {k}: {md[k]}")
        except Exception:
            pass

    return 0


if __name__ == "__main__":
    raise SystemExit(main())

