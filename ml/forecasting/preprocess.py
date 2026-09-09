"""
Weather + Disaster Forecasting Preprocessing

Joins weather CSV + disaster events CSV, engineers lag features.

Usage:
    python ml/forecasting/preprocess.py
"""

import pathlib
import pandas as pd
import numpy as np

ROOT     = pathlib.Path(__file__).resolve().parents[2]
WEATHER  = ROOT / "data" / "raw" / "weather" / "history_latest.csv"
DISASTER = ROOT / "data" / "raw" / "weather" / "global_disaster_events.csv"
PROC_DIR = ROOT / "data" / "processed" / "weather"
OUT_CSV  = PROC_DIR / "features.csv"


# Actual column names from the 'Daily Global Capitals Weather Data' Kaggle dataset
LAG_COLS    = ["precip_mm", "temp_max_c", "temp_min_c", "windspeed_10m_max_kmh"]
LAG_WINDOWS = [3, 7, 14]    # rolling window sizes in days
TARGET_COL  = "disaster_occurred"


def feature_engineer(df: pd.DataFrame) -> pd.DataFrame:
    df = df.sort_values("date")

    for col in LAG_COLS:
        if col not in df.columns:
            continue
        # Lag features
        for lag in [1, 3, 7]:
            df[f"{col}_lag{lag}"] = df[col].shift(lag)
        # Rolling features
        for win in LAG_WINDOWS:
            df[f"{col}_roll{win}_mean"] = df[col].rolling(win).mean()
            df[f"{col}_roll{win}_max"]  = df[col].rolling(win).max()
            df[f"{col}_roll{win}_std"]  = df[col].rolling(win).std()

    # Calendar features
    df["month"]      = pd.to_datetime(df["date"]).dt.month
    df["day_of_year"]= pd.to_datetime(df["date"]).dt.dayofyear

    df = df.dropna()
    return df


def preprocess():
    if not WEATHER.exists():
        print(f"[forecasting.preprocess] {WEATHER} not found. "
              "Place history_latest.csv in data/raw/weather/")
        return

    weather_df = pd.read_csv(WEATHER, parse_dates=["date"])

    if DISASTER.exists():
        disaster_df = pd.read_csv(DISASTER, parse_dates=["date"])
        disaster_df[TARGET_COL] = 1
        disaster_df = disaster_df[["date", TARGET_COL]].drop_duplicates()
        df = weather_df.merge(disaster_df, on="date", how="left")
        df[TARGET_COL] = df[TARGET_COL].fillna(0).astype(int)
    else:
        print("[forecasting.preprocess] global_disaster_events.csv not found. "
              "Creating synthetic target from high-rainfall thresholds.")
        df = weather_df.copy()
        df[TARGET_COL] = (
            (df.get("precip_mm", 0) > 20) |
            (df.get("windspeed_10m_max_kmh", 0) > 40)
        ).astype(int)

    df = feature_engineer(df)
    PROC_DIR.mkdir(parents=True, exist_ok=True)
    df.to_csv(OUT_CSV, index=False)
    print(f"[forecasting.preprocess] Done. {len(df)} rows → {OUT_CSV}")
    print(f"  Target distribution: {df[TARGET_COL].value_counts().to_dict()}")


if __name__ == "__main__":
    preprocess()
