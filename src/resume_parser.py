import re
import spacy
import streamlit as st

# Load spaCy only once
@st.cache_resource(show_spinner=False)
def load_spacy():
    return spacy.load("en_core_web_sm")

nlp = load_spacy()

def parse_resume(text: str) -> dict:

    # Clean text
    text = text.replace("\n", " ")

    doc = nlp(text)

    # ---------------- NAME ----------------
    name = next(
        (
            ent.text
            for ent in doc.ents
            if ent.label_ == "PERSON"
        ),
        "Not found"
    )

    # ---------------- EMAIL ----------------
    email_pattern = r'[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}'

    emails = re.findall(
        email_pattern,
        text
    )

    email = emails[0] if emails else "Not found"

    # ---------------- PHONE ----------------
    phone_pattern = r'(?:\+91[\-\s]?)?[6-9]\d{9}'

    phones = re.findall(
        phone_pattern,
        text
    )

    phone = phones[0] if phones else "Not found"

    # ---------------- EDUCATION ----------------
    edu_keywords = [
        "b.tech", "b.e", "m.tech",
        "mba", "bsc", "msc",
        "bachelor", "master",
        "phd", "diploma"
    ]

    education = [
        line.strip()
        for line in text.split(".")
        if any(
            k in line.lower()
            for k in edu_keywords
        )
    ]

    # ---------------- EXPERIENCE ----------------
    experience_patterns = [
        r'(\d+)\+?\s+years?',
        r'(\d+)\s+yrs?',
        r'experience\s*:\s*(\d+)'
    ]

    experience = "Not found"

    for pattern in experience_patterns:

        match = re.search(
            pattern,
            text,
            re.I
        )

        if match:
            experience = f"{match.group(1)} years"
            break

    return {
        "name": name,
        "email": email,
        "phone": phone,
        "education": education[:2],
        "experience": experience
    }