import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from jd_priority import classify_skills, missing_by_priority, weighted_hard_score  # noqa: E402

JD = """Data Analyst — Bengaluru
About us:
We build dashboards for retail with Excel and Power BI.

Requirements:
- 2+ years with Python and SQL
- Strong pandas skills

Nice to have:
- Docker
- AWS
Experience with Tableau is a plus.
Good communication.
"""

SKILLS = ["excel", "power bi", "python", "sql", "pandas", "docker", "aws", "tableau", "communication"]


def test_sections_and_inline_qualifiers():
    tags = classify_skills(JD, SKILLS)
    assert tags["python"] == tags["sql"] == tags["pandas"] == "must"
    assert tags["docker"] == tags["aws"] == "nice"
    assert tags["tableau"] == "nice"            # "... is a plus" inline
    assert tags["excel"] == "core"              # mentioned under "About us"
    assert tags["power bi"] == "core"


def test_one_line_lists():
    jd = "Must have: Python, SQL\nGood to have: Kafka, Airflow\nWe use Git daily."
    tags = classify_skills(jd, ["python", "sql", "kafka", "airflow", "git"])
    assert tags == {"python": "must", "sql": "must", "kafka": "nice", "airflow": "nice", "git": "core"}


def test_must_wins_when_listed_twice():
    jd = "Preferred: SQL\nRequired: SQL, Python"
    assert classify_skills(jd, ["sql", "python"])["sql"] == "must"


def test_weighted_score_penalises_missing_must_haves_more():
    tags = {"python": "must", "sql": "must", "docker": "nice", "aws": "nice"}
    skills = list(tags)
    lacks_must = weighted_hard_score(["python", "docker", "aws"], skills, tags)
    lacks_nice = weighted_hard_score(["python", "sql", "docker"], skills, tags)
    assert lacks_nice > lacks_must
    assert round(lacks_nice, 3) == round(4.5 / 5, 3)
    # without priorities it is the plain fraction, as before
    assert weighted_hard_score(["python"], skills, None) == 0.25
    assert weighted_hard_score([], [], tags) == 1.0


def test_missing_by_priority():
    tags = {"python": "must", "docker": "nice", "git": "core"}
    assert missing_by_priority(["python", "docker", "git"], tags) == (["python"], ["docker"])


def test_plain_sentences_are_not_requirements():
    jd = "Work with the data science team to generate required reports.\nStrong SQL is required.\nYou must know Git."
    tags = classify_skills(jd, ["data science", "sql", "git"])
    assert tags == {"data science": "core", "sql": "must", "git": "must"}


def test_bulleted_headings():
    jd = "• Requirements:\n• Strong SQL\n• Skills:\n• Python, Kafka\n• Spark is a plus"
    assert classify_skills(jd, ["sql", "python", "kafka", "spark"]) == {
        "sql": "must", "python": "core", "kafka": "core", "spark": "nice"}
