"""
Satellite Model Training — EfficientNet-B0 Transfer Learning

Run this in Google Colab after uploading data/processed/satellite/

Usage:
    python ml/satellite/train.py

Saves:  models/satellite_model.pt
"""

import pathlib
import numpy as np
import torch
import torch.nn as nn
import torch.optim as optim
from torch.utils.data import Dataset, DataLoader, random_split
from torchvision import models, transforms
from PIL import Image

# Config
ROOT       = pathlib.Path(__file__).resolve().parents[2]
PROC_DIR   = ROOT / "data" / "processed" / "satellite"
MODEL_PATH = ROOT / "models" / "satellite_model.pt"
EPOCHS     = 15
BATCH_SIZE = 32
LR         = 1e-4
IMG_SIZE   = 224
DEVICE     = "cuda" if torch.cuda.is_available() else "cpu"

# Dataset

class SatelliteDataset(Dataset):
    """
    Expects PROC_DIR/<class_label>/*.npy  (float32 H×W×3 arrays 0-1)
    Class labels are the subfolder names.
    """
    def __init__(self, root: pathlib.Path, transform=None):
        self.samples: list[tuple[pathlib.Path, int]] = []
        self.classes: list[str] = sorted([
            d.name for d in root.iterdir() if d.is_dir()
        ])
        self.class_to_idx = {c: i for i, c in enumerate(self.classes)}
        self.transform = transform

        for cls in self.classes:
            for npy in (root / cls).glob("*.npy"):
                self.samples.append((npy, self.class_to_idx[cls]))

    def __len__(self):
        return len(self.samples)

    def __getitem__(self, idx):
        path, label = self.samples[idx]
        arr = np.load(path)                          # H×W×3 float32 0-1
        arr = (arr * 255).astype(np.uint8)
        img = Image.fromarray(arr)
        if self.transform:
            img = self.transform(img)
        return img, label


# Model

def build_model(num_classes: int) -> nn.Module:
    model = models.efficientnet_b0(weights=models.EfficientNet_B0_Weights.DEFAULT)
    # Freeze backbone
    for param in model.features.parameters():
        param.requires_grad = False
    # Replace classifier
    in_features = model.classifier[1].in_features
    model.classifier = nn.Sequential(
        nn.Dropout(p=0.3),
        nn.Linear(in_features, num_classes)
    )
    return model


# Training

def train():
    transform = transforms.Compose([
        transforms.Resize((IMG_SIZE, IMG_SIZE)),
        transforms.ToTensor(),
        transforms.Normalize(mean=[0.485, 0.456, 0.406],
                             std=[0.229, 0.224, 0.225]),
    ])

    dataset = SatelliteDataset(PROC_DIR, transform=transform)
    if len(dataset) == 0:
        raise RuntimeError(
            f"No .npy files found in {PROC_DIR}. "
            "Run ml/satellite/preprocess.py first."
        )

    n_val   = max(1, int(0.15 * len(dataset)))
    n_train = len(dataset) - n_val
    train_ds, val_ds = random_split(dataset, [n_train, n_val])

    train_loader = DataLoader(train_ds, batch_size=BATCH_SIZE, shuffle=True,  num_workers=2)
    val_loader   = DataLoader(val_ds,   batch_size=BATCH_SIZE, shuffle=False, num_workers=2)

    model     = build_model(len(dataset.classes)).to(DEVICE)
    criterion = nn.CrossEntropyLoss()
    optimizer = optim.AdamW(model.classifier.parameters(), lr=LR)
    scheduler = optim.lr_scheduler.CosineAnnealingLR(optimizer, T_max=EPOCHS)

    best_val_acc = 0.0

    for epoch in range(1, EPOCHS + 1):
        model.train()
        running_loss = 0.0
        for imgs, labels in train_loader:
            imgs, labels = imgs.to(DEVICE), labels.to(DEVICE)
            optimizer.zero_grad()
            out  = model(imgs)
            loss = criterion(out, labels)
            loss.backward()
            optimizer.step()
            running_loss += loss.item()

        # Validation
        model.eval()
        correct = total = 0
        with torch.no_grad():
            for imgs, labels in val_loader:
                imgs, labels = imgs.to(DEVICE), labels.to(DEVICE)
                preds = model(imgs).argmax(dim=1)
                correct += (preds == labels).sum().item()
                total   += labels.size(0)

        val_acc = correct / total
        scheduler.step()
        print(f"Epoch {epoch}/{EPOCHS}  loss={running_loss/len(train_loader):.4f}  val_acc={val_acc:.3f}")

        if val_acc > best_val_acc:
            best_val_acc = val_acc
            MODEL_PATH.parent.mkdir(parents=True, exist_ok=True)
            torch.save({
                "state_dict": model.state_dict(),
                "classes":    dataset.classes,
                "num_classes": len(dataset.classes),
            }, MODEL_PATH)
            print(f"  ✓ Saved best model (val_acc={val_acc:.3f})")

    print(f"\nTraining complete. Best val accuracy: {best_val_acc:.3f}")
    print(f"Model saved to {MODEL_PATH}")


if __name__ == "__main__":
    train()
