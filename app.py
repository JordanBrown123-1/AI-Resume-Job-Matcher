import streamlit as st
from pypdf import PdfReader
import re
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

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

    resume_skills = set(find_skills(resume_text))

    required_text, preferred_text = split_job_description(
        job_description
    )

    required_skills = set(find_skills(required_text))
    preferred_skills = set(find_skills(preferred_text))

    required_matches = resume_skills.intersection(required_skills)
    preferred_matches = resume_skills.intersection(preferred_skills)

    missing_required = required_skills.difference(resume_skills)
    missing_preferred = preferred_skills.difference(resume_skills)

    # Required score
    if required_skills:
        required_score = (
            len(required_matches) / len(required_skills)
        ) * 100
    else:
        required_score = 100

    # Preferred score
    if preferred_skills:
        preferred_score = (
            len(preferred_matches) / len(preferred_skills)
        ) * 100
    else:
        preferred_score = 100

    # Required qualifications matter more
    match_score = round(
        (required_score * 0.75) +
        (preferred_score * 0.25)
    )

    matching_skills = required_matches.union(
        preferred_matches
    )

    missing_skills = missing_required.union(
        missing_preferred
    )

    return (
        match_score,
        round(required_score),
        round(preferred_score),
        sorted(matching_skills),
        sorted(missing_skills),
        sorted(missing_required),
        sorted(missing_preferred)
    )

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

def generate_interview_questions(matching_skills, missing_skills):
    questions = []

    if "Python" in matching_skills:
        questions.append(
            "Tell me about a project where you used Python. "
            "What problem were you trying to solve?"
        )

    if "REST API" in matching_skills:
        questions.append(
            "Describe your experience building or working with REST APIs."
        )

    if "Git" in matching_skills or "GitHub" in matching_skills:
        questions.append(
            "How have you used Git and GitHub when working on software projects?"
        )

    if "Object-Oriented Programming" in matching_skills:
        questions.append(
            "Can you explain object-oriented programming and give an example "
            "of how you used it in a project?"
        )

    if "PyTest" in matching_skills:
        questions.append(
            "How have you used PyTest or automated testing in your projects?"
        )

    if missing_skills:
        questions.append(
            f"This position mentions {missing_skills[0]}. "
            "How would you approach learning a technology you have not used before?"
        )

    return questions[:5]

def split_job_description(job_description):
    """
    Split the job description into required and preferred sections.
    """

    text = job_description.lower()

    preferred_markers = [
        "preferred qualifications:",
        "preferred qualifications",
        "preferred skills:",
        "preferred skills",
        "nice to have:",
        "nice to have"
    ]

    preferred_position = -1

    for marker in preferred_markers:
        position = text.find(marker)

        if position != -1:
            preferred_position = position
            break

    if preferred_position == -1:
        return job_description, ""

    required_text = job_description[:preferred_position]
    preferred_text = job_description[preferred_position:]

    return required_text, preferred_text
    
def calculate_semantic_similarity(resume_text, job_description):
    """
    Compare the overall language of the resume and job description
    using TF-IDF and cosine similarity.
    """

    try:
        documents = [
            resume_text,
            job_description
        ]

        vectorizer = TfidfVectorizer(
            stop_words="english"
        )

        tfidf_matrix = vectorizer.fit_transform(documents)

        similarity = cosine_similarity(
            tfidf_matrix[0:1],
            tfidf_matrix[1:2]
        )[0][0]

        similarity_score = round(similarity * 100)

        return similarity_score

    except ValueError:
        return 0
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
                (
                    match_score,
                    required_score,
                    preferred_score,
                    matching_skills,
                    missing_skills,
                    missing_required,
                    missing_preferred
                ) = analyze_match(
                    resume_text,
                    job_description
                )

                semantic_score = calculate_semantic_similarity(
                    resume_text,
                    job_description
                )
                                
                st.divider()
                
                st.header("Resume Match Analysis")
                
                # Match score
                st.subheader("Match Score")
                st.progress(match_score / 100)
                st.metric("Overall Match", f"{match_score}%")
                
                # Required vs Preferred breakdown
                st.subheader("Analysis Breakdown")
                col1, col2, col3 = st.columns(3)
                
                with col1:
                    st.metric(
                        "Required Skills",
                        f"{required_score}%"
                    )
                
                with col2:
                    st.metric(
                        "Preferred Skills",
                        f"{preferred_score}%"
                    )
                
                with col3:
                    st.metric(
                        "NLP Similarity",
                        f"{semantic_score}%"
                    )

                with st.expander("What do these scores mean?"):
                    st.write(
                        "**Overall Match:** Weighted qualification score based on "
                        "required and preferred technical skills."
                    )
                
                    st.write(
                        "**Required Skills:** Percentage of detected required "
                        "technical skills found in your resume."
                    )
                
                    st.write(
                        "**Preferred Skills:** Percentage of detected preferred "
                        "technical skills found in your resume."
                    )
                
                    st.write(
                        "**NLP Similarity:** Uses TF-IDF and cosine similarity to "
                        "compare the overall language of your resume with the "
                        "job description."
                    )
                
                # Matching and missing skills side-by-side
                st.subheader("Skills Analysis")
                
                skills_col1, skills_col2 = st.columns(2)
                
                with skills_col1:
                    st.markdown("### ✅ Matching Skills")
                
                    if matching_skills:
                        for skill in matching_skills:
                            st.write(f"✅ {skill}")
                    else:
                        st.write("No matching technical skills found.")
                
                with skills_col2:
                    st.markdown("### ❌ Missing Skills")
                
                    if missing_skills:
                        for skill in missing_skills:
                            st.write(f"❌ {skill}")
                    else:
                        st.write("No major missing technical skills detected.")
                
                # Personalized recommendations
                st.subheader("Resume Recommendations")
    
                recommendations = generate_recommendations(
                    match_score,
                    matching_skills,
                    missing_skills
                )
    
                for number, recommendation in enumerate(recommendations, start=1):
                    st.write(f"{number}. {recommendation}")
                # Interview questions
                st.subheader("Potential Interview Questions")
                
                interview_questions = generate_interview_questions(
                    matching_skills,
                    missing_skills
                )
                
                for number, question in enumerate(interview_questions, start=1):
                    st.write(f"{number}. {question}")

                # Create downloadable analysis report
                report = f"""
                AI Resume & Job Matcher
                =======================
                
                Overall Match: {match_score}%
                Required Skills Match: {required_score}%
                Preferred Skills Match: {preferred_score}%
                NLP Similarity: {semantic_score}%
                
                MATCHING SKILLS
                ---------------
                {chr(10).join(matching_skills)}
                
                MISSING SKILLS
                --------------
                {chr(10).join(missing_skills)}
                
                RESUME RECOMMENDATIONS
                ----------------------
                {chr(10).join(
                    f"{i}. {recommendation}"
                    for i, recommendation in enumerate(recommendations, start=1)
                )}
                
                POTENTIAL INTERVIEW QUESTIONS
                -----------------------------
                {chr(10).join(
                    f"{i}. {question}"
                    for i, question in enumerate(interview_questions, start=1)
                )}
                """
                
                st.divider()
                
                st.download_button(
                    label="📥 Download Analysis Report",
                    data=report,
                    file_name="resume_job_analysis.txt",
                    mime="text/plain"
                )
                st.caption(
                    "This analysis is an estimate based on detected technical skills "
                    "and text similarity. It is not an official ATS or employer score."
                )
        except Exception:
                st.error(
                    "Something went wrong while reading your resume. "
                    "Please upload a valid PDF file."
                )

               
