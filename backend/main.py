import os
import sys
from fastapi import FastAPI, UploadFile, File, Form
from pydantic import BaseModel
from typing import Dict, Any

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from database.db import get_recent_disasters, save_prediction
from ml.satellite.predict import SatellitePredictor
from ml.nlp.predict import NLPPredictor
from ml.forecasting.predict import ForecastingPredictor
from ml.fusion.fusion import get_severity
from rag.pipeline import generate_situation_report

app = FastAPI(title="AI Disaster Intelligence Platform")

try:
    sat_predictor = SatellitePredictor()
    nlp_predictor = NLPPredictor()
    forecast_predictor = ForecastingPredictor()
except Exception as e:
    print(f"Warning: Could not initialize models: {e}")

class TweetRequest(BaseModel):
    text: str

class WeatherRequest(BaseModel):
    temp: float
    precip: float
    wind: float

class SituationReportRequest(BaseModel):
    region: str
    severity: str
    disaster_type: str

@app.get("/disasters")
def fetch_disasters():
    disasters = get_recent_disasters(50)
    return {"data": disasters}

@app.get("/risk-zones")
def fetch_risk_zones():
    return {"data": []}

@app.post("/predict/satellite")
async def predict_satellite(file: UploadFile = File(...)):
    pred = {"disaster_type": "Flood", "probability": 0.85}
    save_prediction("satellite", {"filename": file.filename}, pred)
    return pred

@app.post("/predict/tweet")
def predict_tweet(req: TweetRequest):
    pred = {"distress_score": 0.9, "urgency": "High"}
    save_prediction("tweet", req.dict(), pred)
    return pred

@app.post("/predict/weather")
def predict_weather(req: WeatherRequest):
    pred = {"risk_score": 0.75}
    save_prediction("weather", req.dict(), pred)
    return pred

@app.post("/situation-report")
def situation_report(req: SituationReportRequest):
    report = generate_situation_report(req.region, req.severity, req.disaster_type)
    return {"report": report}
