import os
from pathlib import Path
from dotenv import load_dotenv
from groq import Groq

# Load .env from project root
env_path = Path(__file__).resolve().parent.parent / ".env"
load_dotenv(dotenv_path=env_path)

# Load API key
GROQ_API_KEY = os.getenv("GROQ_API_KEY")

# Initialize client
client = Groq(api_key=GROQ_API_KEY)

def build_prompt(resume_text, jd_text, score):
    return f"""
You are an expert recruiter.

Candidate Match Score: {score}%

JOB DESCRIPTION:
{jd_text[:1200]}

RESUME:
{resume_text[:1200]}

Provide:
1. Why this score
2. Key strengths
3. Key weaknesses
4. Hiring recommendation

Keep response concise and professional.
"""

def get_feedback(resume_text: str, jd_text: str, score: float) -> str:

    try:
        prompt = build_prompt(resume_text, jd_text, score)

        response = client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=[
                {
                    "role": "user",
                    "content": prompt
                }
            ],
            temperature=0.3,
            max_tokens=300
        )

        return response.choices[0].message.content

    except Exception as e:
        return f"Groq error: {str(e)}"