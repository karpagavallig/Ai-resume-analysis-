from pypdf import PdfReader
from docx import Document
import os
import re


# ==========================================
# EXTRACT TEXT FROM PDF
# ==========================================

def extract_pdf_text(file_path):
    text = ""

    reader = PdfReader(file_path)

    for page in reader.pages:
        page_text = page.extract_text()

        if page_text:
            text += page_text + "\n"

    return text


# ==========================================
# EXTRACT TEXT FROM DOCX
# ==========================================

def extract_docx_text(file_path):
    text = ""

    document = Document(file_path)

    for paragraph in document.paragraphs:
        if paragraph.text.strip():
            text += paragraph.text + "\n"

    return text


# ==========================================
# EXTRACT RESUME TEXT
# ==========================================

def extract_resume_text(file_path):

    extension = os.path.splitext(file_path)[1].lower()

    if extension == ".pdf":
        return extract_pdf_text(file_path)

    elif extension == ".docx":
        return extract_docx_text(file_path)

    else:
        return ""


# ==========================================
# DETECT SKILLS
# ==========================================

SKILLS = [
    "python",
    "java",
    "c",
    "c++",
    "javascript",
    "html",
    "css",
    "sql",
    "mysql",
    "mongodb",
    "flask",
    "django",
    "react",
    "node.js",
    "machine learning",
    "deep learning",
    "artificial intelligence",
    "tensorflow",
    "keras",
    "pandas",
    "numpy",
    "power bi",
    "excel",
    "git",
    "github",
    "aws",
    "azure",
    "docker"
]


def extract_skills(text):

    text_lower = text.lower()

    found_skills = []

    for skill in SKILLS:

        if skill.lower() in text_lower:
            found_skills.append(skill)

    return sorted(set(found_skills))


# ==========================================
# EXTRACT EMAIL
# ==========================================

def extract_email(text):

    pattern = r'[\w\.-]+@[\w\.-]+\.\w+'

    match = re.search(pattern, text)

    if match:
        return match.group(0)

    return "Not found"


# ==========================================
# EXTRACT PHONE NUMBER
# ==========================================

def extract_phone(text):

    pattern = r'(\+91[\s-]?)?[6-9]\d{9}'

    match = re.search(pattern, text)

    if match:
        return match.group(0)

    return "Not found"


# ==========================================
# CALCULATE ATS SCORE
# ==========================================

def calculate_ats_score(text, skills):

    score = 0

    text_lower = text.lower()

    # Skills
    if len(skills) >= 8:
        score += 30

    elif len(skills) >= 5:
        score += 25

    elif len(skills) >= 3:
        score += 18

    elif len(skills) >= 1:
        score += 10


    # Resume sections
    sections = {
        "education": 10,
        "experience": 15,
        "skills": 15,
        "project": 10,
        "certificate": 5,
        "summary": 5
    }

    for section, points in sections.items():

        if section in text_lower:
            score += points


    # Contact details
    if extract_email(text) != "Not found":
        score += 2

    if extract_phone(text) != "Not found":
        score += 3


    return min(score, 100)


# ==========================================
# FIND MISSING SKILLS
# ==========================================

def find_missing_skills(skills):

    important_skills = [
        "python",
        "sql",
        "git",
        "github",
        "machine learning",
        "javascript",
        "html",
        "css",
        "flask"
    ]

    missing = []

    for skill in important_skills:

        if skill not in skills:
            missing.append(skill)

    return missing


# ==========================================
# FIND STRENGTHS
# ==========================================

def find_strengths(text, skills):

    text_lower = text.lower()

    strengths = []

    if len(skills) >= 5:
        strengths.append(
            "Good technical skill coverage."
        )

    if "project" in text_lower:
        strengths.append(
            "Projects section is included."
        )

    if "education" in text_lower:
        strengths.append(
            "Education details are available."
        )

    if "experience" in text_lower:
        strengths.append(
            "Work experience is included."
        )

    if "certificate" in text_lower:
        strengths.append(
            "Certifications are included."
        )

    if not strengths:
        strengths.append(
            "Resume contains basic information."
        )

    return strengths


# ==========================================
# GENERATE SUGGESTIONS
# ==========================================

def generate_suggestions(text, skills):

    text_lower = text.lower()

    suggestions = []

    if len(skills) < 5:
        suggestions.append(
            "Add more relevant technical skills."
        )

    if "summary" not in text_lower:
        suggestions.append(
            "Add a professional summary at the beginning."
        )

    if "project" not in text_lower:
        suggestions.append(
            "Add 2–3 relevant projects with measurable results."
        )

    if "certificate" not in text_lower:
        suggestions.append(
            "Add relevant certifications."
        )

    if "experience" not in text_lower:
        suggestions.append(
            "Add internship or work experience if available."
        )

    if "github" not in text_lower:
        suggestions.append(
            "Add your GitHub profile if you have technical projects."
        )

    return suggestions


# ==========================================
# MAIN RESUME ANALYSIS
# ==========================================

def analyze_resume(text):

    skills = extract_skills(text)

    ats_score = calculate_ats_score(
        text,
        skills
    )

    missing_skills = find_missing_skills(
        skills
    )

    strengths = find_strengths(
        text,
        skills
    )

    suggestions = generate_suggestions(
        text,
        skills
    )

    email = extract_email(text)

    phone = extract_phone(text)


    return {

        "ats_score": ats_score,

        "skills": skills,

        "missing_skills": missing_skills,

        "strengths": strengths,

        "suggestions": suggestions,

        "email": email,

        "phone": phone
    }


# ==========================================
# TEST
# ==========================================

if __name__ == "__main__":

    print("AI Resume Analyzer is ready!")
