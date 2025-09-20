import re
from rapidfuzz import fuzz
from sentence_transformers import SentenceTransformer, util

# Load local sentence-transformers model
model = SentenceTransformer('all-MiniLM-L6-v2')

# --------------------------
# Preprocess text
# --------------------------
def preprocess_text(text):
    text = text.lower()
    text = re.sub(r'[^a-z0-9\s]', ' ', text)  # remove punctuation
    text = re.sub(r'\s+', ' ', text)  # collapse spaces
    return text

# --------------------------
# Extract skills using fuzzy matching
# --------------------------
def extract_skills_from_text(text, skill_list, threshold=80):
    found_skills = []
    text_proc = preprocess_text(text)
    words = text_proc.split()
    for skill in skill_list:
        skill_proc = preprocess_text(skill)
        max_ratio = 0
        n_words = len(skill_proc.split())
        for i in range(len(words) - n_words + 1):
            phrase = ' '.join(words[i:i+n_words])
            ratio = fuzz.ratio(skill_proc, phrase)
            if ratio > max_ratio:
                max_ratio = ratio
        if max_ratio >= threshold:
            found_skills.append(skill)
    return found_skills

# --------------------------
# Hard match score
# --------------------------
def hard_match_score(resume_text, jd_skills):
    matched_skills = extract_skills_from_text(resume_text, jd_skills)
    if len(jd_skills) == 0:
        return 1.0, matched_skills
    return len(matched_skills) / len(jd_skills), matched_skills

# --------------------------
# Semantic score
# --------------------------
def semantic_score(resume_text, jd_text):
    emb_resume = model.encode(resume_text, convert_to_tensor=True)
    emb_jd = model.encode(jd_text, convert_to_tensor=True)
    cosine_sim = util.pytorch_cos_sim(emb_resume, emb_jd).item()
    return cosine_sim  # 0-1

# --------------------------
# Feedback generation
# --------------------------
def generate_feedback(resume_text, missing_skills, jd_text):
    feedback_list = []
    
    if missing_skills:
        feedback_list.append(
            f"You are missing key skills: {', '.join(missing_skills)}. "
            "Consider taking projects or courses to strengthen these areas."
        )
    
    emb_resume = model.encode(resume_text, convert_to_tensor=True)
    emb_jd = model.encode(jd_text, convert_to_tensor=True)
    sim = util.pytorch_cos_sim(emb_resume, emb_jd).item()
    
    if sim < 0.4:
        feedback_list.append(
            "Your resume content does not fully align with the job description. "
            "Consider emphasizing relevant projects, internships, or experiences."
        )
    elif sim < 0.7:
        feedback_list.append(
            "Your resume partially matches the job description. "
            "You can highlight relevant projects or technical experience more clearly."
        )
    else:
        feedback_list.append("Your resume is well-aligned with the JD. Great job!")
    
    return feedback_list

# --------------------------
# Compute final score
# --------------------------
def compute_final_score(resume_text, jd_text, jd_skills, weights=(0.5, 0.5)):
    hard, matched_skills = hard_match_score(resume_text, jd_skills)
    semantic = semantic_score(resume_text, jd_text)
    score = weights[0]*hard + weights[1]*semantic
    final_score = round(score*100, 2)
    
    # Missing = all skills not matched
    if jd_skills:
        missing_skills = [s for s in jd_skills if s not in matched_skills]
    else:
        missing_skills = ["Cannot detect skills from JD, please review manually"]
    
    # Verdict
    if final_score >= 75:
        verdict = "High"
    elif final_score >= 50:
        verdict = "Medium"
    else:
        verdict = "Low"
    
    # Feedback
    feedback = generate_feedback(resume_text, missing_skills, jd_text)
    
    return final_score, verdict, missing_skills, feedback
