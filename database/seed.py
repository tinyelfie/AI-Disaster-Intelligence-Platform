"""
Database Seeder

Reads data/raw/weather/global_disaster_events.csv and inserts rows
into the disasters table so the map and analytics are populated on first run.

Usage:
    python database/seed.py
"""

import os
import sys
import pathlib
import random
from datetime import datetime, timezone

ROOT = pathlib.Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

# Load .env if present
try:
    from dotenv import load_dotenv
    load_dotenv(ROOT / ".env")
except ImportError:
    pass

from database.db import engine, Base, DisasterModel, get_risk_zones

CSV_PATH = ROOT / "data" / "raw" / "weather" / "Disaster & Emergency Response Dataset" / "global_disaster_events.csv"
if not CSV_PATH.exists():
    CSV_PATH = ROOT / "data" / "raw" / "weather" / "global_disaster_events.csv"

COL_ALIASES = {
    "disaster_type": ["disaster_type", "Disaster Type", "type", "Type"],
    "year":          ["year", "Year", "Start Year", "date"],
    "country":       ["country", "Country", "Location", "location"],
    "deaths":        ["casualties", "Total Deaths", "deaths", "Deaths", "No. Deaths"],
    "affected":      ["population_at_risk", "Total Affected", "affected", "No. Affected"],
    "latitude":      ["latitude", "Latitude", "lat"],
    "longitude":     ["longitude", "Longitude", "lon", "lng"],
}

COUNTRY_CENTROIDS = {
    "India":       (20.59, 78.96),
    "Bangladesh":  (23.68, 90.35),
    "Indonesia":   (-0.79, 113.92),
    "Philippines": (12.88, 121.77),
    "China":       (35.86, 104.19),
    "Pakistan":    (30.37, 69.35),
    "Nepal":       (28.39, 84.12),
    "Myanmar":     (21.91, 95.96),
    "Vietnam":     (14.05, 108.27),
    "Japan":       (36.20, 138.25),
}
DEFAULT_CENTER = (20.0, 78.0)


def resolve_col(df, aliases):
    for alias in aliases:
        if alias in df.columns:
            return alias
    return None


def seed():
    try:
        import pandas as pd
        from sqlalchemy.orm import sessionmaker
    except ImportError:
        print("[seed] Install: pip install pandas sqlalchemy")
        return

    if engine is None:
        print("[seed] No database engine available. Skipping seed.")
        return

    # Ensure tables exist and default risk zones are seeded
    Base.metadata.create_all(bind=engine)
    get_risk_zones()

    Session = sessionmaker(bind=engine)
    session = Session()

    # Clear existing seeded data
    session.query(DisasterModel).filter(DisasterModel.description.like("Seeded%")).delete(synchronize_session=False)
    session.commit()

    if not CSV_PATH.exists():
        print(f"[seed] {CSV_PATH} not found. Creating sample seed records...")
        sample_disasters = [
            {"type": "flood", "sev": 0.85, "risk": "CRITICAL", "pop": 45000, "lat": 26.20, "lon": 92.93, "loc": "Assam, India"},
            {"type": "cyclone", "sev": 0.90, "risk": "CRITICAL", "pop": 120000, "lat": 19.81, "lon": 85.83, "loc": "Odisha Coast, India"},
            {"type": "wildfire", "sev": 0.75, "risk": "HIGH", "pop": 15000, "lat": 11.68, "lon": 76.63, "loc": "Bandipur, India"},
            {"type": "earthquake", "sev": 0.70, "risk": "HIGH", "pop": 35000, "lat": 30.06, "lon": 79.01, "loc": "Garhwal, India"},
            {"type": "drought", "sev": 0.45, "risk": "MEDIUM", "pop": 80000, "lat": 26.91, "lon": 75.78, "loc": "Rajasthan, India"},
        ]
        for s in sample_disasters:
            session.add(DisasterModel(
                disaster_type=s["type"],
                severity_score=s["sev"],
                risk_level=s["risk"],
                population_at_risk=s["pop"],
                confidence=0.88,
                latitude=s["lat"],
                longitude=s["lon"],
                location_name=s["loc"],
                country="India",
                description="Seeded sample baseline disaster",
                created_at=datetime.utcnow(),
            ))
        session.commit()
        session.close()
        print("[seed] Done. Inserted sample disaster records.")
        return

    df = pd.read_csv(CSV_PATH, encoding="latin1", low_memory=False)
    print(f"[seed] Loaded {len(df)} rows from {CSV_PATH.name}")

    col = {k: resolve_col(df, v) for k, v in COL_ALIASES.items()}

    inserted = 0
    skipped = 0

    for _, row in df.iterrows():
        try:
            dtype = str(row[col["disaster_type"]]).strip().lower() if col["disaster_type"] else "unknown"
            year_val = row[col["year"]] if col["year"] and pd.notna(row[col["year"]]) else 2024
            
            try:
                if isinstance(year_val, str) and "-" in year_val:
                    year = int(year_val.split("-")[0])
                else:
                    year = int(year_val)
            except Exception:
                year = 2024

            country = str(row[col["country"]]).strip() if col["country"] and pd.notna(row[col["country"]]) else "India"

            lat = float(row[col["latitude"]]) if col["latitude"] and pd.notna(row.get(col["latitude"])) else None
            lng = float(row[col["longitude"]]) if col["longitude"] and pd.notna(row.get(col["longitude"])) else None

            if lat is None or lng is None:
                c = COUNTRY_CENTROIDS.get(country, DEFAULT_CENTER)
                lat = c[0] + random.uniform(-2.0, 2.0)
                lng = c[1] + random.uniform(-2.0, 2.0)

            deaths = float(row[col["deaths"]]) if col["deaths"] and pd.notna(row.get(col["deaths"])) else 0
            affected = float(row[col["affected"]]) if col["affected"] and pd.notna(row.get(col["affected"])) else 0

            if deaths > 1000 or affected > 100000:
                risk_level = "CRITICAL"
                severity = 0.90
            elif deaths > 100 or affected > 10000:
                risk_level = "HIGH"
                severity = 0.70
            elif deaths > 10 or affected > 1000:
                risk_level = "MEDIUM"
                severity = 0.50
            else:
                risk_level = "LOW"
                severity = 0.25

            ts = datetime(min(max(year, 2000), 2026), random.randint(1, 12), random.randint(1, 28))

            session.add(DisasterModel(
                disaster_type=dtype,
                severity_score=severity,
                risk_level=risk_level,
                population_at_risk=int(affected) if affected > 0 else random.randint(1000, 50000),
                confidence=round(random.uniform(0.75, 0.95), 2),
                latitude=round(lat, 6),
                longitude=round(lng, 6),
                location_name=country,
                country=country,
                description=f"Seeded from historical record — {year}",
                created_at=ts,
            ))
            inserted += 1

        except Exception as e:
            skipped += 1
            continue

    session.commit()
    session.close()
    print(f"[seed] Done. Inserted {inserted} rows, skipped {skipped}.")


if __name__ == "__main__":
    seed()
