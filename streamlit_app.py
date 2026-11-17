import streamlit as st
import os
import shutil
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
        # start clean so resumes from a previous run aren't scored again
        shutil.rmtree(resumes_folder, ignore_errors=True)
        os.makedirs(resumes_folder, exist_ok=True)
        for resume in resumes_files:
            with open(os.path.join(resumes_folder, resume.name), "wb") as f:
                f.write(resume.getbuffer())

        # Run batch process
        with st.spinner(f"Scoring {len(resumes_files)} resume(s)..."):
            df = batch_process(jd_path, resumes_folder)

        # Display results
        pri = df.attrs.get("jd_priorities") or {}
        must = [s for s, p in pri.items() if p == "must"]
        nice = [s for s, p in pri.items() if p == "nice"]
        if must or nice:
            st.subheader("What the JD asks for")
            c1, c2, c3 = st.columns(3)
            c1.markdown("**Must have** (2× weight)\n\n" + (", ".join(must) or "—"))
            c2.markdown("**Mentioned** (1×)\n\n" + (", ".join(s for s, p in pri.items() if p == "core") or "—"))
            c3.markdown("**Nice to have** (0.5×)\n\n" + (", ".join(nice) or "—"))
            st.caption("Candidates missing a must-have can't get a High verdict.")

        st.subheader("Evaluation Results")
        st.dataframe(df)

        # CSV download
        csv = df.to_csv(index=False).encode('utf-8')
        st.download_button("Download Results CSV", data=csv, file_name="resume_evaluation_results.csv", mime="text/csv")
    else:
        st.warning("Please upload a JD and at least one resume to evaluate.")
