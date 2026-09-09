"""
RAG Retriever — MongoDB & Semantic Vector Search

Given a query string, retrieves the top-k most relevant disaster knowledge chunks
from the MongoDB vector store (or embedded local cache).

Usage:
    from rag.retriever import retrieve
    chunks = retrieve("flooding in river delta", k=5)
"""

import os
import json
import pathlib
import sys
import numpy as np
from typing import Optional

ROOT = pathlib.Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

try:
    from dotenv import load_dotenv
    load_dotenv(ROOT / ".env")
except ImportError:
    pass

CHUNKS_JSON     = ROOT / "rag" / "chunks.json"
CHUNKS_EMBEDDED = ROOT / "rag" / "chunks_embedded.json"
MONGO_URI       = os.getenv("MONGO_URI", "mongodb://localhost:27017")
MONGO_DB_NAME   = os.getenv("MONGO_DB_NAME", "disaster_intelligence")
COLLECTION_NAME = "disaster_knowledge"
EMBED_MODEL     = "all-MiniLM-L6-v2"

# Lazy singletons
_embedder       = None
_mongo_client   = None
_cached_docs    = None


def _get_embedder():
    global _embedder
    if _embedder is None:
        try:
            from sentence_transformers import SentenceTransformer
            _embedder = SentenceTransformer(EMBED_MODEL)
        except Exception as e:
            print(f"[retriever] Could not load sentence-transformers: {e}")
            _embedder = False
    return _embedder if _embedder is not False else None


def _load_documents() -> list[dict]:
    """Fetch documents from MongoDB, or fallback to local chunks_embedded.json / chunks.json."""
    global _mongo_client, _cached_docs
    if _cached_docs is not None:
        return _cached_docs

    # 1. Try MongoDB
    try:
        import pymongo
        if _mongo_client is None:
            _mongo_client = pymongo.MongoClient(MONGO_URI, serverSelectionTimeoutMS=1500)
        db = _mongo_client[MONGO_DB_NAME]
        coll = db[COLLECTION_NAME]
        docs = list(coll.find({}, {"_id": 0}))
        if docs:
            _cached_docs = docs
            return docs
    except Exception:
        pass

    # 2. Try local embedded cache
    if CHUNKS_EMBEDDED.exists():
        try:
            _cached_docs = json.loads(CHUNKS_EMBEDDED.read_text(encoding="utf-8"))
            return _cached_docs
        except Exception:
            pass

    # 3. Fallback to raw chunks.json
    if CHUNKS_JSON.exists():
        try:
            raw = json.loads(CHUNKS_JSON.read_text(encoding="utf-8"))
            _cached_docs = [{"chunk_id": c.get("id"), "source": c.get("source"), "text": c.get("text"), "embedding": None} for c in raw]
            return _cached_docs
        except Exception:
            pass

    return []


def retrieve(query: str, k: int = 5) -> list[dict]:
    """
    Retrieve top-k relevant chunks for a query using semantic vector search.

    Returns:
        List of dicts: [{"text": ..., "source": ..., "distance": ...}, ...]
    """
    docs = _load_documents()
    if not docs:
        return []

    embedder = _get_embedder()

    # If embedder is available and docs have embeddings, do cosine similarity
    if embedder is not None and docs and docs[0].get("embedding") is not None:
        try:
            q_emb = embedder.encode([query])[0]
            q_emb = q_emb / (np.linalg.norm(q_emb) + 1e-9)

            doc_embs = np.array([d["embedding"] for d in docs])
            # Normalize doc embeddings
            norms = np.linalg.norm(doc_embs, axis=1, keepdims=True) + 1e-9
            doc_embs = doc_embs / norms

            sims = np.dot(doc_embs, q_emb)
            top_indices = np.argsort(sims)[::-1][:k]

            results = []
            for idx in top_indices:
                score = float(sims[idx])
                results.append({
                    "text": docs[idx]["text"],
                    "source": docs[idx].get("source", "Knowledge Base"),
                    "distance": round(1.0 - score, 4),
                })
            return results
        except Exception as e:
            print(f"[retriever] Vector search error: {e}")

    # Fallback to keyword matching
    terms = set(query.lower().split())
    scored = []
    for d in docs:
        text = d.get("text", "")
        count = sum(1 for t in terms if t in text.lower())
        scored.append((count, d))
    
    scored.sort(key=lambda x: x[0], reverse=True)
    return [
        {
            "text": item[1]["text"],
            "source": item[1].get("source", "Knowledge Base"),
            "distance": 0.5,
        }
        for item in scored[:k]
    ]
