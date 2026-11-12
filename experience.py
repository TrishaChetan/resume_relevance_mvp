"""Experience requirements (from the JD) vs. experience on the resume.

Only dates under an Experience / Employment / Internship heading are counted.

JD side:    "3+ years", "minimum 2 years", "at least 5 yrs", "2-4 years of experience"
Resume side: date ranges in the work history — "Jan 2020 - Present", "06/2019 – 03/2022",
             "2018 to 2021" — merged so overlapping jobs aren't double counted.
             Falls back to an explicit claim like "4 years of experience".

Education dates are skipped when the range sits on a line mentioning a degree,
so a 2019-2023 B.Tech doesn't count as four years of work.
"""
from __future__ import annotations

import re
from datetime import date

MONTHS = {m: i for i, m in enumerate(
    ["jan", "feb", "mar", "apr", "may", "jun", "jul", "aug", "sep", "oct", "nov", "dec"], 1)}
_MON = r"(?:jan|feb|mar|apr|may|jun|jul|aug|sep|sept|oct|nov|dec)[a-z]*\.?"
_DATE = rf"(?:{_MON}\s*'?\d{{2,4}}|\d{{1,2}}[/-]\d{{4}}|\d{{4}})"
_NOW = r"(?:present|current|now|till date|to date|ongoing)"
RANGE_RE = re.compile(rf"({_DATE})\s*(?:-|–|—|to|till|until)\s*({_DATE}|{_NOW})", re.I)
EDU_RE = re.compile(r"\b(b\.?\s?tech|b\.?e\b|m\.?\s?tech|bachelor|master|b\.?sc|m\.?sc|mba|bca|mca|ph\.?d|"
                    r"degree|university|college|school|class x|class xii|cgpa|gpa|semester|diploma|polytechnic|"
                    r"percentage|ssc|hsc|10th|12th|board)\b", re.I)
# Section headings. Only date ranges under a work-type heading count as experience,
# so project and education dates on student resumes are ignored.
WORK_HEAD_RE = re.compile(r"^\W*(work\s+|professional\s+|relevant\s+)?(experience|employment(\s+history)?|"
                          r"work\s+history|internships?|career(\s+history)?)\W*$", re.I)
OTHER_HEAD_RE = re.compile(r"^\W*(academic\s+)?(projects?|education|academics?|qualifications?|skills|"
                           r"technical\s+skills|certifications?|achievements|awards|publications|"
                           r"extra[- ]?curricular|activities|hobbies|interests|languages|summary|"
                           r"profile|objective|personal\s+(details|projects)|references|declaration)\W*$", re.I)
WORD_NUM = {"one": 1, "two": 2, "three": 3, "four": 4, "five": 5, "six": 6, "seven": 7, "eight": 8,
            "nine": 9, "ten": 10}


def _num(s: str) -> float:
    s = s.lower()
    return float(WORD_NUM.get(s, s))


def required_years(jd_text: str) -> tuple[float, float | None] | None:
    """(minimum, maximum or None) years the JD asks for, or None if it doesn't say."""
    t = jd_text.lower()
    n = r"(\d+(?:\.\d+)?|one|two|three|four|five|six|seven|eight|nine|ten)"
    m = re.search(rf"{n}\s*(?:-|–|to)\s*{n}\s*\+?\s*(?:years?|yrs?)", t)
    if m:
        return _num(m.group(1)), _num(m.group(2))
    m = re.search(rf"(?:minimum|min\.?|at least|atleast)\s*(?:of\s*)?{n}\s*\+?\s*(?:years?|yrs?)", t) \
        or re.search(rf"{n}\s*\+\s*(?:years?|yrs?)", t) \
        or re.search(rf"{n}\s*(?:years?|yrs?)\s*(?:of\s*)?(?:[\w-]+\s){{0,3}}experience", t)
    if m:
        return _num(m.group(1)), None
    return None


def _parse_date(s: str, end: bool) -> date | None:
    s = s.strip().lower().replace("'", "")
    if re.fullmatch(_NOW, s):
        return date.today()
    m = re.fullmatch(r"(\d{1,2})[/-](\d{4})", s)
    if m:
        mo, y = int(m.group(1)), int(m.group(2))
        return date(y, mo, 1) if 1 <= mo <= 12 else None
    m = re.fullmatch(rf"({_MON})\s*(\d{{2,4}})", s)
    if m:
        mo = MONTHS[m.group(1)[:3]]
        y = int(m.group(2))
        y = y + 2000 if y < 100 else y
        return date(y, mo, 1)
    if re.fullmatch(r"\d{4}", s):
        return date(int(s), 12 if end else 1, 1)
    return None


def resume_years(resume_text: str) -> float | None:
    """Estimated years of work experience, or None if no work dates are found."""
    spans = []
    in_work = False
    for line in resume_text.splitlines():
        head = line.strip()
        if len(head) <= 40 and WORK_HEAD_RE.match(head):
            in_work = True
            continue
        if len(head) <= 40 and OTHER_HEAD_RE.match(head):
            in_work = False
            continue
        if not in_work or EDU_RE.search(line):
            continue
        for a, b in RANGE_RE.findall(line):
            start, stop = _parse_date(a, False), _parse_date(b, True)
            if not start or not stop or stop < start or start.year < 1970 or stop > date.today().replace(day=28):
                if stop and start and stop > date.today():
                    stop = date.today()
                else:
                    continue
            spans.append((start, stop))
    if spans:
        spans.sort()
        merged = [list(spans[0])]
        for s, e in spans[1:]:
            if s <= merged[-1][1]:
                merged[-1][1] = max(merged[-1][1], e)
            else:
                merged.append([s, e])
        months = sum((e.year - s.year) * 12 + e.month - s.month + 1 for s, e in merged)
        return round(months / 12, 1)
    m = re.search(r"(\d+(?:\.\d+)?)\s*\+?\s*(?:years?|yrs?)\s*(?:of\s*)?(?:[\w-]+\s){0,3}experience", resume_text.lower())
    return float(m.group(1)) if m else None


def experience_check(resume_text: str, jd_text: str) -> tuple[str, str | None]:
    """(summary for the results table, feedback line or None)."""
    need = required_years(jd_text)
    have = resume_years(resume_text)
    have_txt = f"~{have:g} yrs" if have is not None else "none listed"
    if not need:
        return have_txt, None
    lo, hi = need
    need_txt = f"{lo:g}-{hi:g}" if hi else f"{lo:g}+"
    summary = f"{have_txt} (needs {need_txt})"
    if have is None:
        return summary, f"JD asks for {need_txt} years; add clear dates (e.g. 'Jan 2021 - Present') to your work history."
    if have < lo:
        return summary, f"JD asks for {need_txt} years of experience; the resume shows about {have:g}."
    return summary, None
