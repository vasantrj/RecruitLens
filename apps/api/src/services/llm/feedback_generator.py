import json
from src.services.llm.client import call_llm_json
from src.services.llm.extraction_prompts import (
    RECRUITER_FEEDBACK_SYSTEM_PROMPT,
    build_recruiter_feedback_prompt,
)


def generate_recruiter_feedback(candidate_data: dict, job_data: dict, match_result: dict) -> dict:
    user_prompt = build_recruiter_feedback_prompt(candidate_data, job_data, match_result)
    raw_json = call_llm_json(RECRUITER_FEEDBACK_SYSTEM_PROMPT, user_prompt)
    try:
        return json.loads(raw_json)
    except json.JSONDecodeError:
        return {
            "error": "Failed to parse LLM output as JSON",
            "raw_output": raw_json,
        }