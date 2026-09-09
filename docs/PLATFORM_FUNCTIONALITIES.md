# 🌍 AI Disaster Intelligence Platform — Comprehensive Functionalities

**Version:** 2.0.0  
**Stack:** Python · FastAPI · React · Leaflet.js · SQLite (SQLAlchemy) · MongoDB · Groq Cloud (`openai/gpt-oss-20b`) · EfficientNet-B0 · DistilBERT · XGBoost

---

## 1. Executive Overview
The **AI Disaster Intelligence Platform** is an end-to-end, multi-modal emergency intelligence and early warning system. It aggregates real-time signals from **satellite imagery**, **social media intelligence (Twitter/X)**, **meteorological forecasts**, and a **retrieval-augmented domain knowledge base** into a unified operational dashboard.

---

## 2. Core Functional Modules

### 📍 1. Interactive GIS Risk Map & Spatial Intelligence
* **Live Incident Mapping:** Visualizes active and historical disaster events across regions using Leaflet.js and OpenStreetMap.
* **Color-Coded Severity Pinpoints:**
  * 🔴 **CRITICAL** (Severity > 0.80)
  * 🟠 **HIGH** (Severity 0.60 – 0.80)
  * 🟡 **MEDIUM** (Severity 0.40 – 0.60)
  * 🟢 **LOW** (Severity < 0.40)
* **Geographic Risk Zone Overlays:** Bounding box and GeoJSON polygon overlays for high-risk zones:
  * *Bay of Bengal Coastal Strip* (Cyclone & Storm Surge)
  * *Indo-Gangetic Flood Plain* (Monsoon Inundation)
  * *Western Ghats Fire Zone* (Wildfire Risk)
  * *Himalayan Seismic Belt* (Earthquake Probability)
  * *Rajasthan Drought Zone* (Arid & Heatwave)
* **Real-time Incident Drill-down:** Clicking any pin displays localized severity, population at risk, confidence score, and timestamp.

---

### 🛰️ 2. Satellite Computer Vision Analysis
* **Model:** Deep Convolutional Neural Network (**EfficientNet-B0** in PyTorch).
* **Task:** 4-class visual detection from aerial / drone / satellite feeds:
  * `Cyclone`
  * `Earthquake`
  * `Flood`
  * `Wildfire`
* **Features:**
  * Accepts raw image uploads or external sensor feeds.
  * Outputs per-class probability distribution and primary disaster classification.
  * Sub-second inference latency.

---

### 📱 3. Social Media & Tweet Intelligence (NLP)
* **Model:** Fine-tuned **DistilBERT** (`DistilBertForSequenceClassification`).
* **Task:** 6-class NLP text classification & urgency score calculation:
  * `Drought`, `Earthquake`, `Floods`, `Hurricanes`, `Tornadoes`, `Wildfire`
* **Features:**
  * Filters out noise and false alarms.
  * Extracts situational urgency scores (0.0 to 1.0) based on casualty mentions, trapped individuals, and SOS keywords.
  * Automatic keyword-based fallback engine if network/model weights are cold.

---

### 🌦️ 4. Weather Risk Forecasting
* **Model:** **XGBoost Classifier** trained on tabular time-series lag features.
* **Features Analyzed:**
  * Precipitation (1-day, 3-day, 7-day, 14-day rolling means and max)
  * Wind speed and extreme wind gusts (km/h)
  * Maximum & minimum temperature trends (°C)
* **Output:** Quantified probability score of imminent disaster occurrence.

---

### ⚖️ 5. Multi-Model Decision Fusion Engine
* **Algorithm:** Weighted ensemble mathematical model:
  $$\text{Severity} = 0.40 \times \text{Satellite} + 0.35 \times \text{NLP} + 0.25 \times \text{Weather}$$
* **Functionality:**
  * Combines weak signals from multiple independent data silos.
  * Categorizes composite severity into `CRITICAL`, `HIGH`, `MEDIUM`, or `LOW`.
  * Computes overall confidence score and estimates population at risk.

---

### 📑 6. RAG Situation Report Generator (Groq Cloud LLM)
* **Engine:** **Groq Cloud API** (`openai/gpt-oss-20b` / `llama-3.1-8b-instant`) + **MongoDB / Local Dense Embeddings** (`all-MiniLM-L6-v2`).
* **Functionality:**
  * Semantically searches domain disaster management articles, evacuation guidelines, and triage SOPs.
  * Automatically drafts a comprehensive, actionable Markdown Situation Report within ~2–5 seconds.
  * Generates structured sections:
    1. **Executive Summary**
    2. **Risk Assessment Table** (threats, current status, escalation probability, mitigation priorities)
    3. **Affected Zones & Vulnerable Infrastructure**
    4. **Recommended Actions** (Immediate 0–6h, Short-term 6–24h)
    5. **Critical Resource Mobilization** (SAR units, field hospitals, evacuation vehicles)
  * Built-in template fallback for 100% offline uptime guarantee.

---

### 📊 7. Analytics & Incident Feed
* **Incident Metrics:** Tracks total incident count (50,000+ seeded records), severity distributions, and model confidence scores.
* **Breakdown by Disaster Type:** Instant aggregation across Floods, Wildfires, Earthquakes, Cyclones, Landslides, and Droughts.
* **Monthly Severity Trends:** Historical trend lines displaying seasonal peak risk months.

---

### 💾 8. Persistence & Data Layer
* **SQL Database:** Simple SQLAlchemy with **SQLite** (`disaster.db`) — zero server setup, standalone portability.
* **Document & Vector Store:** **MongoDB** (`pymongo`) for flexible disaster knowledge chunks, situation report archives, and vector embeddings.
* **Audit Log:** Logs all model inference requests, latency metrics, inputs, and outputs to the `predictions` table for auditing and performance tracking.

---

## 3. REST API Reference

| Endpoint | Method | Description |
|---|---|---|
| `/health` | `GET` | System health check and API version verification |
| `/disasters` | `GET` | Fetches recent disaster incidents with coordinates & severity |
| `/risk-zones` | `GET` | Returns geographic risk zone polygons with GeoJSON |
| `/analytics/summary` | `GET` | Aggregated statistical metrics and incident counts |
| `/predict/disaster` | `POST` | Multi-modal disaster prediction from weather & social signals |
| `/predict/satellite` | `POST` | Aerial image classification via EfficientNet-B0 |
| `/predict/tweet` | `POST` | Disaster NLP classification and urgency scoring |
| `/predict/weather` | `POST` | Weather risk forecasting via XGBoost |
| `/situation-report` | `POST` | AI-generated RAG situation report via Groq Cloud |
| `/docs` | `GET` | Interactive OpenAPI Swagger UI documentation |

---

## 4. Operational Links

* 🌐 **Frontend Dashboard:** [http://localhost:3000](http://localhost:3000)
* 📡 **FastAPI Backend & Swagger Docs:** [http://localhost:8000/docs](http://localhost:8000/docs)
* 🩺 **Backend Health Check:** [http://localhost:8000/health](http://localhost:8000/health)
