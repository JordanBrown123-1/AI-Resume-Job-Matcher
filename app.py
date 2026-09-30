import streamlit as st
from pypdf import PdfReader
import re

def extract_resume_text(pdf_file):
    reader = PdfReader(pdf_file)

    resume_text = ""

    for page in reader.pages:
        text = page.extract_text()

        if text:
            resume_text += text + "\n"

    return resume_text

# Skills that the matcher knows how to identify
SKILLS = {
    "Python": ["python"],
    "Java": ["java"],
    "JavaScript": ["javascript"],
    "SQL": ["sql"],
    "HTML": ["html"],
    "CSS": ["css"],
    "React": ["react", "react.js", "reactjs"],
    "AWS": ["aws", "amazon web services"],
    "Docker": ["docker"],
    "Git": ["git"],
    "GitHub": ["github"],
    "PyTest": ["pytest"],
    "PostgreSQL": ["postgresql", "postgres"],
    "REST API": ["rest api", "rest apis", "restful api"],
    "CI/CD": ["ci/cd", "continuous integration", "continuous delivery"],
    "Object-Oriented Programming": [
        "object-oriented programming",
        "object oriented programming",
        "oop"
    ],
    "Data Structures": ["data structures"],
    "Algorithms": ["algorithms"]
}

def find_skills(text):
    """Find and normalize technical skills mentioned in text."""

    text = text.lower()
    found_skills = []

    for skill_name, variations in SKILLS.items():

        for variation in variations:

            if variation in text:
                found_skills.append(skill_name)
                break

    return found_skills


def analyze_match(resume_text, job_description):
    """Compare resume skills against skills requested by the job."""

    resume_skills = set(find_skills(resume_text))
    job_skills = set(find_skills(job_description))

    matching_skills = resume_skills.intersection(job_skills)
    missing_skills = job_skills.difference(resume_skills)

    if len(job_skills) == 0:
        match_score = 0
    else:
        match_score = round(
            (len(matching_skills) / len(job_skills)) * 100
        )

    return match_score, sorted(matching_skills), sorted(missing_skills)

def generate_recommendations(match_score, matching_skills, missing_skills):
    recommendations = []

    if missing_skills:
        recommendations.append(
            "Consider learning or adding experience with: "
            + ", ".join(missing_skills) + "."
        )

    if "GitHub" in matching_skills or "Git" in matching_skills:
        recommendations.append(
            "Highlight projects where you used Git/GitHub "
            "to collaborate or manage source code."
        )

    if "REST API" in matching_skills:
        recommendations.append(
            "Emphasize projects where you built, tested, "
            "or integrated REST APIs."
        )

    if "PyTest" in matching_skills:
        recommendations.append(
            "Highlight your automated testing experience with PyTest."
        )

    if match_score >= 80:
        recommendations.append(
            "Your technical skills align strongly with this position. "
            "Focus on measurable accomplishments in your resume bullets."
        )
    elif match_score >= 60:
        recommendations.append(
            "Your resume has a solid foundation for this position. "
            "Strengthening the missing skills could improve your match."
        )
    else:
        recommendations.append(
            "Consider building projects that demonstrate more of the "
            "technical skills requested by this position."
        )

    return recommendations

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

    # Check if a resume was uploaded
    if resume_file is None:
        st.warning("Please upload your resume.")

    # Check if a job description was entered
    elif not job_description.strip():
        st.warning("Please paste a job description.")

    # Only analyze after BOTH inputs are provided
    else:
        try:
            # Extract text from PDF
            resume_text = extract_resume_text(resume_file)

            # Check whether text could actually be extracted
            if not resume_text.strip():
                st.error(
                    "Could not read text from this PDF. "
                    "Please upload a text-based PDF resume."
                )

            else:
                st.success("Resume successfully analyzed!")

                st.write("### Resume Preview")

                with st.expander("View extracted resume text"):
                    st.text(resume_text)

                # Compare resume with job description
                match_score, matching_skills, missing_skills = analyze_match(
                    resume_text,
                    job_description
                )
                
                st.divider()
                
                st.header("Resume Match Analysis")
                
                # Match score
                st.subheader("Match Score")
                st.progress(match_score / 100)
                st.metric("Overall Match", f"{match_score}%")
                
                # Matching skills
                st.subheader("Matching Skills")
                
                if matching_skills:
                    for skill in matching_skills:
                        st.write(f"✅ {skill.title()}")
                else:
                    st.write("No matching technical skills were found.")
                
                # Missing skills
                st.subheader("Missing Skills")
                
                if missing_skills:
                    for skill in missing_skills:
                        st.write(f"❌ {skill.title()}")
                else:
                    st.write("No major missing technical skills were detected.")
                
                # Personalized recommendations
                st.subheader("Resume Recommendations")
                
                recommendations = generate_recommendations(
                    match_score,
                    matching_skills,
                    missing_skills
                )
                
                for number, recommendation in enumerate(recommendations, start=1):
                    st.write(f"{number}. {recommendation}")
                )

                except Exception:
                    st.error(
                        "Something went wrong while reading your resume. "
                        "Please upload a valid PDF file."
            )
