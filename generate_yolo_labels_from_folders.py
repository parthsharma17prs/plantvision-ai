"""
generate_yolo_labels_from_folders.py

Turn a classification-style dataset into YOLO-style detection labels.

Assumptions:
- You already have this folder layout:
    train/<class_name>/*.jpg
    test/<class_name>/*.jpg
- Each image belongs to exactly one class (its folder name).
- We want to train YOLO to "detect" the leaf in the whole image, so we:
    - assign ONE bounding box per image that covers the full image extent
      (x_center=0.5, y_center=0.5, width=1.0, height=1.0)
    - use the folder name as the class label.

What this script does:
1) Scans `train/` and `test/` directories to collect class names.
2) Assigns a class id (0..N-1) for each class, sorted alphabetically.
3) Creates YOLO label files under `labels_src/` mirroring the split/class
   layout:
       labels_src/train/<class_name>/<image_stem>.txt
       labels_src/test/<class_name>/<image_stem>.txt
4) Writes a class mapping file `classes_mapping.txt` for reference.
5) Regenerates `data.yaml` so that:
    - `path: dataset`
    - `train/val/test` point to the prepared YOLO dataset
    - `nc` and `names` match the discovered classes.

After running this script:
- Run `dataset_preparation.py` to move data into YOLO `dataset/`.
- Then run `train_yolo.py` to train YOLOv8.
"""

from __future__ import annotations

import os
from dataclasses import dataclass
from pathlib import Path
from typing import Dict, List, Sequence

IMAGE_EXTS = {".jpg", ".jpeg", ".png", ".bmp", ".tif", ".tiff", ".webp"}


def is_image_file(p: Path) -> bool:
    return p.is_file() and p.suffix.lower() in IMAGE_EXTS


def discover_classes(split_dirs: Sequence[Path]) -> List[str]:
    """Discover class folder names across all provided split directories."""
    classes = set()
    for split_dir in split_dirs:
        if not split_dir.exists():
            continue
        for class_dir in split_dir.iterdir():
            if class_dir.is_dir():
                classes.add(class_dir.name)
    return sorted(classes)


def generate_labels_for_split(
    split_name: str,
    split_dir: Path,
    labels_root: Path,
    class_to_id: Dict[str, int],
) -> int:
    """
    Generate YOLO label files for a single split (train or test).

    Returns:
        Number of images processed for this split.
    """
    count = 0
    if not split_dir.exists():
        return 0

    for class_dir in split_dir.iterdir():
        if not class_dir.is_dir():
            continue
        class_name = class_dir.name
        if class_name not in class_to_id:
            # Skip unknown classes defensively (should not happen).
            continue
        class_id = class_to_id[class_name]

        for img_path in sorted(class_dir.iterdir()):
            if not is_image_file(img_path):
                continue

            # Full-image bounding box in YOLO normalized format
            # class_id x_center y_center width height
            label_text = f"{class_id} 0.5 0.5 1.0 1.0\n"

            dst_dir = labels_root / split_name / class_name
            dst_dir.mkdir(parents=True, exist_ok=True)
            dst_label = dst_dir / f"{img_path.stem}.txt"
            dst_label.write_text(label_text, encoding="utf-8")
            count += 1

    return count


def write_class_mapping(mapping_path: Path, classes: Sequence[str]) -> None:
    """Write class-id to name mapping for reference."""
    lines = []
    for idx, name in enumerate(classes):
        lines.append(f"{idx}\t{name}")
    mapping_path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def write_data_yaml(data_yaml_path: Path, classes: Sequence[str]) -> None:
    """
    Recreate data.yaml so that:
    - path: dataset
    - train/val/test: images/train, images/val, images/test
    - names: mapping from 0..N-1 to class names
    """
    lines = []
    lines.append("path: dataset")
    lines.append("")
    lines.append("# YOLO expects these to be paths relative to `path` (or absolute paths).")
    lines.append("train: images/train")
    lines.append("val: images/val")
    lines.append("test: images/test")
    lines.append("")
    lines.append(f"nc: {len(classes)}")
    lines.append("names:")
    for idx, name in enumerate(classes):
        # Keep the raw folder name; YOLO is fine with spaces in names.
        lines.append(f"  {idx}: {name}")
    lines.append("")

    data_yaml_path.write_text("\n".join(lines), encoding="utf-8")


def main() -> int:
    repo_root = Path.cwd()
    train_dir = repo_root / "train"
    test_dir = repo_root / "test"
    labels_root = repo_root / "labels_src"

    # Step 1: Discover class names from folder structure.
    classes = discover_classes([train_dir, test_dir])
    if not classes:
        print("ERROR: No class folders found in 'train' or 'test'.")
        return 1

    class_to_id = {name: idx for idx, name in enumerate(classes)}

    print("Discovered classes (folder names):")
    for name, idx in sorted(class_to_id.items(), key=lambda kv: kv[1]):
        print(f"- {idx}: {name}")

    # Step 2: Generate YOLO label files for train and test splits.
    labels_root.mkdir(parents=True, exist_ok=True)

    n_train = generate_labels_for_split("train", train_dir, labels_root, class_to_id)
    n_test = generate_labels_for_split("test", test_dir, labels_root, class_to_id)

    print(f"\nLabel generation complete.")
    print(f"- Output root: {labels_root}")
    print(f"- Train images labeled: {n_train}")
    print(f"- Test images labeled:  {n_test}")

    # Step 3: Write class mapping and update data.yaml
    write_class_mapping(repo_root / "classes_mapping.txt", classes)
    write_data_yaml(repo_root / "data.yaml", classes)

    print("\nFiles written:")
    print(f"- Class mapping: {repo_root / 'classes_mapping.txt'}")
    print(f"- data.yaml:     {repo_root / 'data.yaml'}")
    print("\nNext steps:")
    print("1) Prepare YOLO dataset structure using:")
    print("   python dataset_preparation.py --labels-root labels_src --skip-missing-labels --mode copy")
    print("2) Train YOLOv8 using:")
    print("   python train_yolo.py  # (defaults: epochs=50, imgsz=640)")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())

