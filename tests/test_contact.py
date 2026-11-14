import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from contact import extract_contact  # noqa: E402


def test_full_header():
    text = """PRIYA SHARMA
    priya.sharma@example.com | +91 98765 43210 | linkedin.com/in/priya-sharma | github.com/priyas
    Portfolio: https://priya.dev
    SKILLS"""
    c = extract_contact(text)
    assert c["name"] == "Priya Sharma"
    assert c["email"] == "priya.sharma@example.com"
    assert c["phone"] == "+91 98765 43210"
    assert c["linkedin"] == "https://linkedin.com/in/priya-sharma"
    assert c["github"] == "https://github.com/priyas"
    assert c["portfolio"] == "https://priya.dev"


def test_run_on_links_and_lone_name():
    text = "Summary line first\nRachana\nrachana202@gmail.com | linkedin.com/in/rachana-https://github.com/rach9"
    c = extract_contact(text)
    assert c["name"] == "Rachana"
    assert c["linkedin"] == "https://linkedin.com/in/rachana"
    assert c["github"] == "https://github.com/rach9"


def test_project_urls_and_years_are_not_contact_details():
    text = """Jay Raj
    Built a scraper for https://fe2024.mahacet.org/ cutoff data
    B.Tech 2019 - 2023
    Hosted demo at https://jay.github.io/demo"""
    c = extract_contact(text)
    assert c["phone"] == ""
    assert c["portfolio"] == "https://jay.github.io/demo"


def test_name_falls_back_to_email():
    c = extract_contact("RESUME\nrahul.verma99@mail.com\nObjective: ...")
    assert c["name"] == "Rahul Verma"
    assert extract_contact("nothing useful here")["email"] == ""
