import streamlit as st
import os
import shutil
from batch_process import batch_process
from interview_kit import build_kit, kit_markdown, kits_zip

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
        # keep results across reruns (e.g. picking a candidate below)
        st.session_state.results = df
        st.session_state.jd_priorities = df.attrs.get("jd_priorities") or {}
        st.session_state.jd_name = jd_file.name
    else:
        st.warning("Please upload a JD and at least one resume to evaluate.")

if "results" in st.session_state:
    df = st.session_state.results
    # Display results
    pri = st.session_state.jd_priorities
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

    # Interview kits
    st.subheader("🎤 Interview kits")
    st.caption("Questions to check the skills each candidate claims, and to explore what's missing.")
    rows = df.to_dict("records")
    labels = [f"#{r.get('Rank', i + 1)} {r.get('Name') or r['Resume']} — {r['Score']} ({r['Verdict']})"
              for i, r in enumerate(rows)]
    pick = st.selectbox("Candidate", range(len(rows)), format_func=lambda i: labels[i])
    r = rows[pick]
    split = lambda v: [s.strip() for s in str(v or "").split(",") if s.strip()]
    kit = build_kit(r.get("Name") or r["Resume"], split(r["Matched"]), split(r["Missing"]), pri, str(r["Experience"]))
    md = kit_markdown(kit, st.session_state.jd_name)
    with st.expander("Preview", expanded=True):
        st.markdown(md)
    c1, c2 = st.columns(2)
    c1.download_button("Download this kit (.md)", md, file_name=f"interview-kit-{pick + 1}.md", mime="text/markdown")
    c2.download_button("Download all kits (.zip)", kits_zip(rows, pri, st.session_state.jd_name),
                       file_name="interview-kits.zip", mime="application/zip")
