"""
Satellite Model Evaluation

Run after training to get accuracy, F1, confusion matrix, and Grad-CAM.

Usage:
    python ml/satellite/evaluate.py
"""

import pathlib
import numpy as np
import torch
import torch.nn.functional as F
from torchvision import transforms
from PIL import Image
from sklearn.metrics import classification_report, confusion_matrix
import matplotlib.pyplot as plt
import seaborn as sns

from ml.satellite.train import SatelliteDataset, build_model

# Config
ROOT       = pathlib.Path(__file__).resolve().parents[2]
PROC_DIR   = ROOT / "data" / "processed" / "satellite"
MODEL_PATH = ROOT / "models" / "satellite_model.pt"
DEVICE     = "cuda" if torch.cuda.is_available() else "cpu"


def load_model():
    ckpt  = torch.load(MODEL_PATH, map_location=DEVICE)
    model = build_model(ckpt["num_classes"])
    model.load_state_dict(ckpt["state_dict"])
    model.eval()
    return model, ckpt["classes"]


def evaluate():
    if not MODEL_PATH.exists():
        print(f"[evaluate] Model not found at {MODEL_PATH}. Train first.")
        return

    model, classes = load_model()
    model = model.to(DEVICE)

    transform = transforms.Compose([
        transforms.Resize((224, 224)),
        transforms.ToTensor(),
        transforms.Normalize([0.485, 0.456, 0.406], [0.229, 0.224, 0.225]),
    ])

    dataset     = SatelliteDataset(PROC_DIR, transform=transform)
    loader      = torch.utils.data.DataLoader(dataset, batch_size=32, shuffle=False)
    all_preds   = []
    all_labels  = []

    with torch.no_grad():
        for imgs, labels in loader:
            imgs = imgs.to(DEVICE)
            preds = model(imgs).argmax(dim=1).cpu().numpy()
            all_preds.extend(preds)
            all_labels.extend(labels.numpy())

    print("\n=== Classification Report ===")
    print(classification_report(all_labels, all_preds, target_names=classes))

    cm = confusion_matrix(all_labels, all_preds)
    plt.figure(figsize=(8, 6))
    sns.heatmap(cm, annot=True, fmt="d", xticklabels=classes, yticklabels=classes, cmap="Reds")
    plt.title("Confusion Matrix — Satellite Model")
    plt.ylabel("True")
    plt.xlabel("Predicted")
    plt.tight_layout()
    plt.savefig(ROOT / "models" / "satellite_confusion_matrix.png", dpi=150)
    print(f"Confusion matrix saved to models/satellite_confusion_matrix.png")


# Grad-CAM

class GradCAM:
    def __init__(self, model, target_layer):
        self.model        = model
        self.gradients    = None
        self.activations  = None
        target_layer.register_forward_hook(self._fwd_hook)
        target_layer.register_backward_hook(self._bwd_hook)

    def _fwd_hook(self, module, inp, out):
        self.activations = out.detach()

    def _bwd_hook(self, module, grad_in, grad_out):
        self.gradients = grad_out[0].detach()

    def generate(self, img_tensor, class_idx):
        self.model.zero_grad()
        logits = self.model(img_tensor)
        logits[0, class_idx].backward()
        weights = self.gradients.mean(dim=(2, 3), keepdim=True)
        cam = (weights * self.activations).sum(dim=1, keepdim=True)
        cam = F.relu(cam)
        cam = cam - cam.min()
        cam = cam / (cam.max() + 1e-8)
        return cam.squeeze().cpu().numpy()


def grad_cam_demo(image_path: str):
    """Generate and save a Grad-CAM overlay for a single image."""
    if not MODEL_PATH.exists():
        print("Model not found. Train first.")
        return

    model, classes = load_model()
    model = model.to(DEVICE)

    transform = transforms.Compose([
        transforms.Resize((224, 224)),
        transforms.ToTensor(),
        transforms.Normalize([0.485, 0.456, 0.406], [0.229, 0.224, 0.225]),
    ])

    img     = Image.open(image_path).convert("RGB")
    tensor  = transform(img).unsqueeze(0).to(DEVICE)
    gcam    = GradCAM(model, model.features[-1])
    logits  = model(tensor)
    pred    = logits.argmax(dim=1).item()
    cam_map = gcam.generate(tensor, pred)

    cam_resized = np.array(Image.fromarray((cam_map * 255).astype(np.uint8)).resize(img.size))

    plt.figure(figsize=(8, 4))
    plt.subplot(1, 2, 1); plt.imshow(img); plt.title("Original"); plt.axis("off")
    plt.subplot(1, 2, 2); plt.imshow(img); plt.imshow(cam_resized, alpha=0.5, cmap="jet"); plt.title(f"Grad-CAM: {classes[pred]}"); plt.axis("off")
    plt.tight_layout()
    out_path = ROOT / "models" / "grad_cam_demo.png"
    plt.savefig(out_path, dpi=150)
    print(f"Grad-CAM saved to {out_path}")


if __name__ == "__main__":
    evaluate()
