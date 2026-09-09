"""
Wikipedia Corpus Scraper

Scrapes 10 disaster-related Wikipedia articles and saves them as .txt files
in rag/corpus/. Run once before building the vector store.

Usage:
    python rag/scraper.py
"""

import pathlib
import time

ROOT       = pathlib.Path(__file__).resolve().parent
CORPUS_DIR = ROOT / "corpus"

# 10 Wikipedia article titles to form the RAG knowledge base
ARTICLES = [
    "Natural disaster",
    "Flood",
    "Wildfire",
    "Earthquake",
    "Tropical cyclone",
    "Tsunami",
    "Landslide",
    "Drought",
    "Disaster response",
    "Emergency management",
]


def scrape_all():
    try:
        import wikipedia
    except ImportError:
        print("[scraper] Install wikipedia-python first:  pip install wikipedia-api")
        return

    CORPUS_DIR.mkdir(parents=True, exist_ok=True)
    wikipedia.set_lang("en")

    for title in ARTICLES:
        safe_name = title.lower().replace(" ", "_") + ".txt"
        out_path  = CORPUS_DIR / safe_name

        if out_path.exists():
            print(f"  [skip] {title} (already scraped)")
            continue

        try:
            page    = wikipedia.page(title, auto_suggest=False)
            content = f"# {page.title}\n\n{page.content}"
            out_path.write_text(content, encoding="utf-8")
            print(f"  [ok]   {title} → {out_path.name}  ({len(content):,} chars)")
        except wikipedia.exceptions.DisambiguationError as e:
            # Take the first suggestion
            try:
                page    = wikipedia.page(e.options[0], auto_suggest=False)
                content = f"# {page.title}\n\n{page.content}"
                out_path.write_text(content, encoding="utf-8")
                print(f"  [ok]   {title} (→ {e.options[0]}) → {out_path.name}")
            except Exception as inner:
                print(f"  [err]  {title}: {inner}")
        except Exception as exc:
            print(f"  [err]  {title}: {exc}")

        time.sleep(0.5)  # be polite to Wikipedia servers

    saved = list(CORPUS_DIR.glob("*.txt"))
    print(f"\n[scraper] Done. {len(saved)} articles in {CORPUS_DIR}")


if __name__ == "__main__":
    scrape_all()
