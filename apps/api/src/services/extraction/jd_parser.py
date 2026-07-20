import json
from src.services.llm.client import call_llm_json
from src.services.llm.extraction_prompts import (
    JD_EXTRACTION_SYSTEM_PROMPT,
    build_jd_extraction_prompt,
)


def extract_structured_jd_data(jd_text: str) -> dict:
    user_prompt = build_jd_extraction_prompt(jd_text)
    raw_json = call_llm_json(JD_EXTRACTION_SYSTEM_PROMPT, user_prompt)
    try:
        return json.loads(raw_json)
    except json.JSONDecodeError:
        return {
            "error": "Failed to parse LLM output as JSON",
            "raw_output": raw_json,
        }