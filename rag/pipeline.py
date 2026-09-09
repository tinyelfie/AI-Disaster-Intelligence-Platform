"""
RAG Pipeline

Single public entry point for the backend.

Usage (backend):
    from rag.pipeline import generate_situation_report
    report = generate_situation_report(
        region="River Delta B7",
        severity="HIGH",
        disaster_type="flood"
    )
    # returns: markdown string
"""

from rag.retriever import retrieve
from rag.generator import generate


def generate_situation_report(
    region: str,
    severity: str,
    disaster_type: str,
    k: int = 5,
) -> str:
    """
    Full RAG pipeline: query -> retrieve context -> generate report.

    Args:
        region:        Affected geographic area
        severity:      CRITICAL | HIGH | MEDIUM | LOW
        disaster_type: e.g. "flood", "wildfire", "earthquake"
        k:             Number of context chunks to retrieve

    Returns:
        Markdown-formatted situation report string.
    """
    # Build a semantic search query from the event parameters
    query  = f"{disaster_type} disaster emergency response {region}"
    chunks = retrieve(query, k=k)

    report = generate(
        region=region,
        severity=severity,
        disaster_type=disaster_type,
        chunks=chunks,
    )
    return report
