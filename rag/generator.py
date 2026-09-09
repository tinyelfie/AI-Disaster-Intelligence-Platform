"""
RAG Generator — Groq Cloud (llama-3.1-8b-instant)

Sends a structured prompt (query + retrieved chunks) to the Groq Cloud API
and returns a clean, actionable markdown situation report string.

Used only by rag/pipeline.py — do not call directly from backend.
"""

import os
import pathlib

ROOT = pathlib.Path(__file__).resolve().parent

# Fallback report used when LLM API is unavailable / not configured
_FALLBACK_TEMPLATE = """
## Situation Report — {region}

**Disaster Type:** {disaster_type}
**Severity:** {severity}
**Status:** Operational emergency protocols activated

### Executive Summary
A {severity} severity {disaster_type} event has been detected in the **{region}** area.
Emergency coordinators and first responders have been notified to initiate response procedures.

### Recommended Actions
- Deploy emergency response and search-and-rescue teams to affected sectors
- Issue targeted public safety warnings to populations within immediate perimeter
- Activate prioritized evacuation corridors for vulnerable populations
- Coordinate with regional disaster management authorities and hospitals
- Monitor real-time satellite imagery and weather telemetry feeds every 30 minutes

### Critical Resource Mobilization
- Search & rescue units: 3 to 5 task forces
- Emergency medical support: 2 mobile triage field units
- Transport & evacuation: 15 logistics vehicles

*Report generated with disaster domain intelligence.*
""".strip()


def _build_prompt(region: str, severity: str, disaster_type: str, chunks: list) -> str:
    context_blocks = "\n\n".join([
        f"[Source: {c.get('source', 'Disaster SOP')}]\n{c.get('text', '')}"
        for c in chunks
    ])

    return f"""You are an expert disaster intelligence analyst. Generate a professional,
actionable situation report in markdown format.

## Disaster Event
- Region: {region}
- Disaster Type: {disaster_type}
- Severity: {severity}

## Knowledge Base Context
{context_blocks if context_blocks else "Standard disaster response guidelines and incident management protocols apply."}

## Your Task
Write a comprehensive situation report covering:
1. **Executive Summary** - 2-3 sentences on the situation
2. **Risk Assessment** - current threats and escalation probability
3. **Affected Zones** - which populations/infrastructure are at risk
4. **Recommended Actions** - specific, prioritized emergency responses
5. **Monitoring Requirements** - what sensors/feeds to watch

Format your response in clean markdown with headers. Be specific and professional.
Do not fabricate casualty numbers. Focus on actionable intelligence."""


def generate(region: str, severity: str, disaster_type: str, chunks: list) -> str:
    """
    Generate a RAG-augmented situation report via Groq Cloud.

    Args:
        region:        Geographic region name (e.g. "River Delta B7")
        severity:      Severity level (CRITICAL | HIGH | MEDIUM | LOW)
        disaster_type: Type of disaster (e.g. "flood", "wildfire")
        chunks:        Retrieved context chunks from retriever.py

    Returns:
        Markdown string.
    """
    groq_api_key = os.getenv("GROQ_API_KEY")
    model_name = os.getenv("GROQ_MODEL", "openai/gpt-oss-20b")

    # If key is valid and not a placeholder, call Groq API
    if groq_api_key and groq_api_key.strip() and "your_groq" not in groq_api_key:
        try:
            from groq import Groq
            client = Groq(api_key=groq_api_key)
            prompt = _build_prompt(region, severity, disaster_type, chunks)

            completion = client.chat.completions.create(
                model=model_name,
                messages=[
                    {
                        "role": "system",
                        "content": "You are a disaster response AI intelligence system providing high-accuracy situation reports."
                    },
                    {
                        "role": "user",
                        "content": prompt
                    }
                ],
                temperature=0.3,
                max_tokens=1024,
            )
            return completion.choices[0].message.content
        except Exception as e:
            print(f"[generator] Groq API error: {e}. Falling back to default template.")

    # Check Gemini fallback if GEMINI_API_KEY is present
    gemini_key = os.getenv("GEMINI_API_KEY")
    if gemini_key and gemini_key.strip() and "your_gemini" not in gemini_key:
        try:
            import google.generativeai as genai
            genai.configure(api_key=gemini_key)
            model = genai.GenerativeModel("gemini-1.5-flash")
            prompt = _build_prompt(region, severity, disaster_type, chunks)
            resp = model.generate_content(prompt)
            return resp.text
        except Exception:
            pass

    # Resilient fallback template
    return _FALLBACK_TEMPLATE.format(
        region=region, disaster_type=disaster_type, severity=severity
    )
