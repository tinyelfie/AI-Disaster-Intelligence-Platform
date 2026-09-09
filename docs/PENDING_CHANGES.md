# 📋 Pending Architectural Enhancements & Tasks

## 1. RAG LLM Migration: Gemini 1.5 Flash ➔ Groq Cloud (`llama-3.1-8b-instant`)

### Objective
Replace / augment the Gemini 1.5 Flash generator in the RAG pipeline with **Groq Cloud API** to avoid quota limitations and achieve ultra-low latency response generation for disaster situation reports.

### Implementation Details
- Add `groq` package to [`requirements.txt`](file:///d:/MyProjectsForFun/disaster%20intelligence/requirements.txt).
- Add `GROQ_API_KEY` to [`.env.example`](file:///d:/MyProjectsForFun/disaster%20intelligence/.env.example) and [`.env`](file:///d:/MyProjectsForFun/disaster%20intelligence/.env).
- Update [`rag/generator.py`](file:///d:/MyProjectsForFun/disaster%20intelligence/rag/generator.py) to use Groq with fallback safety.
- Status: *Scheduled*

---

## 2. Database Simplification: PostgreSQL + PostGIS ➔ Simple SQLAlchemy (SQLite / File DB)

### Objective
Remove PostgreSQL and PostGIS requirements to allow zero-configuration, self-contained persistence using standard SQLAlchemy with SQLite (e.g. `disaster.db`).

### Implementation Details
- Remove `psycopg2-binary` and `GeoAlchemy2` dependencies from [`requirements.txt`](file:///d:/MyProjectsForFun/disaster%20intelligence/requirements.txt).
- Simplify [`database/schema.sql`](file:///d:/MyProjectsForFun/disaster%20intelligence/database/schema.sql) and [`database/db.py`](file:///d:/MyProjectsForFun/disaster%20intelligence/database/db.py) to use standard SQLAlchemy 2.0 ORM models without PostGIS extensions (storing coordinates/bounds as standard floats or JSON).
- Set default `DATABASE_URL=sqlite:///./disaster.db` in [`.env.example`](file:///d:/MyProjectsForFun/disaster%20intelligence/.env.example).
- Status: *Scheduled*

---

## 3. Vector & Document Store Migration: ChromaDB ➔ MongoDB

### Objective
Replace ChromaDB with **MongoDB** (using `pymongo`) for storing disaster knowledge corpora, embeddings, situation reports, and incident documents.

### Implementation Details
- Add `pymongo` to [`requirements.txt`](file:///d:/MyProjectsForFun/disaster%20intelligence/requirements.txt).
- Add `MONGO_URI` (e.g. `mongodb://localhost:27017` or MongoDB Atlas URI) and `MONGO_DB_NAME=disaster_intelligence` to [`.env.example`](file:///d:/MyProjectsForFun/disaster%20intelligence/.env.example).
- Replace [`rag/embedder.py`](file:///d:/MyProjectsForFun/disaster%20intelligence/rag/embedder.py) and [`rag/retriever.py`](file:///d:/MyProjectsForFun/disaster%20intelligence/rag/retriever.py) ChromaDB client logic with MongoDB document collection & vector similarity lookup / text search.
- Remove `chromadb` dependency from [`requirements.txt`](file:///d:/MyProjectsForFun/disaster%20intelligence/requirements.txt).
- Status: *Scheduled*
