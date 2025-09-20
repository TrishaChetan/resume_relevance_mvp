import streamlit as st
import os
from batch_process import batch_process

st.set_page_config(page_title="Resume Relevance Checker", layout="wide")
st.title("Automated Resume Relevance Check System")

# Upload JD
jd_file = st.file_uploader("Upload Job Description (PDF/DOCX)", type=["pdf", "docx"])
# Upload resumes
resumes_files = st.file_uploader("Upload Resumes (multiple)", type=["pdf", "docx"], accept_multiple_files=True)

if st.button("Evaluate Resumes"):
    if jd_file and resumes_files:
        # Save JD temporarily
        jd_path = f"temp_jd.{jd_file.name.split('.')[-1]}"
        with open(jd_path, "wb") as f:
            f.write(jd_file.getbuffer())

        # Save resumes temporarily
        resumes_folder = "temp_resumes/"
        os.makedirs(resumes_folder, exist_ok=True)
        for resume in resumes_files:
            with open(os.path.join(resumes_folder, resume.name), "wb") as f:
                f.write(resume.getbuffer())

        # Run batch process
        df = batch_process(jd_path, resumes_folder)

        # Display results
        st.subheader("Evaluation Results")
        st.dataframe(df)

        # CSV download
        csv = df.to_csv(index=False).encode('utf-8')
        st.download_button("Download Results CSV", data=csv, file_name="resume_evaluation_results.csv", mime="text/csv")
    else:
        st.warning("Please upload a JD and at least one resume to evaluate.")
