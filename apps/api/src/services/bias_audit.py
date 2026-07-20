import re


GENDERED_PRONOUNS = {
    r"\bhe\b": "they",
    r"\bhim\b": "them",
    r"\bhis\b": "their",
    r"\bshe\b": "they",
    r"\bher\b": "them",
    r"\bhers\b": "theirs",
    r"\bhimself\b": "themself",
    r"\bherself\b": "themself",
}

GENDER_SIGNAL_WORDS = [
    r"\bmr\.?\b", r"\bmrs\.?\b", r"\bms\.?\b", r"\bmiss\b",
    r"\bwoman\b", r"\bwomen\b", r"\bman\b", r"\bmen\b",
    r"\bfemale\b", r"\bmale\b",
]


def redact_identity_signals(text: str, full_name: str = None) -> str:
    """
    Removes/neutralizes name, gendered pronouns, and gender-signal words from resume text.
    Used to test whether the match score changes when identity signals are stripped —
    a large score delta would indicate the model may be sensitive to identity rather
    than qualifications.
    """
    if not text:
        return text

    redacted = text

    if full_name:
        for part in full_name.split():
            if len(part) > 1:
                redacted = re.sub(re.escape(part), "[REDACTED]", redacted, flags=re.IGNORECASE)

    for pattern, replacement in GENDERED_PRONOUNS.items():
        redacted = re.sub(pattern, replacement, redacted, flags=re.IGNORECASE)

    for pattern in GENDER_SIGNAL_WORDS:
        redacted = re.sub(pattern, "[REDACTED]", redacted, flags=re.IGNORECASE)

    email_pattern = r"[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}"
    redacted = re.sub(email_pattern, "[REDACTED_EMAIL]", redacted)

    phone_pattern = r"(\+?\d{1,3}[\s-]?)?\(?\d{3,5}\)?[\s-]?\d{3,4}[\s-]?\d{3,4}"
    redacted = re.sub(phone_pattern, "[REDACTED_PHONE]", redacted)

    return redacted


def redact_candidate_data(candidate_data: dict) -> dict:
    """
    Returns a copy of parsed candidate data with name/email/phone stripped,
    and gendered pronouns neutralized in the summary field.
    """
    redacted = dict(candidate_data)
    redacted["full_name"] = "[REDACTED]"
    redacted["email"] = None
    redacted["phone"] = None
    if redacted.get("summary"):
        redacted["summary"] = redact_identity_signals(redacted["summary"])
    return redacted