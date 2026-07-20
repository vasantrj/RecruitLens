from groq import Groq
from src.config import settings

client = Groq(api_key=settings.groq_api_key)

MODEL_NAME = "llama-3.3-70b-versatile"


def call_llm_json(system_prompt: str, user_prompt: str) -> str:
    """
    Calls Groq's chat completion API and forces JSON-formatted output.
    Returns the raw JSON string from the model.
    """
    response = client.chat.completions.create(
        model=MODEL_NAME,
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt},
        ],
        temperature=0.1,
        response_format={"type": "json_object"},
    )
    return response.choices[0].message.content