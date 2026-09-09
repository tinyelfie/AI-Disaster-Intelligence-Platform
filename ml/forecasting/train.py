"""
XGBoost Weather Risk Forecasting — Training

Binary classification: will a disaster occur in this weather window?

Usage:
    python ml/forecasting/train.py

Saves:  models/xgboost_model.json
"""

import pathlib
import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler
import xgboost as xgb
import joblib

ROOT       = pathlib.Path(__file__).resolve().parents[2]
PROC_DIR   = ROOT / "data" / "processed" / "weather"
FEATURES   = PROC_DIR / "features.csv"
MODEL_PATH = ROOT / "models" / "xgboost_model.json"
SCALER_PATH= ROOT / "models" / "xgboost_scaler.pkl"
TARGET     = "disaster_occurred"
EXCLUDE    = {"date", "disaster_occurred"}


def train():
    if not FEATURES.exists():
        raise FileNotFoundError(
            f"{FEATURES} not found. Run ml/forecasting/preprocess.py first."
        )

    df = pd.read_csv(FEATURES)

    feature_cols = [c for c in df.columns if c not in EXCLUDE]
    X = df[feature_cols].values
    y = df[TARGET].values

    X_train, X_val, y_train, y_val = train_test_split(
        X, y, test_size=0.2, random_state=42, stratify=y
    )

    scaler  = StandardScaler()
    X_train = scaler.fit_transform(X_train)
    X_val   = scaler.transform(X_val)

    # Save feature column names for inference
    feature_names_path = ROOT / "models" / "xgboost_features.txt"
    feature_names_path.parent.mkdir(parents=True, exist_ok=True)
    feature_names_path.write_text("\n".join(feature_cols))

    model = xgb.XGBClassifier(
        n_estimators=300,
        max_depth=6,
        learning_rate=0.05,
        subsample=0.8,
        colsample_bytree=0.8,
        scale_pos_weight=(y == 0).sum() / (y == 1).sum(),  # handle class imbalance
        eval_metric="logloss",
        random_state=42,
        verbosity=1,
    )

    model.fit(
        X_train, y_train,
        eval_set=[(X_val, y_val)],
        verbose=50,
    )

    MODEL_PATH.parent.mkdir(parents=True, exist_ok=True)
    model.save_model(str(MODEL_PATH))
    joblib.dump(scaler, str(SCALER_PATH))
    print(f"\nModel saved to {MODEL_PATH}")
    print(f"Scaler saved to {SCALER_PATH}")

    val_acc = (model.predict(X_val) == y_val).mean()
    print(f"Val accuracy: {val_acc:.4f}")

    # Feature importance
    importance = sorted(
        zip(feature_cols, model.feature_importances_),
        key=lambda x: x[1], reverse=True
    )[:15]
    print("\nTop-15 feature importances:")
    for name, imp in importance:
        print(f"  {name:<40} {imp:.4f}")


if __name__ == "__main__":
    train()
