"""
Text Chunker

Reads Wikipedia .txt files from rag/corpus/ and splits them into
500-700 token chunks with overlap. Saves the chunk list as rag/chunks.json.

Run after scraper.py:
    python rag/chunker.py
"""

import json
import pathlib

ROOT       = pathlib.Path(__file__).resolve().parent
CORPUS_DIR = ROOT / "corpus"
CHUNKS_OUT = ROOT / "chunks.json"

CHUNK_SIZE    = 600   # tokens (approx — we use character-based splitting × 4)
CHUNK_OVERLAP = 80    # token overlap between consecutive chunks


def chunk_all():
    try:
        from langchain_text_splitters import RecursiveCharacterTextSplitter
    except ImportError:
        print("[chunker] Install:  pip install langchain-text-splitters")
        return

    splitter = RecursiveCharacterTextSplitter(
        chunk_size=CHUNK_SIZE * 4,       # ~4 chars per token
        chunk_overlap=CHUNK_OVERLAP * 4,
        separators=["\n\n", "\n", ". ", " ", ""],
        length_function=len,
    )

    txt_files = sorted(CORPUS_DIR.glob("*.txt"))
    if not txt_files:
        print(f"[chunker] No .txt files in {CORPUS_DIR}. Run rag/scraper.py first.")
        return

    all_chunks = []
    for txt_path in txt_files:
        text   = txt_path.read_text(encoding="utf-8")
        chunks = splitter.split_text(text)
        source = txt_path.stem.replace("_", " ").title()

        for i, chunk in enumerate(chunks):
            all_chunks.append({
                "id":     f"{txt_path.stem}_{i}",
                "source": source,
                "text":   chunk,
            })

        print(f"  {txt_path.name}: {len(chunks)} chunks")

    CHUNKS_OUT.write_text(json.dumps(all_chunks, indent=2, ensure_ascii=False), encoding="utf-8")
    print(f"\n[chunker] Done. {len(all_chunks)} total chunks → {CHUNKS_OUT}")


if __name__ == "__main__":
    chunk_all()
