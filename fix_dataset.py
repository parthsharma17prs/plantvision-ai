from __future__ import annotations

import argparse
import random
import shutil
from pathlib import Path
from typing import List, Tuple


IMAGE_EXTENSIONS = {".jpg", ".jpeg", ".png", ".bmp", ".tif", ".tiff", ".webp"}


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Prepare dataset into YOLO train/val/images+labels structure."
    )
    parser.add_argument(
        "--dataset-root",
        type=str,
        default="dataset",
        help="Dataset root path (default: dataset).",
    )
    parser.add_argument(
        "--split-ratio",
        type=float,
        default=0.8,
        help="Train split ratio between 0 and 1 (default: 0.8).",
    )
    parser.add_argument(
        "--seed",
        type=int,
        default=42,
        help="Random seed for reproducible shuffling (default: 42).",
    )
    parser.add_argument(
        "--no-shuffle",
        action="store_true",
        help="Disable shuffling before split.",
    )
    return parser.parse_args()


def ensure_directories(dataset_root: Path) -> dict[str, Path]:
    paths = {
        "train_images": dataset_root / "train" / "images",
        "train_labels": dataset_root / "train" / "labels",
        "val_images": dataset_root / "val" / "images",
        "val_labels": dataset_root / "val" / "labels",
    }
    for p in paths.values():
        p.mkdir(parents=True, exist_ok=True)
    return paths


def collect_images(images_dir: Path) -> List[Path]:
    return sorted([p for p in images_dir.iterdir() if p.is_file() and p.suffix.lower() in IMAGE_EXTENSIONS])


def match_image_label_pairs(images: List[Path], labels_dir: Path) -> Tuple[List[Tuple[Path, Path]], int]:
    pairs: List[Tuple[Path, Path]] = []
    missing_labels = 0
    for image_path in images:
        label_path = labels_dir / f"{image_path.stem}.txt"
        if label_path.exists():
            pairs.append((image_path, label_path))
        else:
            missing_labels += 1
    return pairs, missing_labels


def split_pairs(
    pairs: List[Tuple[Path, Path]],
    split_ratio: float,
    shuffle: bool,
    seed: int,
) -> Tuple[List[Tuple[Path, Path]], List[Tuple[Path, Path]]]:
    data = pairs[:]
    if shuffle:
        random.seed(seed)
        random.shuffle(data)

    train_count = int(len(data) * split_ratio)
    train_pairs = data[:train_count]
    val_pairs = data[train_count:]
    return train_pairs, val_pairs


def copy_pairs(pairs: List[Tuple[Path, Path]], images_out: Path, labels_out: Path) -> None:
    for image_path, label_path in pairs:
        shutil.copy2(image_path, images_out / image_path.name)
        shutil.copy2(label_path, labels_out / label_path.name)


def main() -> int:
    args = parse_args()

    if not (0.0 < args.split_ratio < 1.0):
        print("ERROR: --split-ratio must be between 0 and 1, e.g. 0.8")
        return 1

    dataset_root = Path(args.dataset_root).resolve()
    images_dir = dataset_root / "images"
    labels_dir = dataset_root / "labels"

    if not images_dir.exists() or not images_dir.is_dir():
        print(f"ERROR: Images folder not found: {images_dir}")
        return 1
    if not labels_dir.exists() or not labels_dir.is_dir():
        print(f"ERROR: Labels folder not found: {labels_dir}")
        return 1

    images = collect_images(images_dir)
    if not images:
        print(f"ERROR: No image files found in: {images_dir}")
        return 1

    pairs, missing_labels = match_image_label_pairs(images, labels_dir)
    if not pairs:
        print("ERROR: No valid image-label pairs found.")
        print("Check that each image has a matching .txt file in dataset/labels.")
        return 1

    out_dirs = ensure_directories(dataset_root)
    train_pairs, val_pairs = split_pairs(
        pairs=pairs,
        split_ratio=args.split_ratio,
        shuffle=not args.no_shuffle,
        seed=args.seed,
    )

    copy_pairs(train_pairs, out_dirs["train_images"], out_dirs["train_labels"])
    copy_pairs(val_pairs, out_dirs["val_images"], out_dirs["val_labels"])

    print("\nDataset Split Summary")
    print("---------------------")
    print(f"Total images found: {len(images)}")
    print(f"Matched image-label pairs: {len(pairs)}")
    print(f"Images skipped (missing labels): {missing_labels}")
    print(f"Train count: {len(train_pairs)}")
    print(f"Validation count: {len(val_pairs)}")
    print("\nDataset successfully prepared for YOLO training")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
