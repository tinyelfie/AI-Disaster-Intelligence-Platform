# 🌍 AI Disaster Intelligence Platform

A full-stack AI-powered disaster monitoring and early-warning system.  
Combines **satellite imagery classification**, **NLP tweet analysis**, **weather risk forecasting**, and **RAG-augmented situation reports** into a single production-grade platform.

![Platform Preview](docs/preview.png)

---

## 🚀 Features

| Feature | Technology | Description |
|---|---|---|
| **Satellite Analysis** | EfficientNet-B0 | Classifies disaster type from aerial imagery |
| **Tweet Intelligence** | DistilBERT | Detects disaster signals + urgency from social media |
| **Weather Forecasting** | XGBoost | Predicts disaster risk from meteorological data |
| **Model Fusion** | Weighted ensemble | Combines all 3 models into a unified severity score |
| **RAG Reports** | ChromaDB + Gemini | Generates contextual situation reports from a Wikipedia knowledge base |
| **Live Map** | Leaflet.js | Color-coded incident markers + risk zone overlays |
| **Dashboard** | React | Real-time stats, incident feed, and system status |

---

## 🗂️ Project Structure

```
disaster-intelligence/
│
├── data/
│   ├── raw/satellite/          ← Rupak Roy Kaggle dataset (not committed)
│   ├── raw/tweets/             ← disaster_tweets.csv
│   ├── raw/weather/            ← history_latest.csv + global_disaster_events.csv
│   └── processed/              ← output of preprocess.py scripts
│
├── ml/
│   ├── satellite/              ← EfficientNet-B0 pipeline
│   ├── nlp/                    ← DistilBERT pipeline
│   ├── forecasting/            ← XGBoost pipeline
│   ├── fusion/                 ← Weighted ensemble logic (no model file)
│   └── inference/              ← Rule-based baseline for /predict/disaster
│
├── rag/
│   ├── scraper.py              ← Wikipedia scraper (run once)
│   ├── chunker.py              ← Text chunking (500–700 tokens)
│   ├── embedder.py             ← ChromaDB embedding store
│   ├── retriever.py            ← Semantic search
│   ├── generator.py            ← Gemini 1.5 Flash report generation
│   └── pipeline.py             ← Single public entry point for backend
│
├── database/
│   ├── schema.sql              ← PostgreSQL + PostGIS tables
│   ├── seed.py                 ← Seed from global_disaster_events.csv
│   └── db.py                   ← SQLAlchemy query functions + fallbacks
│
├── backend/
│   └── app/main.py             ← FastAPI (7 endpoints, all with mock fallbacks)
│
├── frontend/                   ← React + Leaflet premium dashboard
│
├── notebooks/                  ← 6 Jupyter notebooks (EDA + training)
│
├── models/                     ← Saved model files (not committed)
│
├── chroma_db/                  ← ChromaDB local store (auto-created)
│
├── requirements.txt
└── .env.example
```

---

## ⚡ Quick Start

### 1. Clone & Install

```bash
git clone https://github.com/your-username/ai-disaster-intelligence.git
cd ai-disaster-intelligence
pip install -r requirements.txt
```

### 2. Configure Environment

```bash
cp .env.example .env
# Edit .env — add your GEMINI_API_KEY and DATABASE_URL
```

### 3. Database Setup (optional, fallback data works without it)

```bash
# Start PostgreSQL + PostGIS
psql -U postgres -d disaster_intel -f database/schema.sql
python database/seed.py
```

### 4. Build the RAG Knowledge Base (optional, fallback works without it)

```bash
# Run in order — each script feeds the next
python rag/scraper.py      # scrape 10 Wikipedia articles → rag/corpus/
python rag/chunker.py      # chunk text → rag/corpus/chunks.json
python rag/embedder.py     # embed + store in chroma_db/
```

### 5. Start the Backend

```bash
cd ai-disaster-intelligence
uvicorn backend.app.main:app --reload --port 8000
```

Open: http://localhost:8000/docs (Swagger UI)

### 6. Start the Frontend

```bash
cd frontend
npm install
npm start
```

Open: http://localhost:3000  
Login: `admin` / `disaster123`

---

## 🤖 API Endpoints

| Method | Endpoint | Description |
|---|---|---|
| `GET` | `/health` | Server health check |
| `GET` | `/disasters` | Fetch recent disaster records for the map |
| `GET` | `/risk-zones` | Severity-classified geographic zones |
| `GET` | `/analytics/summary` | Aggregated stats for dashboard |
| `POST` | `/predict/disaster` | Rule-based composite disaster prediction |
| `POST` | `/predict/satellite` | Satellite image classification |
| `POST` | `/predict/tweet` | Tweet disaster classification |
| `POST` | `/predict/weather` | XGBoost weather risk forecasting |
| `POST` | `/situation-report` | RAG-augmented situation report (Gemini) |

All endpoints have **graceful mock fallbacks** — the frontend works even before any model is trained.

---

## 🧠 Model Training

Training happens in **Google Colab** using the notebooks. After training, download the model files and place them in `models/`.

| Notebook | Model | Output File |
|---|---|---|
| `02_satellite_training.ipynb` | EfficientNet-B0 | `models/satellite_model.pt` |
| `04_nlp_training.ipynb` | DistilBERT | `models/nlp_model/` (folder) |
| `06_forecasting_training.ipynb` | XGBoost | `models/xgboost_model.json` + scaler |

---

## 🗄️ Database Schema

Three tables in PostgreSQL + PostGIS:

- **`disasters`** — historical and real-time event records
- **`predictions`** — audit log of every ML inference call  
- **`risk_zones`** — GIS polygons with severity classification

---

## 🛠️ Tech Stack

**ML / AI:** PyTorch · HuggingFace Transformers · XGBoost · EfficientNet-B0 · DistilBERT  
**RAG:** ChromaDB · sentence-transformers · Gemini 1.5 Flash · Wikipedia  
**Backend:** FastAPI · Uvicorn · Pydantic · SQLAlchemy  
**Database:** PostgreSQL · PostGIS · psycopg2  
**Frontend:** React · Leaflet.js · Vanilla CSS  

---

## 📋 Dataset Credits

- **Satellite Images:** [Rupak Roy — Kaggle](https://www.kaggle.com/datasets/rupakroy/satellite-images-of-hurricane-damage)  
- **Disaster Tweets:** [NLP Getting Started — Kaggle](https://www.kaggle.com/competitions/nlp-getting-started)  
- **Weather Data:** `history_latest.csv` — historical global weather  
- **Disaster Events:** `global_disaster_events.csv`

---

## 📄 License

MIT License — see [LICENSE](LICENSE) for details.

---

*Built for portfolio demonstration. All model predictions should be validated before operational use.*