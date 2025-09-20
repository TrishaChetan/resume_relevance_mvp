import os
import re
import pdfplumber
import docx2txt
import pandas as pd
from scorer import compute_final_score

# --------------------------
# Parse resume
# --------------------------
def parse_resume(file_path):
    text = ""
    if file_path.lower().endswith(".pdf"):
        with pdfplumber.open(file_path) as pdf:
            for page in pdf.pages:
                text += page.extract_text() + " "
    elif file_path.lower().endswith(".docx"):
        text = docx2txt.process(file_path)
    return text

# --------------------------
# Parse JD (PDF/DOCX)
# --------------------------
def parse_jd(file_path):
    return parse_resume(file_path)

# --------------------------
# Extract skills from JD (robust)
# --------------------------
def extract_skills_from_jd(jd_text):
    jd_text = jd_text.lower()
    
    # Try regex first
    pattern = r"(skills|must have|good to have)\s*[:\-]\s*(.+)"
    matches = [s for _, s in re.findall(pattern, jd_text)]
    
    skills = []
    for skill_str in matches:
        for skill in re.split(r',|;', skill_str):
            skill_clean = skill.strip()
            if skill_clean:
                skills.append(skill_clean)
    
    # Fallback: if no skills found, extract frequent nouns/keywords
    if not skills:
        words = re.findall(r'\b[a-z]{2,}\b', jd_text)
        freq = pd.Series(words).value_counts()
        # top 10 frequent words as "skills"
        skills = freq.head(10).index.tolist()
    
    return skills

# --------------------------
# Batch process resumes
# --------------------------
def batch_process(jd_file, resumes_folder):
    jd_text = parse_jd(jd_file)
    jd_skills = extract_skills_from_jd(jd_text)

    results = []

    for resume_file in os.listdir(resumes_folder):
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
    df.to_csv("resume_evaluation_results.csv", index=False)
    return df
