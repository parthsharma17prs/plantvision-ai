#!/usr/bin/env python3
"""
setup_datasets.py

Prepares and configures plant disease datasets for YOLOv8 training:
1. PlantDoc:
   - Source: C:\\Users\\VINOD SHARMA\\Downloads\\archive (1)  (or archive (1).zip fallback)
   - Target: datasets/plantdoc/
   - Config: data_plantdoc.yaml (30 classes, real-world field lesion bounding boxes)

2. PlantVillage:
   - Source: C:\\Users\\VINOD SHARMA\\Downloads\\archive\\PlantVillage (or archive.zip fallback)
   - Target: datasets/plantvillage/
   - Config: data_plantvillage.yaml (15 classes, laboratory single-leaf detection)

3. Combined (Unified):
   - Merges PlantDoc + balanced PlantVillage into a unified 31-class dataset.
   - Target: datasets/combined/
   - Config: data_combined.yaml
"""

from __future__ import annotations

import argparse
import os
import random
import shutil
import sys
import zipfile
from pathlib import Path

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
if hasattr(sys.stderr, "reconfigure"):
    sys.stderr.reconfigure(encoding="utf-8", errors="replace")

ROOT = Path(__file__).resolve().parent
DATASETS_DIR = ROOT / "datasets"
PLANTDOC_DIR = DATASETS_DIR / "plantdoc"
PLANTVILLAGE_DIR = DATASETS_DIR / "plantvillage"
COMBINED_DIR = DATASETS_DIR / "combined"

DEFAULT_DIR_PLANTDOC = Path(r"C:\Users\VINOD SHARMA\Downloads\archive (1)")
DEFAULT_ZIP_PLANTDOC = Path(r"C:\Users\VINOD SHARMA\Downloads\archive (1).zip")

DEFAULT_DIR_PLANTVILLAGE = Path(r"C:\Users\VINOD SHARMA\Downloads\archive\PlantVillage")
DEFAULT_ZIP_PLANTVILLAGE = Path(r"C:\Users\VINOD SHARMA\Downloads\archive.zip")

PLANTDOC_CLASSES = [
    "Apple Scab Leaf",
    "Apple leaf",
    "Apple rust leaf",
    "Bell_pepper leaf spot",
    "Bell_pepper leaf",
    "Blueberry leaf",
    "Cherry leaf",
    "Corn Gray leaf spot",
    "Corn leaf blight",
    "Corn rust leaf",
    "Peach leaf",
    "Potato leaf early blight",
    "Potato leaf late blight",
    "Potato leaf",
    "Raspberry leaf",
    "Soyabean leaf",
    "Soybean leaf",
    "Squash Powdery mildew leaf",
    "Strawberry leaf",
    "Tomato Early blight leaf",
    "Tomato Septoria leaf spot",
    "Tomato leaf bacterial spot",
    "Tomato leaf late blight",
    "Tomato leaf mosaic virus",
    "Tomato leaf yellow virus",
    "Tomato leaf",
    "Tomato mold leaf",
    "Tomato two spotted spider mites leaf",
    "grape leaf black rot",
    "grape leaf",
]

# PlantVillage classes discovered in dataset
PLANTVILLAGE_CLASSES = [
    "Pepper__bell___Bacterial_spot",
    "Pepper__bell___healthy",
    "Potato___Early_blight",
    "Potato___Late_blight",
    "Potato___healthy",
    "Tomato_Bacterial_spot",
    "Tomato_Early_blight",
    "Tomato_Late_blight",
    "Tomato_Leaf_Mold",
    "Tomato_Septoria_leaf_spot",
    "Tomato_Spider_mites_Two_spotted_spider_mite",
    "Tomato__Target_Spot",
    "Tomato__Tomato_YellowLeaf__Curl_Virus",
    "Tomato__Tomato_mosaic_virus",
    "Tomato_healthy",
]

# Mapping from PlantVillage class names to unified class names
PV_TO_UNIFIED_MAP: dict[str, str] = {
    "Pepper__bell___Bacterial_spot": "Bell_pepper leaf spot",
    "Pepper__bell___healthy": "Bell_pepper leaf",
    "Potato___Early_blight": "Potato leaf early blight",
    "Potato___Late_blight": "Potato leaf late blight",
    "Potato___healthy": "Potato leaf",
    "Tomato_Bacterial_spot": "Tomato leaf bacterial spot",
    "Tomato_Early_blight": "Tomato Early blight leaf",
    "Tomato_Late_blight": "Tomato leaf late blight",
    "Tomato_Leaf_Mold": "Tomato mold leaf",
    "Tomato_Septoria_leaf_spot": "Tomato Septoria leaf spot",
    "Tomato_Spider_mites_Two_spotted_spider_mite": "Tomato two spotted spider mites leaf",
    "Tomato__Target_Spot": "Tomato Target Spot",
    "Tomato__Tomato_YellowLeaf__Curl_Virus": "Tomato leaf yellow virus",
    "Tomato__Tomato_mosaic_virus": "Tomato leaf mosaic virus",
    "Tomato_healthy": "Tomato leaf",
}

# Unified 31 classes (30 PlantDoc + 1 new PlantVillage: "Tomato Target Spot")
UNIFIED_CLASSES = list(PLANTDOC_CLASSES) + ["Tomato Target Spot"]


def setup_plantdoc(src_dir: Path | None = None, src_zip: Path | None = None) -> None:
    print("\n" + "=" * 60)
    print("[1/3] Processing PlantDoc Dataset...")
    print("=" * 60)

    dir_src = src_dir or DEFAULT_DIR_PLANTDOC
    zip_src = src_zip or DEFAULT_ZIP_PLANTDOC

    PLANTDOC_DIR.mkdir(parents=True, exist_ok=True)

    train_imgs = list((PLANTDOC_DIR / "train" / "images").glob("*.*")) if (PLANTDOC_DIR / "train" / "images").exists() else []

    if len(train_imgs) >= 1900:
        print(f"[OK] Existing PlantDoc found in {PLANTDOC_DIR} ({len(train_imgs)} train images).")
    elif dir_src.exists() and (dir_src / "train" / "images").exists():
        print(f"Syncing PlantDoc directly from folder: {dir_src}...")
        for split in ["train", "valid", "test"]:
            for sub in ["images", "labels"]:
                src_split = dir_src / split / sub
                dst_split = PLANTDOC_DIR / split / sub
                dst_split.mkdir(parents=True, exist_ok=True)
                if src_split.exists():
                    for f in src_split.iterdir():
                        if f.is_file():
                            dst_f = dst_split / f.name
                            if not dst_f.exists():
                                shutil.copy2(f, dst_f)
    elif zip_src.exists():
        print(f"Extracting PlantDoc from zip: {zip_src}...")
        with zipfile.ZipFile(zip_src, "r") as zf:
            zf.extractall(PLANTDOC_DIR)
    else:
        print(f"[WARNING] Neither {dir_src} nor {zip_src} found. Checking existing directory...")

    dataset_path_str = str(PLANTDOC_DIR.resolve()).replace("\\", "/")
    yaml_content = f"""# PlantDoc YOLOv8 Object Detection Dataset Configuration
# Generated by setup_datasets.py

path: {dataset_path_str}
train: train/images
val: valid/images
test: test/images

nc: {len(PLANTDOC_CLASSES)}
names:
"""
    for idx, cname in enumerate(PLANTDOC_CLASSES):
        yaml_content += f"  {idx}: {cname}\n"

    (ROOT / "data_plantdoc.yaml").write_text(yaml_content, encoding="utf-8")
    (PLANTDOC_DIR / "data.yaml").write_text(yaml_content, encoding="utf-8")

    train_c = len(list((PLANTDOC_DIR / "train" / "images").glob("*.*"))) if (PLANTDOC_DIR / "train" / "images").exists() else 0
    val_c = len(list((PLANTDOC_DIR / "valid" / "images").glob("*.*"))) if (PLANTDOC_DIR / "valid" / "images").exists() else 0
    test_c = len(list((PLANTDOC_DIR / "test" / "images").glob("*.*"))) if (PLANTDOC_DIR / "test" / "images").exists() else 0
    print(f"[OK] data_plantdoc.yaml ready. Verified: {train_c} train, {val_c} valid, {test_c} test images.")


def setup_plantvillage(src_dir: Path | None = None, src_zip: Path | None = None) -> None:
    print("\n" + "=" * 60)
    print("[2/3] Processing PlantVillage Dataset...")
    print("=" * 60)

    dir_src = src_dir or DEFAULT_DIR_PLANTVILLAGE
    zip_src = src_zip or DEFAULT_ZIP_PLANTVILLAGE

    PLANTVILLAGE_DIR.mkdir(parents=True, exist_ok=True)
    raw_images_dir = PLANTVILLAGE_DIR / "raw"
    raw_images_dir.mkdir(parents=True, exist_ok=True)

    # Ingest raw images
    if dir_src.exists():
        print(f"Reading PlantVillage classes directly from folder: {dir_src}...")
        for cdir in sorted(dir_src.iterdir()):
            if not cdir.is_dir() or cdir.name.startswith(".") or cdir.name == "PlantVillage":
                continue
            target_cdir = raw_images_dir / cdir.name
            target_cdir.mkdir(parents=True, exist_ok=True)
            for f in cdir.iterdir():
                if f.is_file() and f.suffix.lower() in {".jpg", ".jpeg", ".png"}:
                    dst_f = target_cdir / f.name
                    if not dst_f.exists():
                        shutil.copy2(f, dst_f)
    elif zip_src.exists():
        print(f"Extracting PlantVillage from zip: {zip_src}...")
        with zipfile.ZipFile(zip_src, "r") as zf:
            for m in zf.infolist():
                name = m.filename
                if not name.startswith("PlantVillage/") or name.endswith("/"):
                    continue
                rel_path = name[len("PlantVillage/"):]
                if not rel_path or rel_path.startswith("svn-"):
                    continue
                target_file = raw_images_dir / rel_path
                target_file.parent.mkdir(parents=True, exist_ok=True)
                with zf.open(m) as src, open(target_file, "wb") as dst:
                    shutil.copyfileobj(src, dst)

    classes = sorted([d.name for d in raw_images_dir.iterdir() if d.is_dir() and not d.name.startswith(".")])
    print(f"Discovered {len(classes)} PlantVillage classes: {classes}")

    print("Generating train/val splits and YOLO annotations for PlantVillage...")
    train_img_dir = PLANTVILLAGE_DIR / "train" / "images"
    train_lbl_dir = PLANTVILLAGE_DIR / "train" / "labels"
    val_img_dir = PLANTVILLAGE_DIR / "val" / "images"
    val_lbl_dir = PLANTVILLAGE_DIR / "val" / "labels"

    for d in [train_img_dir, train_lbl_dir, val_img_dir, val_lbl_dir]:
        d.mkdir(parents=True, exist_ok=True)

    random.seed(42)
    class_to_id = {c: i for i, c in enumerate(classes)}
    total_train = 0
    total_val = 0

    for cname in classes:
        cdir = raw_images_dir / cname
        imgs = sorted([f for f in cdir.iterdir() if f.is_file() and f.suffix.lower() in {".jpg", ".jpeg", ".png"}])
        random.shuffle(imgs)

        split_idx = int(len(imgs) * 0.8)
        train_imgs = imgs[:split_idx]
        val_imgs = imgs[split_idx:]

        cid = class_to_id[cname]
        bbox_line = f"{cid} 0.5 0.5 1.0 1.0\n"

        for f in train_imgs:
            dst_img = train_img_dir / f"{cname}_{f.name}"
            dst_lbl = train_lbl_dir / f"{cname}_{f.stem}.txt"
            if not dst_img.exists():
                shutil.copy2(f, dst_img)
            dst_lbl.write_text(bbox_line, encoding="utf-8")
            total_train += 1

        for f in val_imgs:
            dst_img = val_img_dir / f"{cname}_{f.name}"
            dst_lbl = val_lbl_dir / f"{cname}_{f.stem}.txt"
            if not dst_img.exists():
                shutil.copy2(f, dst_img)
            dst_lbl.write_text(bbox_line, encoding="utf-8")
            total_val += 1

    dataset_pv_path = str(PLANTVILLAGE_DIR.resolve()).replace("\\", "/")
    yaml_pv = f"""# PlantVillage YOLOv8 Detection Dataset Configuration
# Generated by setup_datasets.py

path: {dataset_pv_path}
train: train/images
val: val/images

nc: {len(classes)}
names:
"""
    for idx, cname in enumerate(classes):
        yaml_pv += f"  {idx}: {cname}\n"

    (ROOT / "data_plantvillage.yaml").write_text(yaml_pv, encoding="utf-8")
    (PLANTVILLAGE_DIR / "data.yaml").write_text(yaml_pv, encoding="utf-8")
    print(f"[OK] PlantVillage prepared: {total_train} train, {total_val} val images across {len(classes)} classes.")
    print("[OK] data_plantvillage.yaml created successfully!")


def setup_combined(max_pv_per_class: int = 350) -> None:
    print("\n" + "=" * 60)
    print(f"[3/3] Generating Unified Combined Dataset (max {max_pv_per_class} PlantVillage images/class)...")
    print("=" * 60)

    COMBINED_DIR.mkdir(parents=True, exist_ok=True)
    c_train_img = COMBINED_DIR / "train" / "images"
    c_train_lbl = COMBINED_DIR / "train" / "labels"
    c_val_img = COMBINED_DIR / "val" / "images"
    c_val_lbl = COMBINED_DIR / "val" / "labels"

    for d in [c_train_img, c_train_lbl, c_val_img, c_val_lbl]:
        d.mkdir(parents=True, exist_ok=True)

    unified_name_to_id = {name: idx for idx, name in enumerate(UNIFIED_CLASSES)}
    plantdoc_id_to_name = {idx: name for idx, name in enumerate(PLANTDOC_CLASSES)}

    copied_train = 0
    copied_val = 0

    # 1. Ingest all PlantDoc train & valid images and labels
    print("1. Merging PlantDoc real-world field images...")
    for split, out_img_dir, out_lbl_dir in [
        ("train", c_train_img, c_train_lbl),
        ("valid", c_val_img, c_val_lbl),
    ]:
        src_img_dir = PLANTDOC_DIR / split / "images"
        src_lbl_dir = PLANTDOC_DIR / split / "labels"
        if not src_img_dir.exists():
            continue

        for img_f in src_img_dir.iterdir():
            if not img_f.is_file() or img_f.suffix.lower() not in {".jpg", ".jpeg", ".png"}:
                continue
            lbl_f = src_lbl_dir / f"{img_f.stem}.txt"
            dst_img = out_img_dir / f"pdoc_{img_f.name}"
            dst_lbl = out_lbl_dir / f"pdoc_{img_f.stem}.txt"

            if not dst_img.exists():
                shutil.copy2(img_f, dst_img)

            if lbl_f.exists():
                new_lines = []
                for line in lbl_f.read_text(encoding="utf-8", errors="replace").splitlines():
                    parts = line.strip().split()
                    if not parts:
                        continue
                    old_id = int(parts[0])
                    cname = plantdoc_id_to_name.get(old_id, "")
                    if cname in unified_name_to_id:
                        new_id = unified_name_to_id[cname]
                        new_lines.append(f"{new_id} " + " ".join(parts[1:]))
                dst_lbl.write_text("\n".join(new_lines) + "\n", encoding="utf-8")
            else:
                dst_lbl.write_text("", encoding="utf-8")

            if split == "train":
                copied_train += 1
            else:
                copied_val += 1

    print(f"   -> Added PlantDoc: {copied_train} train, {copied_val} val.")

    # 2. Ingest balanced sample from PlantVillage raw images
    raw_pv = PLANTVILLAGE_DIR / "raw"
    pv_train_added = 0
    pv_val_added = 0
    if raw_pv.exists():
        print(f"2. Merging balanced PlantVillage images (up to {max_pv_per_class} per class)...")
        random.seed(42)
        for pv_class_dir in sorted(raw_pv.iterdir()):
            if not pv_class_dir.is_dir() or pv_class_dir.name.startswith("."):
                continue
            pv_cname = pv_class_dir.name
            unified_cname = PV_TO_UNIFIED_MAP.get(pv_cname, pv_cname)
            if unified_cname not in unified_name_to_id:
                continue
            unified_id = unified_name_to_id[unified_cname]

            all_imgs = sorted([f for f in pv_class_dir.iterdir() if f.is_file() and f.suffix.lower() in {".jpg", ".jpeg", ".png"}])
            random.shuffle(all_imgs)
            sample_imgs = all_imgs[:max_pv_per_class]

            split_pt = int(len(sample_imgs) * 0.8)
            train_sample = sample_imgs[:split_pt]
            val_sample = sample_imgs[split_pt:]

            bbox_line = f"{unified_id} 0.5 0.5 1.0 1.0\n"

            for img_f in train_sample:
                dst_img = c_train_img / f"pv_{pv_cname}_{img_f.name}"
                dst_lbl = c_train_lbl / f"pv_{pv_cname}_{img_f.stem}.txt"
                if not dst_img.exists():
                    shutil.copy2(img_f, dst_img)
                dst_lbl.write_text(bbox_line, encoding="utf-8")
                pv_train_added += 1

            for img_f in val_sample:
                dst_img = c_val_img / f"pv_{pv_cname}_{img_f.name}"
                dst_lbl = c_val_lbl / f"pv_{pv_cname}_{img_f.stem}.txt"
                if not dst_img.exists():
                    shutil.copy2(img_f, dst_img)
                dst_lbl.write_text(bbox_line, encoding="utf-8")
                pv_val_added += 1

        print(f"   -> Added PlantVillage: {pv_train_added} train, {pv_val_added} val.")

    comb_path_str = str(COMBINED_DIR.resolve()).replace("\\", "/")
    yaml_comb = f"""# PlantVision AI Combined (PlantDoc + PlantVillage) Unified Dataset Configuration
# Generated by setup_datasets.py

path: {comb_path_str}
train: train/images
val: val/images

nc: {len(UNIFIED_CLASSES)}
names:
"""
    for idx, cname in enumerate(UNIFIED_CLASSES):
        yaml_comb += f"  {idx}: {cname}\n"

    (ROOT / "data_combined.yaml").write_text(yaml_comb, encoding="utf-8")
    (COMBINED_DIR / "data.yaml").write_text(yaml_comb, encoding="utf-8")

    tot_train = copied_train + pv_train_added
    tot_val = copied_val + pv_val_added
    print(f"[OK] Combined dataset ready: {tot_train} train, {tot_val} val images across {len(UNIFIED_CLASSES)} unified classes.")
    print("[OK] data_combined.yaml created successfully!")


def main() -> None:
    parser = argparse.ArgumentParser(description="PlantVision AI Dataset Setup Pipeline")
    parser.add_argument("--plantdoc-dir", type=str, default="", help="Path to PlantDoc folder")
    parser.add_argument("--plantvillage-dir", type=str, default="", help="Path to PlantVillage folder")
    parser.add_argument("--skip-combined", action="store_true", help="Skip building combined dataset")
    parser.add_argument("--max-pv-per-class", type=int, default=350, help="Max PlantVillage images per class in combined set")
    args = parser.parse_args()

    pdoc_dir = Path(args.plantdoc_dir) if args.plantdoc_dir else None
    pv_dir = Path(args.plantvillage_dir) if args.plantvillage_dir else None

    print("=" * 60)
    print("🌿 PlantVision AI — Dataset Ingestion & Preparation Pipeline")
    print("=" * 60)
    print(f"PlantDoc Source:    {pdoc_dir or DEFAULT_DIR_PLANTDOC}")
    print(f"PlantVillage Source:{pv_dir or DEFAULT_DIR_PLANTVILLAGE}")

    setup_plantdoc(src_dir=pdoc_dir)
    setup_plantvillage(src_dir=pv_dir)

    if not args.skip_combined:
        setup_combined(max_pv_per_class=args.max_pv_per_class)

    print("\n" + "=" * 60)
    print("🎉 Dataset Setup Complete! Available Configurations:")
    print("  1. data_plantdoc.yaml    -> 30 classes (Real-world field images)")
    print("  2. data_plantvillage.yaml-> 15 classes (High-resolution lab foliar images)")
    print("  3. data_combined.yaml    -> 31 classes (Unified merged multi-crop dataset)")
    print("=" * 60)


if __name__ == "__main__":
    main()
