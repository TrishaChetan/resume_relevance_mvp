import os
import re
import pdfplumber
import docx2txt
import pandas as pd
from scorer import compute_final_score
from skills_db import SKILL_ALIASES

# --------------------------
# Parse resume
# --------------------------
def parse_resume(file_path):
    text = ""
    if file_path.lower().endswith(".pdf"):
        with pdfplumber.open(file_path) as pdf:
            for page in pdf.pages:
                # extract_text() returns None for scanned/image-only pages
                text += (page.extract_text() or "") + " "
    elif file_path.lower().endswith(".docx"):
        text = docx2txt.process(file_path) or ""
    return text

# --------------------------
# Parse JD (PDF/DOCX)
# --------------------------
def parse_jd(file_path):
    return parse_resume(file_path)

# --------------------------
# Extract skills from JD
# --------------------------
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


def extract_skills_from_jd(jd_text):
    """Skills the JD asks for.

    1. Every skill from the vocabulary in skills_db.py that the JD mentions.
    2. Plus short items from explicit "Skills:" / "Must have:" lists that the
       vocabulary doesn't know yet (e.g. a niche tool), cleaned of bullets
       and filler words.
    Never falls back to raw word frequency, which used to return "and", "the"...
    """
    jd_lower = jd_text.lower()
    skills = find_known_skills(jd_lower)

    pattern = r"(skills|must have|must-have|good to have|nice to have|requirements)\s*[:\-]\s*(.+)"
    for _, line in re.findall(pattern, jd_lower):
        for item in re.split(r",|;|\||•|/| and ", line):
            item = re.sub(r"^[\s\-*•·]+|[\s.]+$", "", item)
            item = re.sub(r"^(and|or|with|experience in|knowledge of|proficiency in)\s+", "", item)
            if not item or len(item.split()) > 3:
                continue  # long phrases are sentences, not skill names
            known = find_known_skills(item)
            if known:
                skills.extend(k for k in known if k not in skills)
            elif item not in skills and len(item) > 1:
                skills.append(item)
    return skills

# --------------------------
# Batch process resumes
# --------------------------
def batch_process(jd_file, resumes_folder):
    jd_text = parse_jd(jd_file)
    jd_skills = extract_skills_from_jd(jd_text)

    results = []

    for resume_file in sorted(os.listdir(resumes_folder)):
        if not resume_file.lower().endswith((".pdf", ".docx")):
            continue
        resume_path = os.path.join(resumes_folder, resume_file)
        resume_text = parse_resume(resume_path)
        score, verdict, missing, feedback = compute_final_score(resume_text, jd_text, jd_skills)
        results.append({
            "JD": os.path.basename(jd_file),
            "Resume": resume_file,
            "Score": score,
            "Missing": missing,
            "Verdict": verdict,
            "Feedback": feedback
        })

    df = pd.DataFrame(results)
    if not df.empty:
        # best candidates first, with a rank column for shortlisting
        df = df.sort_values("Score", ascending=False).reset_index(drop=True)
        df.insert(0, "Rank", range(1, len(df) + 1))
    df.to_csv("resume_evaluation_results.csv", index=False)
    return df
