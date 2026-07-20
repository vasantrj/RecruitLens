# Canonical skill -> list of known aliases/variants
SKILL_TAXONOMY = {
    "Python": ["python", "python3", "py"],
    "Machine Learning": ["ml", "machine learning", "machine-learning"],
    "Deep Learning": ["dl", "deep learning"],
    "SQL": ["sql", "mysql", "postgresql", "postgres", "t-sql", "pl/sql"],
    "JavaScript": ["javascript", "js", "es6"],
    "TypeScript": ["typescript", "ts"],
    "React": ["react", "react.js", "reactjs"],
    "Node.js": ["node", "node.js", "nodejs"],
    "Data Science": ["data science", "datascience"],
    "Natural Language Processing": ["nlp", "natural language processing"],
    "Computer Vision": ["cv", "computer vision"],
    "Scikit-learn": ["scikit-learn", "sklearn", "scikit learn"],
    "TensorFlow": ["tensorflow", "tf"],
    "PyTorch": ["pytorch", "torch"],
    "Pandas": ["pandas"],
    "NumPy": ["numpy"],
    "Git": ["git"],
    "GitHub": ["github"],
    "Docker": ["docker"],
    "Kubernetes": ["kubernetes", "k8s"],
    "AWS": ["aws", "amazon web services"],
    "REST API": ["rest api", "restful api", "rest"],
    "Data Structures and Algorithms": ["dsa", "data structures and algorithms", "data structures", "algorithms"],
    "Object-Oriented Programming": ["oop", "object oriented programming", "object-oriented programming"],
    "Database Management": ["dbms", "database management"],
    "Operating Systems": ["os", "operating systems", "operating system"],
    "Computer Networks": ["cn", "computer networks", "networking"],
}

# Reverse lookup: alias -> canonical name (built once at import time)
ALIAS_TO_CANONICAL = {}
for canonical, aliases in SKILL_TAXONOMY.items():
    ALIAS_TO_CANONICAL[canonical.lower()] = canonical
    for alias in aliases:
        ALIAS_TO_CANONICAL[alias.lower()] = canonical