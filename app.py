import streamlit as st
from pypdf import PdfReader

def extract_resume_text(pdf_file):
    reader = PdfReader(pdf_file)

    resume_text = ""

    for page in reader.pages:
        text = page.extract_text()

        if text:
            resume_text += text + "\n"

    return resume_text

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
    # Extract text from the uploaded PDF
    resume_text = extract_resume_text(resume_file)

    if not resume_text.strip():
        st.error("Could not read text from this PDF.")
    else:
        st.success("Resume successfully analyzed!")

        st.write("### Resume Preview")

        with st.expander("View extracted resume text"):
            st.text(resume_text)

        st.write("### Job Description Received")
        st.write(job_description)

        st.info("AI matching will be added in the next step.")
