import pandas as pd
import joblib

from sentence_transformers import SentenceTransformer

from preprocess import preprocess_dataframe

print("Loading dataset...")

df = pd.read_csv(
    "data/Resume.csv",
    low_memory=False
)

df = preprocess_dataframe(df)

print("Loading transformer model...")

model = SentenceTransformer(
    "all-MiniLM-L6-v2"
)

print("Generating embeddings...")

embeddings = model.encode(
    df["clean_resume"].tolist(),
    batch_size=64,
    show_progress_bar=True,
    convert_to_tensor=True
)

print("Saving embeddings...")

joblib.dump(
    embeddings,
    "src/resume_embeddings.pkl"
)

print("Done!")