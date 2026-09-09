"""
XGBoost Weather Risk Inference

Loaded once at import time. Exposes predict(weather_params) -> dict.
Falls back gracefully when model is not yet trained.

Backend usage:
    from ml.forecasting.predict import predict as weather_predict
    result = weather_predict({
        "precipitation": 80.0,
        "temp_max": 38.5,
        "temp_min": 22.0,
        "wind_speed": 55.0,
        "humidity": 88.0,
    })
"""

import pathlib

ROOT        = pathlib.Path(__file__).resolve().parents[2]
MODEL_PATH  = ROOT / "models" / "xgboost_model.json"
SCALER_PATH = ROOT / "models" / "xgboost_scaler.pkl"
FEAT_PATH   = ROOT / "models" / "xgboost_features.txt"

_model         = None
_scaler        = None
_feature_names = None


def _load_model():
    global _model, _scaler, _feature_names
    if _model is not None:
        return

    try:
        import xgboost as xgb
        import joblib

        _model  = xgb.XGBClassifier()
        _model.load_model(str(MODEL_PATH))
        _scaler = joblib.load(str(SCALER_PATH))
        _feature_names = FEAT_PATH.read_text().strip().split("\n") if FEAT_PATH.exists() else []
        print("[forecasting.predict] Model loaded successfully.")
    except Exception as e:
        print(f"[forecasting.predict] Could not load model ({e}). Using rule-based fallback.")
        _model = None


def predict(weather_params: dict) -> dict:
    """
    Predict disaster risk from weather parameters.

    Args:
        weather_params: dict with keys like:
            precipitation (mm), temp_max (°C), temp_min (°C),
            wind_speed (km/h), humidity (%)

    Returns:
        {
            "risk_score": float,      # 0-1 probability of disaster
            "risk_level": str,        # LOW | MEDIUM | HIGH | CRITICAL
            "source": "model" | "fallback"
        }
    """
    _load_model()

    if _model is not None and _feature_names:
        try:
            import numpy as np
            # Build feature vector (zeros for engineered features not provided)
            vec = [weather_params.get(f, 0.0) for f in _feature_names]
            X   = _scaler.transform([vec])
            prob = float(_model.predict_proba(X)[0][1])
            return {
                "risk_score": round(prob, 4),
                "risk_level": _score_to_level(prob),
                "source":     "model",
            }
        except Exception as e:
            print(f"[forecasting.predict] Inference error: {e}. Using fallback.")

    # Rule-based fallback
    rain  = weather_params.get("precipitation", 0)
    wind  = weather_params.get("wind_speed", 0)
    humid = weather_params.get("humidity", 0)

    score = min(1.0, (rain / 200) * 0.5 + (wind / 100) * 0.3 + (humid / 100) * 0.2)
    return {
        "risk_score": round(score, 4),
        "risk_level": _score_to_level(score),
        "source":     "fallback",
    }


def _score_to_level(score: float) -> str:
    if score > 0.75:  return "CRITICAL"
    if score > 0.50:  return "HIGH"
    if score > 0.25:  return "MEDIUM"
    return "LOW"
