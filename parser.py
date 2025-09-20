import re
import fitz
import docx2txt
from rapidfuzz import fuzz

SKILLS = ["python", "java", "c++", "machine learning", "data analysis", "nlp", "sql", "deep learning"]

def clean_text(text):
    text = text.lower()
    text = re.sub(r'\s+', ' ', text)
    return text

def extract_candidate_skills_from_text(text, skills_list=SKILLS, threshold=80):
    text_low = clean_text(text)
    found = set()
    for skill in skills_list:
        skill_low = skill.lower()
        if re.search(r"\b" + re.escape(skill_low) + r"\b", text_low):
            found.add(skill_low)
        else:
            score = fuzz.partial_ratio(skill_low, text_low)
            if score >= threshold:
                found.add(skill_low)
    return sorted(list(found))

def parse_jd_structured(text):
    t = clean_text(text)
    words = t.split()
    title = " ".join(words[:8]) if words else ""
    must_have = []
    good_to_have = []
    patterns = {
        "must": r"(must have|must-haves|required|required skills|requirements)(:|\s|-)?(.*?)(?=(good to have|nice to have|preferred|$))",
        "good": r"(good to have|nice to have|preferred|optional)(:|\s|-)?(.*?)(?=(must have|required|requirements|$))"
    }
    for k, pat in patterns.items():
        m = re.search(pat, t, flags=re.IGNORECASE | re.DOTALL)
        if m:
            content = m.group(3)
            items = re.split(r"[\n•\-\*;]+|,|;", content)
            items = [i.strip() for i in items if len(i.strip())>1]
            if k == "must":
                must_have.extend(items)
            else:
                good_to_have.extend(items)
    if not must_have and not good_to_have:
        candidate_skills = extract_candidate_skills_from_text(t)
        must_have = candidate_skills[:6]
        good_to_have = candidate_skills[6:16]
    must_have = [m.lower() for m in must_have]
    good_to_have = [g.lower() for g in good_to_have]
    return {"title": title, "must_have": must_have, "good_to_have": good_to_have, "raw": t}

def extract_resume_text(path):
    if path.lower().endswith(".pdf"):
        text = ""
        doc = fitz.open(path)
        for page in doc:
            text += page.get_text()
        return text
    elif path.lower().endswith(".docx"):
        return docx2txt.process(path)
    else:
        with open(path, "r", encoding="utf-8", errors="ignore") as f:
            return f.read()
