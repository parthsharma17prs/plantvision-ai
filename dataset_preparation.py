from __future__ import annotations

import argparse
import json
import os
import random
import shutil
from dataclasses import dataclass
from pathlib import Path
from typing import Dict, Iterable, List, Optional, Sequence, Tuple


IMAGE_EXTS = {".jpg", ".jpeg", ".png", ".bmp", ".tif", ".tiff", ".webp"}


@dataclass(frozen=True)
class Item:
    """One image and its optional corresponding label file."""

    image_path: Path
    class_name: str
    label_path: Optional[Path]

    @property
    def stem(self) -> str:
        return self.image_path.stem


def is_image_file(p: Path) -> bool:
    return p.is_file() and p.suffix.lower() in IMAGE_EXTS


def discover_class_folders(source_dir: Path) -> List[Path]:
    """Return immediate subdirectories (class folders) under source_dir."""
    if not source_dir.exists():
        return []
    return sorted([p for p in source_dir.iterdir() if p.is_dir()])


def find_label_for_image(
    image_path: Path,
    labels_root: Optional[Path],
    class_name: str,
    split_name: Optional[str] = None,
) -> Optional[Path]:
    """
    Find the label file corresponding to an image.

    Search strategy (first match wins):
    - If labels_root is not provided, look next to the image: <image_stem>.txt
    - If labels_root is provided, try common layouts:
        1) labels_root/<class_name>/<image_stem>.txt
        2) labels_root/<split>/<class_name>/<image_stem>.txt   (when split_name is given)
        3) labels_root/<image_stem>.txt
        4) labels_root/.../ (recursive search avoided for speed and determinism)
    """
    candidate_names = [image_path.with_suffix(".txt").name]

    # 1) Next to the image (common when images+labels are co-located)
    if labels_root is None:
        direct = image_path.with_suffix(".txt")
        return direct if direct.exists() else None

    # 2) labels_root/<class>/<stem>.txt (mirrors class-subfolder layout)
    class_candidate = labels_root / class_name / candidate_names[0]
    if class_candidate.exists():
        return class_candidate

    # 3) labels_root/<split>/<class>/<stem>.txt (e.g. labels_src/train/<class>/<stem>.txt)
    if split_name is not None:
        split_class_candidate = labels_root / split_name / class_name / candidate_names[0]
        if split_class_candidate.exists():
            return split_class_candidate

    # 4) labels_root/<stem>.txt (flat labels directory)
    flat_candidate = labels_root / candidate_names[0]
    if flat_candidate.exists():
        return flat_candidate

    return None


def scan_items(source_dirs: Sequence[Path], labels_root: Optional[Path]) -> List[Item]:
    """
    Scan source directories that contain class-subfolder layout:
      source_dir/<class_name>/*.jpg
    """
    items: List[Item] = []

    for source_dir in source_dirs:
        split_name = source_dir.name  # e.g. "train" or "test"
        for class_dir in discover_class_folders(source_dir):
            class_name = class_dir.name
            for p in sorted(class_dir.iterdir()):
                if not is_image_file(p):
                    continue
                label = find_label_for_image(
                    p,
                    labels_root=labels_root,
                    class_name=class_name,
                    split_name=split_name,
                )
                items.append(Item(image_path=p, class_name=class_name, label_path=label))

    return items


def split_items(
    items: Sequence[Item],
    train_ratio: float,
    val_ratio: float,
    test_ratio: float,
    seed: int,
) -> Tuple[List[Item], List[Item], List[Item]]:
    """Shuffle and split items into train/val/test with requested ratios."""
    if not items:
        return [], [], []

    total = train_ratio + val_ratio + test_ratio
    if total <= 0:
        raise ValueError("Split ratios must sum to a positive number.")

    train_r = train_ratio / total
    val_r = val_ratio / total

    rng = random.Random(seed)
    shuffled = list(items)
    rng.shuffle(shuffled)

    n = len(shuffled)
    n_train = int(round(n * train_r))
    n_val = int(round(n * val_r))

    # Ensure we don't exceed n, and keep deterministic sizing
    n_train = max(0, min(n, n_train))
    n_val = max(0, min(n - n_train, n_val))
    n_test = n - n_train - n_val

    train_items = shuffled[:n_train]
    val_items = shuffled[n_train : n_train + n_val]
    test_items = shuffled[n_train + n_val :]
    assert len(train_items) + len(val_items) + len(test_items) == n

    return train_items, val_items, test_items


def ensure_yolo_dirs(dataset_root: Path) -> Dict[str, Path]:
    """Create YOLO folder structure and return paths."""
    paths = {
        "images_train": dataset_root / "images" / "train",
        "images_val": dataset_root / "images" / "val",
        "images_test": dataset_root / "images" / "test",
        "labels_train": dataset_root / "labels" / "train",
        "labels_val": dataset_root / "labels" / "val",
        "labels_test": dataset_root / "labels" / "test",
    }
    for p in paths.values():
        p.mkdir(parents=True, exist_ok=True)
    return paths


def safe_name(name: str) -> str:
    """Make filenames safer by replacing path-unfriendly characters."""
    return "".join(c if c.isalnum() or c in ("-", "_", ".") else "_" for c in name)


def destination_basename(item: Item) -> str:
    """
    Create a destination basename that avoids collisions across classes.

    Example:
      class = "Apple leaf", stem = "image_12" -> "Apple_leaf__image_12"
    """
    cls = safe_name(item.class_name.replace(" ", "_"))
    stem = safe_name(item.stem)
    return f"{cls}__{stem}"


def transfer_file(src: Path, dst: Path, mode: str, dry_run: bool) -> None:
    dst.parent.mkdir(parents=True, exist_ok=True)
    if dry_run:
        return
    if mode == "move":
        shutil.move(str(src), str(dst))
    elif mode == "copy":
        shutil.copy2(str(src), str(dst))
    else:
        raise ValueError(f"Unknown mode: {mode}")


def place_items(
    items: Sequence[Item],
    split_name: str,
    yolo_paths: Dict[str, Path],
    mode: str,
    dry_run: bool,
) -> None:
    """Move/copy image+label files into YOLO split folders."""
    img_dst_dir = yolo_paths[f"images_{split_name}"]
    lbl_dst_dir = yolo_paths[f"labels_{split_name}"]

    for item in items:
        base = destination_basename(item)
        img_dst = img_dst_dir / f"{base}{item.image_path.suffix.lower()}"
        transfer_file(item.image_path, img_dst, mode=mode, dry_run=dry_run)

        # Label path is guaranteed present for items passed here
        assert item.label_path is not None
        lbl_dst = lbl_dst_dir / f"{base}.txt"
        transfer_file(item.label_path, lbl_dst, mode=mode, dry_run=dry_run)


def build_report(items: Sequence[Item]) -> Dict[str, object]:
    """Build a JSON-serializable report about the dataset scan."""
    total = len(items)
    with_label = sum(1 for it in items if it.label_path is not None)
    missing = [str(it.image_path) for it in items if it.label_path is None]

    by_class: Dict[str, Dict[str, int]] = {}
    for it in items:
        d = by_class.setdefault(it.class_name, {"total": 0, "with_label": 0, "missing_label": 0})
        d["total"] += 1
        if it.label_path is None:
            d["missing_label"] += 1
        else:
            d["with_label"] += 1

    return {
        "total_images_found": total,
        "images_with_labels": with_label,
        "images_missing_labels": total - with_label,
        "missing_label_images": missing[:2000],  # cap to keep file manageable
        "by_class": dict(sorted(by_class.items(), key=lambda kv: kv[0].lower())),
    }


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Prepare dataset into YOLO format.")

    parser.add_argument(
        "--source-dirs",
        nargs="+",
        default=["train", "test"],
        help="Source directories that contain class subfolders (default: train test).",
    )
    parser.add_argument(
        "--labels-root",
        default=None,
        help="Optional root directory containing YOLO label .txt files.",
    )
    parser.add_argument(
        "--output-dir",
        default="dataset",
        help="Output YOLO dataset root directory (default: dataset).",
    )
    parser.add_argument("--train", type=float, default=0.7, help="Train split ratio (default: 0.7).")
    parser.add_argument("--val", type=float, default=0.2, help="Validation split ratio (default: 0.2).")
    parser.add_argument("--test", type=float, default=0.1, help="Test split ratio (default: 0.1).")
    parser.add_argument("--seed", type=int, default=42, help="Random seed for reproducible splits.")

    parser.add_argument(
        "--mode",
        choices=["move", "copy"],
        default="move",
        help="Whether to move or copy files into YOLO structure (default: move).",
    )
    parser.add_argument(
        "--skip-missing-labels",
        action="store_true",
        help="If set, images without labels are skipped instead of failing.",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="If set, only prints summary and creates folders; does not move/copy.",
    )

    return parser.parse_args()


def main() -> int:
    args = parse_args()

    repo_root = Path.cwd()
    source_dirs = [repo_root / d for d in args.source_dirs]
    labels_root = Path(args.labels_root).resolve() if args.labels_root else None
    output_dir = (repo_root / args.output_dir).resolve()

    # Step 1: Scan dataset items (images + their label counterparts).
    items = scan_items(source_dirs=source_dirs, labels_root=labels_root)

    # Step 2: Ensure the YOLO folder structure exists (this "verifies" the expected layout
    # and creates it if missing).
    yolo_paths = ensure_yolo_dirs(output_dir)

    # Step 3: Report missing labels and decide whether to proceed.
    report = build_report(items)
    report_path = repo_root / "dataset_preparation_report.json"
    # Always write the scan report (even in --dry-run) so you can inspect missing labels.
    report_path.write_text(json.dumps(report, indent=2), encoding="utf-8")

    missing_count = int(report["images_missing_labels"])  # type: ignore[assignment]
    if missing_count > 0 and not args.skip_missing_labels:
        print("ERROR: Some images are missing corresponding label files.")
        print(f"- Total images found: {report['total_images_found']}")
        print(f"- Images with labels:  {report['images_with_labels']}")
        print(f"- Missing labels:      {report['images_missing_labels']}")
        print(f"See report for paths: {report_path}")
        return 2

    # Step 4: Keep only fully-paired items for YOLO training.
    paired = [it for it in items if it.label_path is not None]
    if not paired:
        print("No (image,label) pairs found. Nothing to prepare.")
        print(f"See report for details: {report_path}")
        return 3

    # Step 5: Split paired items into train/val/test.
    train_items, val_items, test_items = split_items(
        paired,
        train_ratio=args.train,
        val_ratio=args.val,
        test_ratio=args.test,
        seed=args.seed,
    )

    # Step 6: Move/copy into the correct destination folders.
    place_items(train_items, "train", yolo_paths, mode=args.mode, dry_run=args.dry_run)
    place_items(val_items, "val", yolo_paths, mode=args.mode, dry_run=args.dry_run)
    place_items(test_items, "test", yolo_paths, mode=args.mode, dry_run=args.dry_run)

    # Step 7: Print a short summary.
    print("YOLO dataset preparation complete.")
    print(f"- Output dir:          {output_dir}")
    print(f"- Mode:                {args.mode}{' (dry-run)' if args.dry_run else ''}")
    print(f"- Total pairs used:    {len(paired)}")
    print(f"- Train/Val/Test:      {len(train_items)}/{len(val_items)}/{len(test_items)}")
    print(f"- Scan report written: {report_path}")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())

