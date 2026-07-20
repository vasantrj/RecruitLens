import json
from src.services.llm.client import call_llm_json
from src.services.llm.extraction_prompts import (
    ROLE_PROFILE_SYSTEM_PROMPT,
    build_role_profile_prompt,
)


def generate_role_profile(role_title: str) -> dict:
    user_prompt = build_role_profile_prompt(role_title)
    raw_json = call_llm_json(ROLE_PROFILE_SYSTEM_PROMPT, user_prompt)
    try:
        return json.loads(raw_json)
    except json.JSONDecodeError:
        return {
            "error": "Failed to parse LLM output as JSON",
            "raw_output": raw_json,
        }