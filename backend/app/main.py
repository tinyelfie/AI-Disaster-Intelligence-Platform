"""
AI Disaster Intelligence Platform — FastAPI Backend

All routes in a single file.

Start:
    uvicorn backend.app.main:app --reload --port 8000

Endpoints:
    GET  /health
    GET  /disasters
    GET  /risk-zones
    GET  /analytics/summary
    POST /predict/disaster
    POST /predict/satellite
    POST /predict/tweet
    POST /predict/weather
    POST /situation-report
"""

import sys
import os
import time

PROJECT_ROOT = os.path.abspath(
    os.path.join(os.path.dirname(__file__), "..", "..")
)
BACKEND_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
# Make both project root AND backend/ importable so 'app.*' resolves correctly
for _p in [PROJECT_ROOT, BACKEND_DIR]:
    if _p not in sys.path:
        sys.path.insert(0, _p)

# Load .env
try:
    from dotenv import load_dotenv
    load_dotenv(os.path.join(PROJECT_ROOT, ".env"))
except ImportError:
    pass

from fastapi import FastAPI, HTTPException, UploadFile, File
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Optional
from datetime import datetime

from app.db import SessionLocal, engine, Base
from ml.inference.predict import run_inference

# DB bootstrap (only when engine is available)
if engine is not None:
    try:
        Base.metadata.create_all(bind=engine)
    except Exception as _db_err:
        print(f"[main] DB table creation skipped: {_db_err}")

# FastAPI app
app = FastAPI(
    title="AI Disaster Intelligence Platform",
    description="Real-time disaster detection, risk forecasting, and RAG situation reports",
    version="2.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://127.0.0.1:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Pydantic Schemas


class DisasterInput(BaseModel):
    latitude: float
    longitude: float
    timestamp: datetime
    weather_rainfall: Optional[float] = None
    weather_wind_speed: Optional[float] = None
    social_signal_score: Optional[float] = None


class DisasterOutput(BaseModel):
    disaster_type: str
    severity_score: float
    risk_level: str
    population_at_risk: int
    confidence: float
    timestamp: datetime


class DisasterRecord(BaseModel):
    id: int
    disaster_type: str
    severity_score: float
    risk_level: str
    population_at_risk: int
    confidence: float
    latitude: float
    longitude: float
    created_at: datetime


class TweetInput(BaseModel):
    text: str


class WeatherInput(BaseModel):
    precipitation: Optional[float] = 0.0
    temp_max: Optional[float] = 30.0
    temp_min: Optional[float] = 20.0
    wind_speed: Optional[float] = 0.0
    humidity: Optional[float] = 60.0
    location: Optional[str] = "Unknown"


class SituationReportInput(BaseModel):
    region: str
    disaster_type: str
    severity: str


class RiskZone(BaseModel):
    id: int
    name: str
    severity: str
    zone_type: Optional[str] = None
    description: Optional[str] = None
    bounds: dict   # {north, south, east, west}


class AnalyticsSummary(BaseModel):
    total_incidents: int
    critical_count: int
    high_count: int
    medium_count: int
    low_count: int
    avg_confidence: float
    avg_severity: float
    by_type: list
    monthly_severity: list


# Helpers


def _mock_risk_zones() -> list[dict]:
    """
    Static risk zone data (used when PostGIS / DB is not available).
    Each zone has a simple lat/lng bounding box for the Leaflet frontend.
    """
    return [
        {
            "id": 1,
            "name": "Bay of Bengal Coastal Strip",
            "severity": "CRITICAL",
            "zone_type": "coastal",
            "description": "High cyclone and storm surge risk",
            "bounds": {"north": 22.0, "south": 15.0, "east": 92.0, "west": 85.0},
        },
        {
            "id": 2,
            "name": "Indo-Gangetic Flood Plain",
            "severity": "HIGH",
            "zone_type": "flood_plain",
            "description": "Monsoon flood-prone alluvial plain",
            "bounds": {"north": 30.0, "south": 24.0, "east": 88.0, "west": 75.0},
        },
        {
            "id": 3,
            "name": "Western Ghats Fire Zone",
            "severity": "HIGH",
            "zone_type": "fire_risk",
            "description": "Dense forest cover — high wildfire risk in dry season",
            "bounds": {"north": 21.0, "south": 8.0, "east": 78.0, "west": 74.0},
        },
        {
            "id": 4,
            "name": "Himalayan Seismic Belt",
            "severity": "MEDIUM",
            "zone_type": "seismic",
            "description": "Active tectonic zone — moderate to high earthquake probability",
            "bounds": {"north": 36.0, "south": 27.0, "east": 97.0, "west": 72.0},
        },
        {
            "id": 5,
            "name": "Rajasthan Drought Zone",
            "severity": "MEDIUM",
            "zone_type": "drought",
            "description": "Arid region with persistent drought and heat wave risk",
            "bounds": {"north": 30.0, "south": 24.0, "east": 78.0, "west": 69.0},
        },
    ]


def _fallback_disasters() -> list[dict]:
    """Return mock disaster data when the DB is empty or unavailable."""
    import random
    base = [
        {"disaster_type": "flood",      "risk_level": "HIGH",     "latitude": 23.8,  "longitude": 90.4,  "severity_score": 0.72, "confidence": 0.89},
        {"disaster_type": "wildfire",   "risk_level": "CRITICAL", "latitude": 15.3,  "longitude": 75.1,  "severity_score": 0.91, "confidence": 0.94},
        {"disaster_type": "earthquake", "risk_level": "MEDIUM",   "latitude": 28.6,  "longitude": 77.2,  "severity_score": 0.55, "confidence": 0.78},
        {"disaster_type": "cyclone",    "risk_level": "CRITICAL", "latitude": 17.4,  "longitude": 83.5,  "severity_score": 0.88, "confidence": 0.92},
        {"disaster_type": "flood",      "risk_level": "MEDIUM",   "latitude": 25.6,  "longitude": 85.1,  "severity_score": 0.50, "confidence": 0.81},
        {"disaster_type": "wildfire",   "risk_level": "HIGH",     "latitude": 12.9,  "longitude": 77.6,  "severity_score": 0.70, "confidence": 0.87},
        {"disaster_type": "earthquake", "risk_level": "HIGH",     "latitude": 34.1,  "longitude": 74.8,  "severity_score": 0.68, "confidence": 0.83},
        {"disaster_type": "flood",      "risk_level": "HIGH",     "latitude": 22.3,  "longitude": 88.3,  "severity_score": 0.75, "confidence": 0.90},
    ]
    now = datetime.utcnow()
    return [
        {
            "id": i + 1,
            "disaster_type": d["disaster_type"],
            "severity_score": d["severity_score"],
            "risk_level": d["risk_level"],
            "population_at_risk": random.randint(10000, 200000),
            "confidence": d["confidence"],
            "latitude": d["latitude"],
            "longitude": d["longitude"],
            "created_at": now.isoformat(),
        }
        for i, d in enumerate(base)
    ]


# Routes


@app.get("/health")
def health_check():
    return {"status": "ok", "version": "2.0.0"}


# GET /disasters
@app.get("/disasters")
def get_disasters():
    """Fetch recent disasters for the map and dashboard."""
    try:
        from database.db import get_recent_disasters
        rows = get_recent_disasters(limit=100)
        if rows:
            # Normalise datetime objects to ISO strings
            for r in rows:
                if hasattr(r.get("created_at"), "isoformat"):
                    r["created_at"] = r["created_at"].isoformat()
            return rows
    except Exception as e:
        print(f"[GET /disasters] DB error: {e}")

    # Fallback: return mock data so the frontend always has something to show
    return _fallback_disasters()


# GET /risk-zones
@app.get("/risk-zones")
def get_risk_zones():
    """Return severity-classified geographic bounding boxes for the map overlay."""
    try:
        from database.db import get_risk_zones as db_risk_zones
        zones = db_risk_zones()
        if zones:
            return zones
    except Exception as e:
        print(f"[GET /risk-zones] DB error: {e}")

    return _mock_risk_zones()


# GET /analytics/summary
@app.get("/analytics/summary")
def analytics_summary():
    """Aggregated stats for Dashboard and Analytics pages."""
    try:
        from database.db import get_analytics_summary
        return get_analytics_summary()
    except Exception as e:
        print(f"[GET /analytics/summary] Error: {e}")
        from database.db import _fallback_analytics
        return _fallback_analytics()


# POST /predict/disaster
@app.post("/predict/disaster", response_model=DisasterOutput)
def predict_disaster(data: DisasterInput):
    """Run the composite rule-based inference on weather + social signals."""
    prediction = run_inference(data.dict())

    result = DisasterOutput(
        disaster_type=prediction["disaster_type"],
        severity_score=prediction["severity_score"],
        risk_level=prediction["risk_level"],
        population_at_risk=prediction["population_at_risk"],
        confidence=prediction["confidence"],
        timestamp=datetime.utcnow(),
    )

    # Persist to DB
    try:
        if SessionLocal is not None:
            from sqlalchemy import text
            db = SessionLocal()
            db.execute(text("""
                INSERT INTO disasters
                    (disaster_type, severity_score, risk_level, population_at_risk,
                     confidence, latitude, longitude, created_at)
                VALUES
                    (:disaster_type, :severity_score, :risk_level, :population_at_risk,
                     :confidence, :latitude, :longitude, :created_at)
            """), {
                "disaster_type":    result.disaster_type,
                "severity_score":   result.severity_score,
                "risk_level":       result.risk_level,
                "population_at_risk": result.population_at_risk,
                "confidence":       result.confidence,
                "latitude":         data.latitude,
                "longitude":        data.longitude,
                "created_at":       result.timestamp,
            })
            db.commit()
            db.close()
    except Exception as e:
        print(f"[POST /predict/disaster] DB insert error: {e}")


    return result


# POST /predict/satellite
@app.post("/predict/satellite")
def predict_satellite(image_url: Optional[str] = None):
    """
    Run satellite image classification.
    Accepts an optional image URL (for demo, uses the fallback when no model).
    """
    t0 = time.time()

    try:
        from ml.satellite.predict import predict as sat_predict
        result = sat_predict(image_path=None)    # fallback — no local file in demo
    except Exception as e:
        result = {
            "disaster_type":     "flood",
            "probability":       0.78,
            "all_probabilities": {"cyclone": 0.10, "earthquake": 0.05, "flood": 0.78, "wildfire": 0.07},
            "source":            "fallback",
        }

    result["latency_ms"] = int((time.time() - t0) * 1000)
    return result


# POST /predict/tweet
@app.post("/predict/tweet")
def predict_tweet(data: TweetInput):
    """Classify a tweet as disaster-related and return an urgency score."""
    t0 = time.time()

    if not data.text or not data.text.strip():
        raise HTTPException(status_code=422, detail="text field is required")

    try:
        from ml.nlp.predict import predict as nlp_predict
        result = nlp_predict(data.text)
    except Exception as e:
        result = {
            "is_disaster":          True,
            "disaster_probability": 0.82,
            "urgency_score":        0.82,
            "source":               "fallback",
        }

    result["latency_ms"] = int((time.time() - t0) * 1000)

    # Log prediction
    try:
        from database.db import save_prediction
        save_prediction(
            source="tweet",
            input_data={"text": data.text},
            output_data=result,
            risk_level="HIGH" if result.get("urgency_score", 0) > 0.5 else "LOW",
            confidence=result.get("disaster_probability"),
            latency_ms=result["latency_ms"],
        )
    except Exception:
        pass

    return result


# POST /predict/weather
@app.post("/predict/weather")
def predict_weather(data: WeatherInput):
    """Run XGBoost weather risk forecasting."""
    t0 = time.time()

    try:
        from ml.forecasting.predict import predict as wx_predict
        result = wx_predict(data.dict())
    except Exception as e:
        result = {
            "risk_score":  0.65,
            "risk_level":  "HIGH",
            "source":      "fallback",
        }

    result["latency_ms"] = int((time.time() - t0) * 1000)
    result["location"]   = data.location

    # Log prediction
    try:
        from database.db import save_prediction
        save_prediction(
            source="weather",
            input_data=data.dict(),
            output_data=result,
            risk_level=result.get("risk_level"),
            confidence=result.get("risk_score"),
            latency_ms=result["latency_ms"],
        )
    except Exception:
        pass

    return result


# POST /situation-report
@app.post("/situation-report")
def situation_report(data: SituationReportInput):
    """
    Generate a RAG-augmented situation report using Groq Cloud (llama-3.1-8b-instant).
    Falls back to a canned report if Groq API is not configured.
    """
    if not data.region or not data.disaster_type:
        raise HTTPException(status_code=422, detail="region and disaster_type are required")

    t0 = time.time()

    try:
        from rag.pipeline import generate_situation_report
        report = generate_situation_report(
            region=data.region,
            severity=data.severity,
            disaster_type=data.disaster_type,
        )
    except Exception as e:
        print(f"[POST /situation-report] RAG pipeline error: {e}")
        report = f"""## Situation Report — {data.region}

**Disaster Type:** {data.disaster_type.title()}
**Severity:** {data.severity}

### Summary
A {data.severity.lower()} severity {data.disaster_type.lower()} event has been detected
in the **{data.region}** area. Emergency response protocols are active.

### Recommended Actions
- Deploy emergency response teams immediately
- Issue public safety warnings to all sectors within 15 km
- Activate evacuation routes for high-risk populations
- Coordinate with regional disaster management agencies
- Monitor all satellite and sensor feeds continuously

### Status
RAG pipeline temporarily unavailable. Configure `GROQ_API_KEY` and run the
embedding pipeline (`rag/scraper.py → rag/chunker.py → rag/embedder.py`) for
AI-generated analysis."""

    latency = int((time.time() - t0) * 1000)
    return {
        "region":        data.region,
        "disaster_type": data.disaster_type,
        "severity":      data.severity,
        "report":        report,
        "latency_ms":    latency,
    }
