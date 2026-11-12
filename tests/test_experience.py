import os
import sys
from datetime import date

import pytest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from experience import experience_check, required_years, resume_years  # noqa: E402


@pytest.mark.parametrize("jd, expected", [
    ("We need 3+ years of Python experience", (3, None)),
    ("Minimum 2 years in data analytics", (2, None)),
    ("at least five years experience", (5, None)),
    ("2-4 years of experience in ML", (2, 4)),
    ("3 years of hands-on backend experience", (3, None)),
    ("Freshers welcome, strong Python skills", None),
])
def test_required_years(jd, expected):
    assert required_years(jd) == expected


def test_resume_years_merges_overlaps_and_skips_education():
    text = """
    EXPERIENCE
    Software Engineer, Acme   Jan 2019 - Dec 2020
    Freelance developer       06/2020 - 12/2021
    B.Tech Computer Science, XYZ University   2015 - 2019
    PROJECTS
    Deepfake detector   June 2018 - May 2019
    """
    assert resume_years(text) == 3.0          # Jan 2019 .. Dec 2021, overlap counted once, degree ignored


def test_present_and_claimed_years():
    y = date.today().year - 2
    assert resume_years(f"Work Experience\nData Analyst  Mar {y} - Present") >= 1.5
    assert resume_years(f"Projects\nSales dashboard  Mar {y} - Present") is None   # projects aren't jobs
    assert resume_years("Results-driven engineer with 4 years of professional experience") == 4.0
    assert resume_years("Python, SQL, Tableau") is None


def test_experience_check_feedback():
    summary, fb = experience_check("Internships\nIntern  Jun 2023 - Aug 2023", "Requires 3+ years of experience")
    assert summary.startswith("~0.2 yrs (needs 3+)")
    assert experience_check("Skills: SQL", "3+ years")[0] == "none listed (needs 3+)"
    assert "3+ years" in fb
    summary, fb = experience_check("Employment\nEngineer 2015 - 2022", "2-4 years of experience")
    assert fb is None and "needs 2-4" in summary
    assert experience_check("x", "no requirement")[1] is None
