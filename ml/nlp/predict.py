"""
NLP Tweet Inference

Loaded once at import time. Exposes predict(text) -> dict.
Falls back gracefully if the model is not yet trained.

Backend usage:
    from ml.nlp.predict import predict as nlp_predict
    result = nlp_predict("Flash floods are sweeping through downtown!")
"""

import pathlib
import re

ROOT      = pathlib.Path(__file__).resolve().parents[2]
MODEL_DIR = ROOT / "models" / "nlp_model"

_tokenizer = None
_model     = None


def _clean(text: str) -> str:
    text = re.sub(r"http\S+|www\S+", "", text)
    text = re.sub(r"@\w+", "", text)
    text = re.sub(r"#(\w+)", r"\1", text)
    text = re.sub(r"[^\w\s.,!?'-]", " ", text)
    return re.sub(r"\s+", " ", text).strip().lower()


def _load_model():
    global _tokenizer, _model
    if _model is not None:
        return

    try:
        import torch
        from transformers import DistilBertTokenizerFast, DistilBertForSequenceClassification

        _tokenizer = DistilBertTokenizerFast.from_pretrained(str(MODEL_DIR))
        _model     = DistilBertForSequenceClassification.from_pretrained(str(MODEL_DIR))
        _model.eval()
        print("[nlp.predict] Model loaded successfully.")
    except Exception as e:
        print(f"[nlp.predict] Could not load model ({e}). Using keyword fallback.")
        _tokenizer = None
        _model     = None


def predict(text: str) -> dict:
    """
    Classify a tweet as disaster-related or not.

    Returns:
        {
            "is_disaster": bool,
            "disaster_probability": float,   # 0-1
            "urgency_score": float,          # 0-1 (used by fusion)
            "source": "model" | "fallback"
        }
    """
    _load_model()

    if _model is not None and _tokenizer is not None:
        try:
            import torch
            import torch.nn.functional as F

            clean = _clean(text)
            enc   = _tokenizer(
                clean, max_length=128, padding="max_length",
                truncation=True, return_tensors="pt"
            )
            with torch.no_grad():
                logits = _model(**enc).logits
                probs  = F.softmax(logits, dim=1).squeeze().tolist()

            # Handle both 2-class (binary) and 6-class (multi-class) models
            if isinstance(probs, float):
                probs = [probs]
            pred_idx      = int(torch.argmax(torch.tensor(probs)).item())
            disaster_prob = round(max(probs), 4)
            return {
                "is_disaster":          disaster_prob > 0.5,
                "disaster_probability": disaster_prob,
                "predicted_class":      pred_idx,
                "urgency_score":        disaster_prob,      # proxy for fusion
                "source":               "model",
            }
        except Exception as e:
            print(f"[nlp.predict] Inference error: {e}. Using fallback.")

    # Keyword-based fallback
    DISASTER_KEYWORDS = {
        "flood", "earthquake", "fire", "wildfire", "cyclone", "hurricane",
        "tornado", "tsunami", "disaster", "emergency", "evacuation", "warning",
        "storm", "landslide", "explosion", "casualt", "trapped", "rescue",
    }
    lower = text.lower()
    hits  = sum(1 for kw in DISASTER_KEYWORDS if kw in lower)
    prob  = min(1.0, round(hits * 0.2, 4))

    return {
        "is_disaster":          prob > 0.5,
        "disaster_probability": prob,
        "urgency_score":        prob,
        "source":               "fallback",
    }
