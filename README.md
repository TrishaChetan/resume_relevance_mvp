Automated Resume Relevance Check System (MVP)
Project Overview

The Automated Resume Relevance Check System is a Python-based tool designed to streamline and automate the process of evaluating resumes against job descriptions (JDs). This system was created to assist placement teams, recruiters, and students by providing a fast, consistent, and accurate evaluation of resumes while highlighting gaps and offering actionable feedback.

Manual resume evaluation is time-consuming and inconsistent. Recruiters must go through thousands of applications for each job posting, which often leads to delayed shortlisting and subjective judgments. This project addresses these challenges by automating resume parsing, skill matching, scoring, and feedback generation.

Key Features

Resume Parsing: Extracts and standardizes text from PDF and DOCX resumes.

Job Description Parsing: Identifies required skills, qualifications, and preferred experience from job descriptions.

Hybrid Scoring System: Combines hard keyword matching with semantic similarity using embeddings to generate a Relevance Score (0–100).

Missing Skills Detection: Identifies skills or experiences in the JD that are missing from the resume.

Skill Vocabulary: ~80 canonical skills with aliases (e.g. sklearn → scikit-learn, k8s → kubernetes) in skills_db.py, matched on word boundaries so R doesn't match React and C doesn't match C++. Extend it with your own domain skills.

Alias-Aware Resume Matching: Resumes are matched through the same aliases, so a JD asking for scikit-learn credits a resume that says sklearn, and machine learning credits ML. Results show both Matched and Missing skills.

Experience Check: Reads the years a JD asks for ("3+ years", "2-4 years") and estimates the candidate's experience from date ranges under the resume's Experience / Employment / Internship headings (overlapping jobs counted once; project and education dates ignored). Shown in an Experience column, with a feedback note when the resume falls short. Scores are not changed.

Ranked Shortlist: Results are sorted by score with a Rank column, ready for shortlisting.

AI/LLM-based Feedback: Provides tailored feedback to students, highlighting areas for improvement.

Verdict Generation: Categorizes candidates as High, Medium, or Low suitability for a given role.

Batch Processing: Allows evaluation of multiple resumes against a JD at once.

Streamlit Dashboard: User-friendly interface for uploading JDs and resumes, reviewing results, and downloading CSV reports.


Technology Stack

Programming Language: Python

Resume & JD Parsing: pdfplumber, docx2txt, pandas, re

Skill Matching & Scoring: rapidfuzz (fuzzy matching), sentence-transformers (embeddings), cosine similarity

Web Interface: Streamlit

Data Storage: CSV (for evaluation results)

Version Control: Git & GitHub

Installation

Clone the repository:

git clone https://github.com/TrishaChetan/resume_relevance_mvp.git


Navigate to the project folder:

cd resume_relevance_mvp


Create and activate a virtual environment:

python -m venv venv
# Windows
venv\Scripts\activate
# Mac/Linux
source venv/bin/activate


Install dependencies:

pip install -r requirements.txt

Usage

Open the project folder in VSCode or any IDE.

Run the Streamlit app:

streamlit run streamlit_app.py


In the web interface:

Upload a Job Description (JD) file (PDF/DOCX).

Upload one or multiple resumes (PDF/DOCX).

Click Evaluate Resumes.

View Relevance Scores, Missing Skills, Verdicts, and Feedback.

Optionally, download the results as a CSV file.

How it Works

Parsing: Extracts text from resumes and job descriptions.

Hard Match: Checks for exact or fuzzy keyword matches of required skills.

Semantic Match: Uses sentence embeddings and cosine similarity to understand contextual relevance.

Scoring & Verdict: Combines hard and semantic matches to produce a final score and candidate verdict.

Feedback Generation: Suggests improvements based on missing skills or weak matches.

Sample Output
JD	Resume	Score	Missing Skills	Verdict	Feedback
sample_jd_2.pdf	resume-1.pdf	72	['NLP', 'Machine Learning']	Medium	“Consider adding experience or projects on NLP and Machine Learning to better align with the job description.”
Future Improvements

Add support for multiple JDs at once.

Integrate with real-time placement dashboards.

Use advanced NLP models for even more accurate semantic matching.

Add cloud-based storage for large-scale deployments.
