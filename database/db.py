"""
Database Access Layer

SQLAlchemy engine + session + cross-engine query functions (SQLite & PostgreSQL compatible).
Imported by the backend and by database/seed.py.

Usage:
    from database.db import get_recent_disasters, save_prediction, get_risk_zones, get_analytics_summary
"""

import os
import sys
import json
import pathlib
from datetime import datetime
from typing import Optional

ROOT = pathlib.Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

try:
    from dotenv import load_dotenv
    load_dotenv(ROOT / ".env")
except ImportError:
    pass

from sqlalchemy import (
    create_engine, Column, Integer, String, Float, Text, DateTime
)
from sqlalchemy.orm import declarative_base, sessionmaker, Session

Base = declarative_base()


# ORM Models

class DisasterModel(Base):
    __tablename__ = "disasters"
    id = Column(Integer, primary_key=True, autoincrement=True)
    disaster_type = Column(String(64), nullable=False, index=True)
    severity_score = Column(Float, nullable=False)
    risk_level = Column(String(16), nullable=False, index=True)
    population_at_risk = Column(Integer, default=0)
    confidence = Column(Float, default=0.0)
    latitude = Column(Float, nullable=False)
    longitude = Column(Float, nullable=False)
    location_name = Column(String(256), nullable=True)
    country = Column(String(128), nullable=True)
    description = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow, index=True)


class PredictionModel(Base):
    __tablename__ = "predictions"
    id = Column(Integer, primary_key=True, autoincrement=True)
    source = Column(String(32), nullable=False, index=True)
    input_data = Column(Text, nullable=True)
    output_data = Column(Text, nullable=True)
    disaster_type = Column(String(64), nullable=True)
    risk_level = Column(String(16), nullable=True)
    confidence = Column(Float, nullable=True)
    latency_ms = Column(Integer, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow, index=True)


class RiskZoneModel(Base):
    __tablename__ = "risk_zones"
    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(256), nullable=False)
    severity = Column(String(16), nullable=False, index=True)
    zone_type = Column(String(64), nullable=True)
    geometry = Column(Text, nullable=False)  # GeoJSON string
    description = Column(Text, nullable=True)
    updated_at = Column(DateTime, default=datetime.utcnow)


# Engine & Session Setup

_DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./disaster.db")

try:
    connect_args = {"check_same_thread": False} if "sqlite" in _DATABASE_URL else {}
    engine = create_engine(_DATABASE_URL, connect_args=connect_args)
    SessionLocal = sessionmaker(bind=engine, autoflush=False, autocommit=False)
    Base.metadata.create_all(bind=engine)
    print(f"[db] Database initialized with {_DATABASE_URL}")
except Exception as e:
    print(f"[db] Database init error ({e}). Falling back to memory/mock.")
    engine = None
    SessionLocal = None


def _get_session() -> Optional[Session]:
    if SessionLocal is None:
        return None
    return SessionLocal()


# Default Risk Zones (if table is empty)
DEFAULT_RISK_ZONES = [
    {
        "name": "Bay of Bengal Coastal Strip",
        "severity": "CRITICAL",
        "zone_type": "coastal",
        "geometry": {"type": "Polygon", "coordinates": [[[85, 15], [92, 15], [92, 22], [85, 22], [85, 15]]]},
        "description": "High cyclone and storm surge risk along the Bay of Bengal coastline"
    },
    {
        "name": "Indo-Gangetic Flood Plain",
        "severity": "HIGH",
        "zone_type": "flood_plain",
        "geometry": {"type": "Polygon", "coordinates": [[[75, 24], [88, 24], [88, 30], [75, 30], [75, 24]]]},
        "description": "Monsoon flood-prone alluvial plain — annual inundation risk"
    },
    {
        "name": "Western Ghats Fire Zone",
        "severity": "HIGH",
        "zone_type": "fire_risk",
        "geometry": {"type": "Polygon", "coordinates": [[[74, 8], [78, 8], [78, 21], [74, 21], [74, 8]]]},
        "description": "Dense forest cover with high wildfire risk in dry season"
    },
    {
        "name": "Himalayan Seismic Belt",
        "severity": "MEDIUM",
        "zone_type": "seismic",
        "geometry": {"type": "Polygon", "coordinates": [[[72, 27], [97, 27], [97, 36], [72, 36], [72, 27]]]},
        "description": "Active tectonic zone with moderate to high earthquake probability"
    },
    {
        "name": "Rajasthan Drought Zone",
        "severity": "MEDIUM",
        "zone_type": "drought",
        "geometry": {"type": "Polygon", "coordinates": [[[69, 24], [78, 24], [78, 30], [69, 30], [69, 24]]]},
        "description": "Arid region with persistent drought and heat wave risk"
    }
]


# Query Functions

def get_recent_disasters(limit: int = 100) -> list[dict]:
    """Return the most recent disaster records ordered by created_at DESC."""
    db = _get_session()
    if db is None:
        return []

    try:
        records = (
            db.query(DisasterModel)
            .order_by(DisasterModel.created_at.desc())
            .limit(limit)
            .all()
        )
        return [
            {
                "id": r.id,
                "disaster_type": r.disaster_type,
                "severity_score": r.severity_score,
                "risk_level": r.risk_level,
                "population_at_risk": r.population_at_risk,
                "confidence": r.confidence,
                "latitude": r.latitude,
                "longitude": r.longitude,
                "location_name": r.location_name,
                "country": r.country,
                "created_at": r.created_at.isoformat() if r.created_at else None,
            }
            for r in records
        ]
    except Exception as e:
        print(f"[db.get_recent_disasters] Error: {e}")
        return []
    finally:
        db.close()


def save_prediction(
    source: str,
    input_data: dict,
    output_data: dict,
    disaster_type: Optional[str] = None,
    risk_level: Optional[str] = None,
    confidence: Optional[float] = None,
    latency_ms: Optional[int] = None,
) -> Optional[int]:
    """Log a model inference call to the predictions table. Returns the new row ID."""
    db = _get_session()
    if db is None:
        return None

    try:
        record = PredictionModel(
            source=source,
            input_data=json.dumps(input_data),
            output_data=json.dumps(output_data),
            disaster_type=disaster_type,
            risk_level=risk_level,
            confidence=confidence,
            latency_ms=latency_ms,
        )
        db.add(record)
        db.commit()
        db.refresh(record)
        return record.id
    except Exception as e:
        db.rollback()
        print(f"[db.save_prediction] Error: {e}")
        return None
    finally:
        db.close()


def get_risk_zones() -> list[dict]:
    """Return all risk zones with their geometry as GeoJSON dicts."""
    db = _get_session()
    if db is None:
        return DEFAULT_RISK_ZONES

    try:
        zones = db.query(RiskZoneModel).all()
        if not zones:
            # Seed default zones
            for item in DEFAULT_RISK_ZONES:
                db.add(RiskZoneModel(
                    name=item["name"],
                    severity=item["severity"],
                    zone_type=item["zone_type"],
                    geometry=json.dumps(item["geometry"]),
                    description=item["description"],
                ))
            db.commit()
            zones = db.query(RiskZoneModel).all()

        severity_order = {"CRITICAL": 1, "HIGH": 2, "MEDIUM": 3, "LOW": 4}
        results = []
        for z in zones:
            try:
                geom = json.loads(z.geometry) if isinstance(z.geometry, str) else z.geometry
            except Exception:
                geom = {}
            results.append({
                "id": z.id,
                "name": z.name,
                "severity": z.severity,
                "zone_type": z.zone_type,
                "description": z.description,
                "geometry": geom,
            })
        
        results.sort(key=lambda x: severity_order.get(x["severity"], 5))
        return results
    except Exception as e:
        print(f"[db.get_risk_zones] Error: {e}")
        return DEFAULT_RISK_ZONES
    finally:
        db.close()


def get_analytics_summary() -> dict:
    """Return aggregated stats for the Dashboard and Analytics pages."""
    db = _get_session()
    if db is None:
        return _fallback_analytics()

    try:
        records = db.query(DisasterModel).all()
        if not records:
            return _fallback_analytics()

        total = len(records)
        critical = sum(1 for r in records if r.risk_level == "CRITICAL")
        high = sum(1 for r in records if r.risk_level == "HIGH")
        medium = sum(1 for r in records if r.risk_level == "MEDIUM")
        low = sum(1 for r in records if r.risk_level == "LOW")

        avg_conf = sum(r.confidence for r in records) / total if total > 0 else 0.85
        avg_sev = sum(r.severity_score for r in records) / total if total > 0 else 0.60

        # Group by disaster type
        type_counts: dict[str, int] = {}
        for r in records:
            dtype = r.disaster_type or "unknown"
            type_counts[dtype] = type_counts.get(dtype, 0) + 1
        
        by_type = [
            {"name": name, "count": count}
            for name, count in sorted(type_counts.items(), key=lambda x: x[1], reverse=True)[:8]
        ]

        # Monthly severity
        monthly_map: dict[str, list[float]] = {}
        month_names = ["Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"]
        for r in records:
            if r.created_at:
                m_str = month_names[r.created_at.month - 1]
                monthly_map.setdefault(m_str, []).append(r.severity_score * 100)
        
        monthly_severity = [
            {"month": m, "value": round(sum(scores) / len(scores), 1)}
            for m, scores in monthly_map.items()
        ]
        if not monthly_severity:
            monthly_severity = _fallback_analytics()["monthly_severity"]

        return {
            "total_incidents": total,
            "critical_count": critical,
            "high_count": high,
            "medium_count": medium,
            "low_count": low,
            "avg_confidence": round(avg_conf, 3),
            "avg_severity": round(avg_sev, 3),
            "by_type": by_type,
            "monthly_severity": monthly_severity,
        }
    except Exception as e:
        print(f"[db.get_analytics_summary] Error: {e}")
        return _fallback_analytics()
    finally:
        db.close()


def _fallback_analytics() -> dict:
    """Static fallback used when DB is empty."""
    return {
        "total_incidents": 124,
        "critical_count": 18,
        "high_count": 34,
        "medium_count": 55,
        "low_count": 17,
        "avg_confidence": 0.87,
        "avg_severity": 0.62,
        "by_type": [
            {"name": "flood", "count": 56},
            {"name": "wildfire", "count": 32},
            {"name": "earthquake", "count": 20},
            {"name": "cyclone", "count": 16},
        ],
        "monthly_severity": [
            {"month": "Jan", "value": 45},
            {"month": "Feb", "value": 62},
            {"month": "Mar", "value": 55},
            {"month": "Apr", "value": 80},
            {"month": "May", "value": 70},
            {"month": "Jun", "value": 58},
        ],
    }
