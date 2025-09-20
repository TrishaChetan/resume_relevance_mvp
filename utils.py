# utils.py
import re
from rapidfuzz import fuzz
import openai
from config import SEMANTIC_MODEL

# Configure OpenAI API key here or use environment variable
openai.api_key = "YOUR_OPENAI_API_KEY"

def clean_text(text):
    text = text.lower()
    text = re.sub(r'\s+', ' ', text)
    return text.strip()

def generate_feedback_rule_based(resume_skills, jd_must, jd_good):
    missing_must = [s for s in jd_must if s not in resume_skills]
    missing_good = [s for s in jd_good if s not in resume_skills]

    feedback = []
    if missing_must:
        feedback.append(f"Missing key skills: {', '.join(missing_must)}")
    if missing_good:
        feedback.append(f"Consider improving: {', '.join(missing_good)}")
    return " | ".join(feedback)

def generate_feedback_llm(resume_text, jd_struct):
    prompt = f"""
    JD Title: {jd_struct['title']}
    Must-have Skills: {', '.join(jd_struct['must_have'])}
    Good-to-have Skills: {', '.join(jd_struct['good_to_have'])}
    
    Resume Content: {resume_text}

    Generate concise personalized feedback for this candidate, including missing skills, projects, or certifications.
    """
    response = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages=[{"role":"user", "content": prompt}],
        temperature=0.7,
        max_tokens=200
    )
    return response['choices'][0]['message']['content'].strip()
