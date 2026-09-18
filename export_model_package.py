#!/usr/bin/env python3
"""
export_model_package.py

Bundles everything an ML / Computer Vision expert needs to audit and test the model:
1. Model weights (best.pt)
2. Model specification & audit report (MODEL_CARD.md)
3. Dataset configuration & class mapping (data_plantdoc.yaml)
4. Model inference & evaluation runner (run_model.py)
5. Tri-Engine sub-modules (pest_adapter.py, nutrition_engine.py)
6. Metric plots & curves (PR curve, F1 curve, confusion matrix, loss charts)
7. Sample test leaf images
Outputs: PlantVision_Model_Export.zip
"""

import os
import zipfile
from pathlib import Path

ROOT = Path(__file__).resolve().parent
EXPORT_ZIP = ROOT / "PlantVision_Model_Export.zip"


def create_package():
    print(f"[1/3] Gathering expert package files...")
    files_to_pack = [
        ROOT / "best.pt",
        ROOT / "MODEL_CARD.md",
        ROOT / "data_plantdoc.yaml",
        ROOT / "data_plantvillage.yaml",
        ROOT / "data_combined.yaml",
        ROOT / "run_model.py",
        ROOT / "pest_adapter.py",
        ROOT / "nutrition_engine.py",
    ]

    plots_dir = ROOT / "runs" / "detect" / "train"
    sample_images_dir = ROOT / "datasets" / "plantdoc" / "test" / "images"

    with zipfile.ZipFile(EXPORT_ZIP, "w", zipfile.ZIP_DEFLATED) as zf:
        # Core model files
        for f in files_to_pack:
            if f.exists():
                print(f"  + {f.name}")
                zf.write(f, arcname=f.name)

        # Evaluation plots
        if plots_dir.exists():
            print(f"  + Evaluation curves & confusion matrices:")
            for p in plots_dir.glob("*.*"):
                if p.suffix.lower() in [".png", ".jpg", ".csv"]:
                    print(f"    - evaluation_plots/{p.name}")
                    zf.write(p, arcname=f"evaluation_plots/{p.name}")

        # Sample test images (5 samples)
        if sample_images_dir.exists():
            samples = list(sample_images_dir.glob("*.jpg"))[:6]
            print(f"  + Sample test leaf images:")
            for s in samples:
                print(f"    - sample_images/{s.name}")
                zf.write(s, arcname=f"sample_images/{s.name}")

    sz_mb = EXPORT_ZIP.stat().st_size / (1024 * 1024)
    print(f"\n[2/3] Package created successfully!")
    print(f"  File: {EXPORT_ZIP.resolve()}")
    print(f"  Size: {sz_mb:.2f} MB")
    print(f"\n[3/3] Ready to share with your ML/AI expert!")


if __name__ == "__main__":
    create_package()
