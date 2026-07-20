import httpx
from bs4 import BeautifulSoup

from src.services.llm.client import call_llm_json


def fetch_page_text(url: str, timeout: float = 8.0) -> str:
    try:
        response = httpx.get(url, timeout=timeout, follow_redirects=True, headers={
            "User-Agent": "Mozilla/5.0 (compatible; RecruitLensBot/1.0)"
        })
        response.raise_for_status()
        soup = BeautifulSoup(response.text, "html.parser")
        for tag in soup(["script", "style", "nav", "footer"]):
            tag.decompose()
        text = soup.get_text(separator=" ", strip=True)
        return text[:6000]  # cap length to keep LLM prompt small
    except Exception:
        return ""


SITE_SUMMARY_SYSTEM_PROMPT = """You are summarizing a candidate's personal website or portfolio page for a recruiter. Return ONLY valid JSON with:
- summary (string — 2-3 sentences on what this page shows: projects, skills, focus areas)
- notable_signals (array of strings — 1-3 short notable things, e.g. "Has 3 deployed projects", "Focuses on NLP")

If the page content is empty, unclear, or not resume-relevant, return summary as null and notable_signals as an empty array."""


def summarize_personal_site(url: str) -> dict:
    page_text = fetch_page_text(url)
    if not page_text:
        return {"summary": None, "notable_signals": []}

    raw_json = call_llm_json(
        SITE_SUMMARY_SYSTEM_PROMPT,
        f"Page content from {url}:\n\n{page_text}\n\nSummarize as JSON.",
    )
    import json
    try:
        return json.loads(raw_json)
    except json.JSONDecodeError:
        return {"summary": None, "notable_signals": []}