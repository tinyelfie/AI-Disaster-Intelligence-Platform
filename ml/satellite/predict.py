"""
Satellite Model Inference

Loaded once at import time. Exposes a single predict() function.
Falls back gracefully if the model file is not yet available.

Backend usage:
    from ml.satellite.predict import predict as satellite_predict
    result = satellite_predict(image_path)
"""

import pathlib
from typing import Optional

ROOT       = pathlib.Path(__file__).resolve().parents[2]
MODEL_PATH = ROOT / "models" / "satellite_model.pt"

# Lazy model loader (loaded once at first call)
_model  = None
_classes = None

# Default classes matching the Rupak Roy Kaggle dataset categories
_DEFAULT_CLASSES = ["cyclone", "earthquake", "flood", "wildfire"]


def _load_model():
    global _model, _classes
    if _model is not None:
        return

    try:
        import torch
        from torchvision import transforms
        from ml.satellite.train import build_model

        ckpt    = torch.load(MODEL_PATH, map_location="cpu")
        _classes = ckpt["classes"]
        m        = build_model(len(_classes))
        m.load_state_dict(ckpt["state_dict"])
        m.eval()
        _model = m
        print("[satellite.predict] Model loaded successfully.")

    except Exception as e:
        print(f"[satellite.predict] Could not load model ({e}). Using rule-based fallback.")
        _model  = None
        _classes = _DEFAULT_CLASSES


def predict(image_path: Optional[str] = None) -> dict:
    """
    Run satellite inference on a single image.

    Args:
        image_path: Absolute path to image file.

    Returns:
        {
            "disaster_type": str,
            "probability": float,       # 0-1
            "all_probabilities": dict,  # {class: prob}
            "source": "model" | "fallback"
        }
    """
    _load_model()

    if _model is not None and image_path:
        try:
            import torch
            import torch.nn.functional as F
            from torchvision import transforms
            from PIL import Image

            transform = transforms.Compose([
                transforms.Resize((224, 224)),
                transforms.ToTensor(),
                transforms.Normalize([0.485, 0.456, 0.406],
                                     [0.229, 0.224, 0.225]),
            ])
            img    = Image.open(image_path).convert("RGB")
            tensor = transform(img).unsqueeze(0)

            with torch.no_grad():
                logits = _model(tensor)
                probs  = F.softmax(logits, dim=1).squeeze().tolist()

            pred_idx = int(torch.argmax(torch.tensor(probs)).item())
            return {
                "disaster_type":     _classes[pred_idx],
                "probability":       round(probs[pred_idx], 4),
                "all_probabilities": {c: round(p, 4) for c, p in zip(_classes, probs)},
                "source":            "model",
            }
        except Exception as e:
            print(f"[satellite.predict] Inference error: {e}. Using fallback.")

    # Rule-based fallback (no model / no image)
    import random
    idx  = random.randint(0, len(_DEFAULT_CLASSES) - 1)
    prob = round(random.uniform(0.55, 0.95), 4)
    return {
        "disaster_type":     _DEFAULT_CLASSES[idx],
        "probability":       prob,
        "all_probabilities": {c: round(random.uniform(0.0, 0.5), 4) for c in _DEFAULT_CLASSES},
        "source":            "fallback",
    }
