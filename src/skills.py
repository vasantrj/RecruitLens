import re

SKILLS_DB = {

    # Programming Languages
    "python",
    "java",
    "c",
    "c++",
    "javascript",
    "typescript",

    # Web Development
    "html",
    "css",
    "react",
    "nodejs",
    "express",
    "django",
    "flask",
    "fastapi",

    # Databases
    "sql",
    "mysql",
    "mongodb",
    "postgresql",

    # Data Science & Analytics
    "pandas",
    "numpy",
    "matplotlib",
    "seaborn",
    "power bi",
    "tableau",
    "excel",
    "data analysis",
    "data science",
    "data visualization",

    # AI / ML
    "machine learning",
    "deep learning",
    "artificial intelligence",
    "nlp",
    "tensorflow",
    "pytorch",
    "scikit-learn",

    # Cloud / DevOps
    "aws",
    "azure",
    "docker",
    "kubernetes",

    # Tools
    "git",
    "github",
    "streamlit",
    "linux",

    # Soft Skills
    "teamwork",
    "communication",
    "leadership",
    "problem-solving",
    "quick learner",
    "collaboration",
    "time management"
}

def extract_skills(text):

    if not text:
        return []

    text = text.lower()

    found_skills = []

    for skill in SKILLS_DB:

        # Correct regex word boundary
        pattern = r'\b' + re.escape(skill) + r'\b'

        if re.search(pattern, text):
            found_skills.append(skill)

    return sorted(list(set(found_skills)))