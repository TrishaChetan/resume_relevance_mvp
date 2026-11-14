"""Pull contact details out of resume text so a shortlist is actionable.

Extracts the candidate's name (best effort, from the first lines), email,
phone (Indian and international formats), LinkedIn, GitHub and portfolio
links. Missing fields come back as "".
"""
from __future__ import annotations

import re

EMAIL_RE = re.compile(r"[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}")
# +91 98765 43210, 098765-43210, (555) 123-4567, +1 555.123.4567 ...
PHONE_RE = re.compile(r"(?<![\w/])(\+?\d{1,3}[\s.-]?)?(\(?\d{2,5}\)?[\s.-]?)?\d{3,5}[\s.-]?\d{4,5}(?![\w/])")
LINKEDIN_RE = re.compile(r"(?:https?://)?(?:[a-z]{2,3}\.)?linkedin\.com/(?:in|pub)/[A-Za-z0-9_%-]+/?", re.I)
GITHUB_RE = re.compile(r"(?:https?://)?(?:www\.)?github\.com/[A-Za-z0-9-]{1,39}(?![A-Za-z0-9-])/?", re.I)
URL_RE = re.compile(r"(?:https?://|www\.)[^\s|,;()<>]+", re.I)
# Only treat a link as the candidate's own site if it's labelled as one or hosted
# somewhere people keep portfolios — not any URL mentioned in a project bullet.
PORTFOLIO_HOSTS = re.compile(r"github\.io|vercel\.app|netlify\.app|pages\.dev|behance\.net|dribbble\.com|"
                             r"medium\.com/@|about\.me|wixsite\.com|wordpress\.com|notion\.site|carrd\.co|"
                             r"kaggle\.com/[A-Za-z0-9_-]+$", re.I)
PORTFOLIO_LABEL = re.compile(r"\b(portfolio|website|personal site|blog|homepage)\b", re.I)
SECTION_WORDS = re.compile(r"\b(resume|curriculum|vitae|cv|profile|summary|objective|contact|email|phone|"
                           r"address|skills|education|experience|projects?)\b", re.I)


def _clean_url(u: str) -> str:
    u = u.rstrip("/.").strip()
    return u if u.lower().startswith("http") else "https://" + u


def _phone(text: str) -> str:
    for m in PHONE_RE.finditer(text):
        raw = m.group(0).strip()
        digits = re.sub(r"\D", "", raw)
        if not 10 <= len(digits) <= 13:
            continue
        if re.fullmatch(r"(19|20)\d{2}\D*(19|20)\d{2}", raw.replace(" ", "")):  # "2019 - 2023"
            continue
        return raw
    return ""


def _name(text: str, email: str) -> str:
    email_local = re.sub(r"\d+", "", email.split("@")[0]).lower() if email else ""
    for line in text.splitlines()[:8]:
        line = line.strip(" |•-:\t")
        # a lone word only counts if it matches the email (rachana202@... -> "Rachana")
        if re.fullmatch(r"[A-Za-z]{3,}", line) and email_local.startswith(line.lower()):
            return line.capitalize()
        if not line or "@" in line or any(ch.isdigit() for ch in line) or SECTION_WORDS.search(line):
            continue
        words = line.split()
        if 2 <= len(words) <= 4 and all(re.fullmatch(r"[A-Za-z][A-Za-z.'-]*", w) for w in words):
            return " ".join(w.capitalize() if w.isupper() or w.islower() else w for w in words)
    if email:  # fall back to the email's local part: priya.sharma99 -> Priya Sharma
        local = re.sub(r"\d+", "", email.split("@")[0])
        parts = [p for p in re.split(r"[._-]+", local) if len(p) > 1]
        if 2 <= len(parts) <= 3:
            return " ".join(p.capitalize() for p in parts)
    return ""


def extract_contact(text: str) -> dict:
    m = EMAIL_RE.search(text)
    email = m.group(0) if m else ""
    linkedin = LINKEDIN_RE.search(text)
    linkedin_url = ""
    if linkedin:
        # PDF text can run the next link straight on: "linkedin.com/in/chandra-https://github.com/..."
        linkedin_url = re.sub(r"(?i)(https?|www)/?$", "", linkedin.group(0).rstrip("/")).rstrip("-_")
        if re.search(r"/(in|pub)/?$", linkedin_url, re.I):  # handle missing entirely
            linkedin_url = ""
    github = GITHUB_RE.search(text)
    portfolio = ""
    for line in text.splitlines():
        for m in URL_RE.finditer(line):
            u = m.group(0).rstrip("/.")
            if re.search(r"linkedin\.com|github\.com/|mailto:", u, re.I):
                continue
            if PORTFOLIO_HOSTS.search(u) or PORTFOLIO_LABEL.search(line):
                portfolio = _clean_url(u)
                break
        if portfolio:
            break
    return {
        "name": _name(text, email),
        "email": email,
        "phone": _phone(text),
        "linkedin": _clean_url(linkedin_url) if linkedin_url else "",
        "github": _clean_url(github.group(0)) if github else "",
        "portfolio": portfolio,
    }
