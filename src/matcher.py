import pandas as pd
import streamlit as st
import joblib

from sentence_transformers import (
    SentenceTransformer,
    util
)

# Load model once
@st.cache_resource
def _load_model():

    return SentenceTransformer(
        "all-MiniLM-L6-v2",
        device="cpu"
    )

# Load embeddings once
@st.cache_resource
def load_embeddings():

    return joblib.load(
        "src/resume_embeddings.pkl"
    )

def match_resumes(
    job_description: str,
    df: pd.DataFrame,
    top_n: int = 10
):

    model = _load_model()

    resume_embeddings = load_embeddings()

    jd_embedding = model.encode(
        job_description,
        convert_to_tensor=True
    )

    scores = util.cos_sim(
        jd_embedding,
        resume_embeddings
    )[0]

    df = df.copy()

    df["match_score"] = [
        round(float(score) * 100, 2)
        for score in scores
    ]

    return (
        df.nlargest(top_n, "match_score")
          .reset_index(drop=True)
    )



# Whenever dataset changes, run again:
# # python src/precompute_embeddings.py