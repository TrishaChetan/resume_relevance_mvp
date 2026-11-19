import io
import os
import sys
import zipfile

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from interview_kit import build_kit, kit_markdown, kits_zip, probe_questions  # noqa: E402

PRI = {"python": "must", "sql": "must", "docker": "nice", "excel": "core", "airflow": "core"}


def test_probes_prioritise_must_haves_and_gaps_cover_missing_musts():
    kit = build_kit("Priya Sharma", matched=["excel", "docker", "python"], missing=["sql", "airflow"], priorities=PRI)
    assert [s for s, _ in kit["probes"]] == ["python", "excel", "docker"]
    assert [s for s, _ in kit["gaps"]] == ["sql"]                 # only the missing must-have
    assert "closest thing" in kit["gaps"][0][1][0]


def test_without_priorities_and_unknown_skills():
    kit = build_kit("A", matched=["rust-tauri"], missing=["airflow", "kafka", "spark"])
    assert "rust-tauri" in kit["probes"][0][1][0]                 # generic question names the skill
    assert len(kit["gaps"]) == 2
    assert probe_questions("SQL")[0].startswith("Write a query")


def test_experience_questions_only_when_short():
    assert build_kit("A", [], [], experience="~1.5 yrs (needs 3+)")["experience"]
    assert build_kit("A", [], [], experience="not found (needs 2-4)")["experience"]
    assert not build_kit("A", [], [], experience="~5 yrs (needs 3+)")["experience"]
    assert not build_kit("A", [], [], experience="~5 yrs")["experience"]


def test_markdown_and_zip():
    md = kit_markdown(build_kit("Priya", ["python"], ["sql"], PRI, "~1 yrs (needs 2+)"), "Data Analyst")
    assert md.startswith("# Interview kit — Priya (Data Analyst)")
    for section in ("## Check the skills they claim", "## Explore the gaps", "## Experience", "## Notes"):
        assert section in md
    rows = [{"Name": "Priya Sharma", "Matched": "python, excel", "Missing": "sql", "Experience": ""},
            {"Name": "Priya Sharma", "Matched": "python", "Missing": "", "Experience": ""},
            {"Name": "", "Resume": "cv 3.pdf", "Matched": "", "Missing": "sql", "Experience": ""}]
    names = zipfile.ZipFile(io.BytesIO(kits_zip(rows, PRI))).namelist()
    assert names == ["interview-kit-Priya_Sharma.md", "interview-kit-Priya_Sharma-2.md", "interview-kit-cv_3.pdf.md"]
