"""Must-have vs nice-to-have skills in a job description.

JDs usually say which skills are non-negotiable and which are a bonus:

    Must have: Python, SQL, Pandas
    Nice to have: Docker, AWS
    Experience with Tableau is a plus.

classify_skills() tags every JD skill as "must", "nice" or "core" (mentioned
without a qualifier). weighted_hard_score() then weights them 2 : 1 : 0.5, so
missing a must-have costs four times as much as missing a nice-to-have.
"""
from __future__ import annotations

import re

from skills_db import find_known_skills

MUST_HEAD = re.compile(
    r"\b(must[\s-]?haves?|required|requirements|mandatory|essential|minimum qualifications?|"
    r"basic qualifications?|you must|what you need)\b", re.I)
NICE_HEAD = re.compile(
    r"\b(nice[\s-]?to[\s-]?haves?|good[\s-]?to[\s-]?haves?|preferred|bonus|desirable|desired|"
    r"preferred qualifications?|is a plus|are a plus|would be a plus|added advantage|optional)\b", re.I)
# In ordinary sentences only explicit wording counts ("generate required reports" doesn't)
MUST_INLINE = re.compile(
    r"\b(must[\s-]?have|you must|must be (?:proficient|familiar|skilled|comfortable)|"
    r"(?:is|are) (?:required|mandatory|essential|a must)|mandatory)\b", re.I)
# A short line ending in ":" (or a heading-ish line) starts a new section
BULLET = re.compile(r"^\s*(?:[-*•·▪◦]|\d+[.)])\s+")
HEADING = re.compile(r"^\s*[A-Za-z][A-Za-z /&()'-]{2,60}:?\s*$")

WEIGHTS = {"must": 2.0, "core": 1.0, "nice": 0.5}


def _skills_in(text: str, jd_skills: list[str]) -> set[str]:
    low = text.lower()
    found = set(find_known_skills(low))
    for s in jd_skills:  # skills outside the vocabulary (niche tools from "Skills:" lists)
        if re.search(rf"(?<![a-z0-9]){re.escape(s.lower())}(?![a-z0-9])", low):
            found.add(s)
    return {s for s in found if s in jd_skills}


def classify_skills(jd_text: str, jd_skills: list[str]) -> dict[str, str]:
    """{skill: "must" | "nice" | "core"} for every skill in jd_skills."""
    tags: dict[str, str] = {}
    section = None  # "must" | "nice" | None
    inline = False  # section came from "Must have: a, b" rather than a heading
    for raw in jd_text.splitlines():
        line = raw.strip()
        if not line:
            continue
        if inline and not BULLET.match(line):
            section, inline = None, False  # an inline list only carries on through bullets
        line = BULLET.sub("", line, count=1)  # "• Requirements:" is still a heading
        is_must, is_nice = bool(MUST_HEAD.search(line)), bool(NICE_HEAD.search(line))
        # heading lines ("Requirements:", "Preferred Qualifications") switch the section;
        # "Must have: Python, SQL" does both at once
        head = line.split(":", 1)[0] if ":" in line else line
        if (is_must or is_nice) and (HEADING.match(line) or ":" in line):
            section = "nice" if NICE_HEAD.search(head) else ("must" if MUST_HEAD.search(head) else section)
            inline = ":" in line and bool(line.split(":", 1)[1].strip())
        elif HEADING.match(line) and line.endswith(":"):
            section, inline = None, False  # some other heading, e.g. "About us:"
        # sentence-level qualifiers win over the section: "Tableau is a plus."
        if NICE_HEAD.search(line) and not MUST_HEAD.search(head):
            level = "nice"
        elif MUST_INLINE.search(line) and not HEADING.match(line) and ":" not in line:
            level = "must"
        else:
            level = section
        if not level:
            continue
        for s in _skills_in(line, jd_skills):
            # the strongest requirement wins if a skill is listed twice
            if tags.get(s) != "must":
                tags[s] = level
    return {s: tags.get(s, "core") for s in jd_skills}


def weighted_hard_score(matched: list[str], jd_skills: list[str], priorities: dict[str, str] | None) -> float:
    if not jd_skills:
        return 1.0
    if not priorities:
        return len([s for s in jd_skills if s in matched]) / len(jd_skills)
    total = sum(WEIGHTS[priorities.get(s, "core")] for s in jd_skills)
    got = sum(WEIGHTS[priorities.get(s, "core")] for s in jd_skills if s in matched)
    return got / total


def missing_by_priority(missing: list[str], priorities: dict[str, str] | None) -> tuple[list[str], list[str]]:
    """(missing must-haves, missing nice-to-haves)."""
    priorities = priorities or {}
    return ([s for s in missing if priorities.get(s) == "must"],
            [s for s in missing if priorities.get(s) == "nice"])
