"""
XGBoost Forecasting Evaluation

MAE, RMSE, F1, and feature importance plot.

Usage:
    python ml/forecasting/evaluate.py
"""

import pathlib
import pandas as pd
import numpy as np
import xgboost as xgb
import joblib
import matplotlib.pyplot as plt
from sklearn.model_selection import train_test_split
from sklearn.metrics import classification_report, mean_absolute_error
from sklearn.preprocessing import StandardScaler

ROOT        = pathlib.Path(__file__).resolve().parents[2]
PROC_DIR    = ROOT / "data" / "processed" / "weather"
FEATURES    = PROC_DIR / "features.csv"
MODEL_PATH  = ROOT / "models" / "xgboost_model.json"
SCALER_PATH = ROOT / "models" / "xgboost_scaler.pkl"
TARGET      = "disaster_occurred"
EXCLUDE     = {"date", "disaster_occurred"}


def evaluate():
    if not MODEL_PATH.exists():
        print("[forecasting.evaluate] Model not found. Train first.")
        return

    df = pd.read_csv(FEATURES)
    feature_cols = [c for c in df.columns if c not in EXCLUDE]
    X = df[feature_cols].values
    y = df[TARGET].values

    _, X_test, _, y_test = train_test_split(X, y, test_size=0.2, random_state=42, stratify=y)

    scaler = joblib.load(str(SCALER_PATH))
    X_test = scaler.transform(X_test)

    model = xgb.XGBClassifier()
    model.load_model(str(MODEL_PATH))

    probs  = model.predict_proba(X_test)[:, 1]
    preds  = (probs > 0.5).astype(int)

    mae  = mean_absolute_error(y_test, probs)
    rmse = np.sqrt(((y_test - probs) ** 2).mean())

    print(f"\n=== XGBoost Forecasting Evaluation ===")
    print(f"MAE:  {mae:.4f}")
    print(f"RMSE: {rmse:.4f}")
    print(classification_report(y_test, preds, target_names=["No Disaster", "Disaster"]))

    # Feature importance plot
    importance = pd.Series(model.feature_importances_, index=feature_cols)
    importance = importance.nlargest(20)

    plt.figure(figsize=(10, 6))
    importance.sort_values().plot(kind="barh", color="firebrick")
    plt.title("XGBoost Feature Importance (Top 20)")
    plt.xlabel("Importance Score")
    plt.tight_layout()
    out_path = ROOT / "models" / "xgboost_feature_importance.png"
    plt.savefig(out_path, dpi=150)
    print(f"\nFeature importance plot saved to {out_path}")


if __name__ == "__main__":
    evaluate()
