"""Skill vocabulary used to pull required skills out of job descriptions.

Each canonical skill maps to the aliases that may appear in text. Matching is
case-insensitive and on word boundaries, so "R" won't match inside "React".
Add your own domain skills here — no other code needs to change.
"""
import re


SKILL_ALIASES = {
    # Programming languages
    "python": ["python"],
    "java": ["java"],
    "javascript": ["javascript", "js", "ecmascript"],
    "typescript": ["typescript"],
    "c": ["c language", "c programming"],
    "c++": ["c++", "cpp"],
    "c#": ["c#", "csharp"],
    "go": ["golang", "go lang"],
    "rust": ["rust"],
    "kotlin": ["kotlin"],
    "swift": ["swift"],
    "php": ["php"],
    "ruby": ["ruby"],
    "scala": ["scala"],
    "r": ["r programming", "r language", "rstudio"],
    "matlab": ["matlab"],
    "bash": ["bash", "shell scripting", "shell script"],
    # Data & ML
    "sql": ["sql", "mysql", "postgresql", "postgres", "sqlite", "t-sql", "pl/sql"],
    "nosql": ["nosql", "mongodb", "cassandra", "dynamodb"],
    "machine learning": ["machine learning", "ml"],
    "deep learning": ["deep learning", "neural networks", "neural network"],
    "nlp": ["nlp", "natural language processing"],
    "computer vision": ["computer vision", "opencv", "image processing"],
    "generative ai": ["generative ai", "genai", "llm", "llms", "large language models", "prompt engineering"],
    "data analysis": ["data analysis", "data analytics", "exploratory data analysis", "eda"],
    "data science": ["data science"],
    "statistics": ["statistics", "statistical analysis", "hypothesis testing"],
    "data visualization": ["data visualization", "data visualisation", "matplotlib", "seaborn", "plotly"],
    "power bi": ["power bi", "powerbi"],
    "tableau": ["tableau"],
    "excel": ["excel", "ms excel", "advanced excel"],
    "pandas": ["pandas"],
    "numpy": ["numpy"],
    "scikit-learn": ["scikit-learn", "sklearn", "scikit learn"],
    "tensorflow": ["tensorflow"],
    "keras": ["keras"],
    "pytorch": ["pytorch", "torch"],
    "spark": ["spark", "apache spark", "pyspark"],
    "hadoop": ["hadoop", "hdfs", "hive"],
    "kafka": ["kafka", "apache kafka"],
    "airflow": ["airflow", "apache airflow"],
    "etl": ["etl", "elt", "data pipelines", "data pipeline"],
    "data warehousing": ["data warehouse", "data warehousing", "snowflake", "redshift", "bigquery"],
    "mlops": ["mlops", "mlflow", "kubeflow"],
    # Web & software engineering
    "html": ["html", "html5"],
    "css": ["css", "css3", "tailwind", "bootstrap"],
    "react": ["react", "reactjs", "react.js"],
    "angular": ["angular", "angularjs"],
    "vue": ["vue", "vue.js", "vuejs"],
    "node.js": ["node.js", "nodejs", "node js", "express.js", "expressjs"],
    "django": ["django"],
    "flask": ["flask"],
    "fastapi": ["fastapi"],
    "spring": ["spring", "spring boot", "springboot"],
    ".net": [".net", "dotnet", "asp.net"],
    "rest api": ["rest api", "rest apis", "restful", "api development"],
    "graphql": ["graphql"],
    "microservices": ["microservices", "microservice"],
    "git": ["git", "github", "gitlab", "version control"],
    "linux": ["linux", "unix"],
    "oop": ["oop", "object oriented", "object-oriented"],
    "data structures": ["data structures", "algorithms", "dsa"],
    "testing": ["unit testing", "pytest", "junit", "selenium", "test automation"],
    "agile": ["agile", "scrum", "kanban", "jira"],
    # Cloud & DevOps
    "aws": ["aws", "amazon web services", "ec2", "s3", "lambda"],
    "azure": ["azure", "microsoft azure"],
    "gcp": ["gcp", "google cloud"],
    "docker": ["docker", "containers", "containerization"],
    "kubernetes": ["kubernetes", "k8s"],
    "ci/cd": ["ci/cd", "cicd", "jenkins", "github actions", "continuous integration"],
    "terraform": ["terraform", "infrastructure as code"],
    # Security & networking
    "cybersecurity": ["cybersecurity", "cyber security", "information security", "infosec"],
    "networking": ["networking", "tcp/ip", "computer networks"],
    # Soft skills
    "communication": ["communication", "communication skills", "verbal and written"],
    "leadership": ["leadership", "team lead", "mentoring"],
    "problem solving": ["problem solving", "problem-solving", "analytical skills"],
    "teamwork": ["teamwork", "collaboration", "team player"],
}

# Flat list kept for backwards compatibility with older code
SKILLS = list(SKILL_ALIASES)


def _alias_pattern(alias):
    # \b doesn't work next to symbols like "+" or "#", so use look-arounds
    return re.compile(r"(?<![a-z0-9.])" + re.escape(alias.lower()) + r"(?![a-z0-9+#])")

_SKILL_PATTERNS = {skill: [_alias_pattern(a) for a in aliases] for skill, aliases in SKILL_ALIASES.items()}


def find_known_skills(text):
    """Return canonical skills from the vocabulary that appear in text, in order of first appearance."""
    text = text.lower()
    hits = []
    for skill, patterns in _SKILL_PATTERNS.items():
        positions = [m.start() for p in patterns for m in [p.search(text)] if m]
        if positions:
            hits.append((min(positions), skill))
    return [s for _, s in sorted(hits)]
