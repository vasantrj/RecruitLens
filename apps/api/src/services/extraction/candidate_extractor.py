import json
from src.services.llm.client import call_llm_json
from src.services.llm.extraction_prompts import (
    RESUME_EXTRACTION_SYSTEM_PROMPT,
    build_resume_extraction_prompt,
)


def extract_structured_resume_data(raw_text: str) -> dict:
    user_prompt = build_resume_extraction_prompt(raw_text)
    raw_json = call_llm_json(RESUME_EXTRACTION_SYSTEM_PROMPT, user_prompt)
    try:
        return json.loads(raw_json)
    except json.JSONDecodeError:
        return {
            "error": "Failed to parse LLM output as JSON",
            "raw_output": raw_json,
        }