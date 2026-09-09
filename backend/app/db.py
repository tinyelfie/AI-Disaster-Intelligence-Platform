"""
Backend DB module

Exposes SQLAlchemy engine, Base, and SessionLocal configured for SQLite and standard SQL.
"""
import os
import pathlib

ROOT = pathlib.Path(__file__).resolve().parents[2]

try:
    from dotenv import load_dotenv
    load_dotenv(ROOT / ".env")
except ImportError:
    pass

from database.db import engine, SessionLocal, Base, DisasterModel, PredictionModel, RiskZoneModel

__all__ = ["engine", "SessionLocal", "Base", "DisasterModel", "PredictionModel", "RiskZoneModel"]
