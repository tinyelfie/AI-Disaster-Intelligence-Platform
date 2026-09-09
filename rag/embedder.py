"""
Vector & Document Store Builder — MongoDB + SentenceTransformers

Embeds all text chunks from rag/chunks.json using sentence-transformers
(all-MiniLM-L6-v2) and indexes them into MongoDB (collection: disaster_knowledge).

Usage:
    python rag/embedder.py
"""

import os
import json
import pathlib
import sys
import numpy as np

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


def build_vector_store():
    if not CHUNKS_JSON.exists():
        print(f"[embedder] {CHUNKS_JSON} not found. Run rag/chunker.py first.")
        return

    try:
        from sentence_transformers import SentenceTransformer
    except ImportError:
        print("[embedder] Install: pip install sentence-transformers")
        return

    chunks = json.loads(CHUNKS_JSON.read_text(encoding="utf-8"))
    if not chunks:
        print("[embedder] No chunks found in chunks.json.")
        return

    print(f"[embedder] Loading embedding model: {EMBED_MODEL} ...")
    embedder = SentenceTransformer(EMBED_MODEL)

    texts = [c["text"] for c in chunks]
    print(f"[embedder] Embedding {len(texts)} chunks ...")
    embeddings = embedder.encode(texts, show_progress_bar=True, batch_size=32).tolist()

    docs = []
    for chunk, emb in zip(chunks, embeddings):
        docs.append({
            "chunk_id": chunk.get("id", ""),
            "source": chunk.get("source", "Knowledge Base"),
            "text": chunk.get("text", ""),
            "embedding": emb,
        })

    # 1. Save local embedded backup cache
    CHUNKS_EMBEDDED.write_text(json.dumps(docs, ensure_ascii=False), encoding="utf-8")
    print(f"[embedder] Saved local embedded cache to {CHUNKS_EMBEDDED.name}")

    # 2. Index into MongoDB
    try:
        import pymongo
        client = pymongo.MongoClient(MONGO_URI, serverSelectionTimeoutMS=3000)
        # Test connection
        client.admin.command('ping')
        db = client[MONGO_DB_NAME]
        coll = db[COLLECTION_NAME]

        # Recreate collection for fresh state
        coll.drop()
        coll.insert_many(docs)
        coll.create_index([("chunk_id", pymongo.ASCENDING)], unique=True)
        coll.create_index([("source", pymongo.ASCENDING)])

        print(f"[embedder] Successfully indexed {len(docs)} documents into MongoDB `{MONGO_DB_NAME}.{COLLECTION_NAME}` at {MONGO_URI}")
    except Exception as e:
        print(f"[embedder] Note: MongoDB connection skipped/unavailable ({e}). Local vector cache will be used.")

    print(f"\n[embedder] Done. {len(chunks)} chunks indexed.")


if __name__ == "__main__":
    build_vector_store()
