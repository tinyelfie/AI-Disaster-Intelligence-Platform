"""
Satellite Image Preprocessing

Reads raw satellite images from data/raw/satellite/
Outputs resized + normalized images to data/processed/satellite/

Run once before training:
    python ml/satellite/preprocess.py
"""

import os
import pathlib
import numpy as np
from PIL import Image, ImageEnhance
import random

# Paths
ROOT      = pathlib.Path(__file__).resolve().parents[2]
RAW_DIR   = ROOT / "data" / "raw" / "satellite"
PROC_DIR  = ROOT / "data" / "processed" / "satellite"
IMG_SIZE  = (224, 224)          # EfficientNet-B0 input size

# Augmentation helpers

def random_flip(img: Image.Image) -> Image.Image:
    if random.random() > 0.5:
        img = img.transpose(Image.FLIP_LEFT_RIGHT)
    if random.random() > 0.5:
        img = img.transpose(Image.FLIP_TOP_BOTTOM)
    return img


def random_rotate(img: Image.Image) -> Image.Image:
    angle = random.choice([0, 90, 180, 270])
    return img.rotate(angle)


def random_brightness(img: Image.Image) -> Image.Image:
    factor = random.uniform(0.7, 1.3)
    return ImageEnhance.Brightness(img).enhance(factor)


def augment(img: Image.Image) -> Image.Image:
    img = random_flip(img)
    img = random_rotate(img)
    img = random_brightness(img)
    return img


# Core processing

def preprocess_image(src_path: pathlib.Path, augment_count: int = 3) -> list[np.ndarray]:
    """
    Open one raw image and return a list of preprocessed numpy arrays:
    - original resized + normalised
    - augment_count augmented variants
    """
    img = Image.open(src_path).convert("RGB")
    img = img.resize(IMG_SIZE, Image.LANCZOS)

    results = []
    arr = np.array(img, dtype=np.float32) / 255.0
    results.append(arr)

    for _ in range(augment_count):
        aug = augment(img.copy())
        results.append(np.array(aug, dtype=np.float32) / 255.0)

    return results


def process_all(augment_count: int = 3):
    """Walk raw/, process every image, save to processed/."""
    PROC_DIR.mkdir(parents=True, exist_ok=True)

    all_files = list(RAW_DIR.rglob("*.jpg")) + list(RAW_DIR.rglob("*.png")) + \
                list(RAW_DIR.rglob("*.jpeg"))

    if not all_files:
        print(f"[preprocess] No images found in {RAW_DIR}. "
              "Place the Rupak Roy Kaggle dataset there first.")
        return

    processed = 0
    for src in all_files:
        # Preserve subfolder structure (class label = parent folder name)
        rel = src.relative_to(RAW_DIR)
        out_dir = PROC_DIR / rel.parent
        out_dir.mkdir(parents=True, exist_ok=True)

        arrays = preprocess_image(src, augment_count=augment_count)
        stem = src.stem

        for i, arr in enumerate(arrays):
            tag = "orig" if i == 0 else f"aug{i}"
            out_path = out_dir / f"{stem}_{tag}.npy"
            np.save(out_path, arr)
            processed += 1

    print(f"[preprocess] Done. Saved {processed} arrays to {PROC_DIR}")


if __name__ == "__main__":
    process_all()
