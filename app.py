import streamlit as st

# Page configuration
st.set_page_config(
    page_title="AI Resume Job Matcher",
    page_icon="📄",
    layout="centered"
)

# App title
st.title("📄 AI Resume & Job Matcher")

st.write(
    "Upload your resume and paste a job description to see "
    "how well your experience matches the position."
)

st.divider()

# Resume upload
st.subheader("1. Upload Your Resume")

resume_file = st.file_uploader(
    "Upload your resume as a PDF",
    type=["pdf"]
)

# Job description
st.subheader("2. Paste the Job Description")

job_description = st.text_area(
    "Job Description",
    placeholder="Paste the full job description here...",
    height=250
)

# Analyze button
if st.button("Analyze Resume", type="primary"):

    if resume_file is None:
        st.warning("Please upload your resume.")

    elif not job_description.strip():
        st.warning("Please paste a job description.")

    else:
        st.success("Resume and job description received!")

        st.write("### Analysis")
        st.write("AI analysis will appear here in the next version.")
