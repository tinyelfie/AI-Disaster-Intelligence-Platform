# Machine Learning Inference Module

## Overview

This directory contains the **machine learning inference pipeline** for the AI Disaster Intelligence Platform.

All models in this module are **pre-trained**. The code here is strictly limited to:
- Loading trained models
- Running inference
- Producing standardized outputs for backend consumption

Training, experimentation, and exploratory notebooks are intentionally excluded to keep the repository clean and production-oriented.

---

## Role in the Overall System

The ML module generates **disaster intelligence signals** that are later:
- Stored in a geospatial database (PostGIS)
- Served via FastAPI endpoints
- Visualized on an interactive React + Mapbox dashboard

This clear separation allows the ML system to scale independently from the application layer.

---

## Directory Structure

ml/
├── README.md
├── requirements.txt
├── inference/
│ └── predict.py
└── sample_outputs/
└── example_output.json


---

## Inference Script (`inference/predict.py`)

The `predict.py` file acts as the **single entry point** for all ML predictions.

It is responsible for:
1. Loading pre-trained model artifacts
2. Accepting structured input features
3. Running multimodal inference (satellite, social, weather)
4. Returning clean, schema-consistent outputs

The script is designed to be:
- Stateless
- Deterministic
- Callable from backend services or batch jobs

---

## Input Format (Example)

```json
{
  "latitude": 26.20,
  "longitude": 91.70,
  "timestamp": "2025-09-01T10:00:00",
  "weather_features": {
    "rainfall": 120,
    "wind_speed": 45
  },
  "social_signal_score": 0.78
}


{
  "disaster_type": "flood",
  "severity_score": 0.84,
  "risk_level": "HIGH",
  "population_at_risk": 180000,
  "confidence": 0.91,
  "timestamp": "2025-09-01T10:00:00"
}
