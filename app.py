
from flask import (
    Flask,
    render_template,
    request,
    redirect,
    url_for,
    session,
    flash,
    send_file
)

import sqlite3
import os
import re
from io import BytesIO

from werkzeug.utils import secure_filename
from pypdf import PdfReader
from docx import Document

from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.enums import TA_CENTER
from reportlab.lib.units import mm
from reportlab.platypus import (
    SimpleDocTemplate,
    Paragraph,
    Spacer,
    Table,
    TableStyle
)


# ==========================================================
# APPLICATION
# ==========================================================

app = Flask(__name__)

app.secret_key = "resumeai_secret_2026"

DATABASE = "database.db"

UPLOAD_FOLDER = os.path.join(
    "static",
    "uploads"
)

os.makedirs(
    UPLOAD_FOLDER,
    exist_ok=True
)

app.config["UPLOAD_FOLDER"] = UPLOAD_FOLDER

ALLOWED_EXTENSIONS = {
    "pdf",
    "docx"
}


# ==========================================================
# DATABASE
# ==========================================================

def init_db():

    conn = sqlite3.connect(DATABASE)

    cursor = conn.cursor()

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT NOT NULL,
            email TEXT UNIQUE NOT NULL,
            password TEXT NOT NULL
        )
    """)

    conn.commit()

    conn.close()


# ==========================================================
# FILE CHECK
# ==========================================================

def allowed_file(filename):

    if "." not in filename:
        return False

    extension = filename.rsplit(
        ".",
        1
    )[1].lower()

    return extension in ALLOWED_EXTENSIONS


# ==========================================================
# HOME
# ==========================================================

@app.route("/")
def home():

    return render_template(
        "index.html"
    )


# ==========================================================
# REGISTER
# ==========================================================

@app.route(
    "/register",
    methods=["GET", "POST"]
)
def register():

    if request.method == "POST":

        username = request.form.get(
            "username",
            ""
        ).strip()

        email = request.form.get(
            "email",
            ""
        ).strip()

        password = request.form.get(
            "password",
            ""
        ).strip()


        if not username or not email or not password:

            flash(
                "Please fill in all fields."
            )

            return redirect(
                url_for("register")
            )


        if len(password) < 6:

            flash(
                "Password must contain at least 6 characters."
            )

            return redirect(
                url_for("register")
            )


        try:

            conn = sqlite3.connect(
                DATABASE
            )

            cursor = conn.cursor()

            cursor.execute(
                """
                INSERT INTO users
                (username, email, password)
                VALUES (?, ?, ?)
                """,
                (
                    username,
                    email,
                    password
                )
            )

            conn.commit()

            conn.close()

            flash(
                "Registration successful."
            )

            return redirect(
                url_for("login")
            )


        except sqlite3.IntegrityError:

            flash(
                "Email already registered."
            )

            return redirect(
                url_for("register")
            )


# ==========================================================
# LOGIN
# ==========================================================

@app.route(
    "/login",
    methods=["GET", "POST"]
)
def login():

    if request.method == "POST":

        email = request.form.get(
            "email",
            ""
        ).strip()

        password = request.form.get(
            "password",
            ""
        ).strip()


        conn = sqlite3.connect(
            DATABASE
        )

        cursor = conn.cursor()

        cursor.execute(
            """
            SELECT id, username, email
            FROM users
            WHERE email = ? AND password = ?
            """,
            (
                email,
                password
            )
        )

        user = cursor.fetchone()

        conn.close()


        if user:

            session["user_id"] = user[0]

            session["username"] = user[1]

            session["email"] = user[2]

            return redirect(
                url_for("dashboard")
            )


        flash(
            "Invalid email or password."
        )

        return redirect(
            url_for("login")
        )


    return render_template(
        "login.html"
    )


# ==========================================================
# LOGOUT
# ==========================================================

@app.route("/logout")
def logout():

    session.clear()

    return redirect(
        url_for("login")
    )


# ==========================================================
# DASHBOARD
# ==========================================================

@app.route("/dashboard")
def dashboard():

    if "user_id" not in session:

        return redirect(
            url_for("login")
        )


    return render_template(
        "dashboard.html",
        username=session.get(
            "username",
            "User"
        ),
        email=session.get(
            "email",
            ""
        )
    )


# ==========================================================
# PDF TEXT EXTRACTION
# ==========================================================

def extract_pdf_text(filepath):

    text = ""

    reader = PdfReader(
        filepath
    )

    for page in reader.pages:

        try:

            page_text = page.extract_text()

            if page_text:

                text += page_text + "\n"

        except Exception:

            pass


    return text


# ==========================================================
# DOCX TEXT EXTRACTION
# ==========================================================

def extract_docx_text(filepath):

    document = Document(
        filepath
    )

    text = []

    for paragraph in document.paragraphs:

        value = paragraph.text.strip()

        if value:

            text.append(
                value
            )


    return "\n".join(text)


# ==========================================================
# RESUME ANALYZER
# ==========================================================

def analyze_resume(text):

    text_lower = text.lower()


    skills_database = [

        "python",
        "java",
        "c++",
        "c programming",
        "javascript",
        "html",
        "css",
        "flask",
        "django",
        "react",
        "node.js",
        "tensorflow",
        "keras",
        "pytorch",
        "machine learning",
        "deep learning",
        "artificial intelligence",
        "sql",
        "mysql",
        "postgresql",
        "mongodb",
        "git",
        "github",
        "aws",
        "azure",
        "google cloud",
        "docker",
        "pandas",
        "numpy",
        "opencv",
        "power bi",
        "excel",
        "communication",
        "leadership",
        "teamwork",
        "problem solving"

    ]


    skills = []

    for skill in skills_database:

        if skill in text_lower:

            skills.append(
                skill.title()
            )


    # EMAIL

    email_pattern = (
        r"[A-Za-z0-9._%+-]+"
        r"@[A-Za-z0-9.-]+\.[A-Za-z]{2,}"
    )

    emails = re.findall(
        email_pattern,
        text
    )


    # PHONE

    phone_pattern = (
        r"(?:\+91[\s-]?)?[6-9]\d{9}"
    )

    phones = re.findall(
        phone_pattern,
        text
    )


    # SECTIONS

    section_keywords = {

        "Education": [
            "education",
            "academic",
            "qualification"
        ],

        "Experience": [
            "experience",
            "work experience",
            "employment"
        ],

        "Internship": [
            "internship",
            "intern"
        ],

        "Projects": [
            "projects",
            "project"
        ],

        "Certifications": [
            "certification",
            "certifications",
            "certificate"
        ],

        "Skills": [
            "skills",
            "technical skills"
        ],

        "Languages": [
            "languages"
        ],

        "Achievements": [
            "achievement",
            "achievements",
            "awards"
        ]

    }


    sections = []


    for section, keywords in section_keywords.items():

        for keyword in keywords:

            if keyword in text_lower:

                sections.append(
                    section
                )

                break


    # WORD COUNT

    word_count = len(
        text.split()
    )


    # ATS SCORE

    score = 0


    if emails:
        score += 10

    if phones:
        score += 10

    if len(skills) >= 10:
        score += 20

    elif len(skills) >= 7:
        score += 17

    elif len(skills) >= 4:
        score += 12

    elif len(skills) >= 1:
        score += 6


    if "Education" in sections:
        score += 10

    if "Experience" in sections:
        score += 10

    if "Internship" in sections:
        score += 5

    if "Projects" in sections:
        score += 10

    if "Certifications" in sections:
        score += 5

    if "Skills" in sections:
        score += 5

    if "Achievements" in sections:
        score += 5


    if word_count >= 400:
        score += 10

    elif word_count >= 250:
        score += 7

    elif word_count >= 150:
        score += 4


    score = min(
        score,
        100
    )


    # STRENGTH

    if score >= 85:

        strength = "Excellent"

    elif score >= 70:

        strength = "Very Good"

    elif score >= 55:

        strength = "Good"

    elif score >= 40:

        strength = "Average"

    else:

        strength = "Needs Improvement"


    # STRENGTHS

    strengths = []


    if emails:

        strengths.append(
            "Professional email address is included."
        )


    if phones:

        strengths.append(
            "Contact phone number is included."
        )


    if len(skills) >= 7:

        strengths.append(
            "Strong technical skill coverage."
        )

    elif len(skills) >= 4:

        strengths.append(
            "Good technical skill coverage."
        )

    elif skills:

        strengths.append(
            "Technical skills are present."
        )


    if "Education" in sections:

        strengths.append(
            "Education information is clearly included."
        )


    if "Projects" in sections:

        strengths.append(
            "Projects demonstrate practical knowledge."
        )


    if "Experience" in sections:

        strengths.append(
            "Professional experience is included."
        )


    if "Internship" in sections:

        strengths.append(
            "Internship experience is included."
        )


    if "Certifications" in sections:

        strengths.append(
            "Certifications are included."
        )


    if "Achievements" in sections:

        strengths.append(
            "Achievements or awards are mentioned."
        )


    if word_count >= 250:

        strengths.append(
            "Resume contains sufficient relevant information."
        )


    if not strengths:

        strengths.append(
            "Basic resume information is available."
        )


    # MISSING SKILLS

    recommended = [

        "Python",
        "SQL",
        "Git",
        "Machine Learning",
        "Communication",
        "Problem Solving",
        "Cloud Computing",
        "Data Analysis"

    ]


    missing_skills = []


    for skill in recommended:

        if skill.lower() not in text_lower:

            missing_skills.append(
                skill
            )


    # SUGGESTIONS

    suggestions = []


    if not emails:

        suggestions.append(
            "Add a professional email address."
        )


    if not phones:

        suggestions.append(
            "Add a contact phone number."
        )


    if len(skills) < 5:

        suggestions.append(
            "Add more technical skills relevant to your target job."
        )


    if "Projects" not in sections:

        suggestions.append(
            "Add academic or personal projects."
        )


    if (
        "Experience" not in sections
        and
        "Internship" not in sections
    ):

        suggestions.append(
            "Add internship or practical experience."
        )


    if "Certifications" not in sections:

        suggestions.append(
            "Add relevant certifications."
        )


    if word_count < 250:

        suggestions.append(
            "Add more relevant details while keeping the resume concise."
        )


    if not suggestions:

        suggestions.append(
            "Your resume is well structured. Continue tailoring it to each job."
        )


    # PROFESSIONAL IMPROVEMENTS

    improvements = []


    if (
        "summary" not in text_lower
        and
        "objective" not in text_lower
        and
        "profile" not in text_lower
    ):

        improvements.append(
            "Add a professional summary at the beginning."
        )


    action_words = [

        "developed",
        "designed",
        "implemented",
        "created",
        "built",
        "managed",
        "analyzed",
        "improved",
        "optimized"

    ]


    if not any(
        word in text_lower
        for word in action_words
    ):

        improvements.append(
            "Use strong action verbs such as Developed, Designed and Implemented."
        )


    if not re.search(
        r"\b\d+%?\b",
        text
    ):

        improvements.append(
            "Add measurable results using numbers or percentages."
        )


    improvements.append(
        "Customize your resume for the job description you are applying for."
    )


    return {

        "ats_score": score,

        "strength": strength,

        "strengths": strengths,

        "skills": skills,

        "missing_skills": missing_skills,

        "sections": sections,

        "email": emails[0]
        if emails
        else "Not detected",

        "phone": phones[0]
        if phones
        else "Not detected",

        "word_count": word_count,

        "suggestions": suggestions,

        "improvements": improvements

    }


# ==========================================================
# RESUME IMPROVEMENT ENGINE
# ==========================================================

def generate_improved_resume(text):

    lines = text.splitlines()

    improved = []


    # Professional action replacements

    replacements = {

        "worked on":
            "Developed and contributed to",

        "responsible for":
            "Managed and executed",

        "helped with":
            "Supported and contributed to",

        "helped":
            "Supported",

        "used":
            "Utilized",

        "made":
            "Developed",

        "did":
            "Executed",

        "participated in":
            "Actively contributed to",

        "learned":
            "Gained practical experience in",

        "worked":
            "Collaborated and contributed"

    }


    for line in lines:

        line = line.strip()


        if not line:

            continue


        # Remove existing bullet symbols

        line = line.lstrip(
            "•-*✓➢"
        ).strip()


        # Skip very short lines

        if len(line.split()) < 5:

            continue


        # Skip contact information

        if "@" in line:

            continue


        lower = line.lower()

        new_line = line


        for old, new in replacements.items():

            if old in lower:

                pattern = re.compile(
                    re.escape(old),
                    re.IGNORECASE
                )

                new_line = pattern.sub(
                    new,
                    new_line,
                    count=1
                )

                break


        # Add professional punctuation

        if not new_line.endswith("."):

            new_line += "."


        improved.append(
            new_line
        )


    # Remove duplicates

    final_result = []


    for item in improved:

        if item not in final_result:

            final_result.append(
                item
            )


    # If original resume has very little usable text

    if not final_result:

        final_result = [

            "Developed and contributed to technical projects using relevant technologies.",

            "Implemented practical solutions while applying analytical and problem-solving skills.",

            "Collaborated effectively with team members to achieve project objectives.",

            "Applied technical knowledge to develop practical and user-focused solutions.",

            "Demonstrated strong communication, teamwork, and continuous learning abilities."

        ]


    return final_result[:20]


# ==========================================================
# ANALYZE RESUME
# ==========================================================

@app.route(
    "/analyze",
    methods=["POST"]
)
def analyze():

    if "user_id" not in session:

        return redirect(
            url_for("login")
        )


    if "resume" not in request.files:

        flash(
            "Please select a resume."
        )

        return redirect(
            url_for("dashboard")
        )


    file = request.files["resume"]


    if file.filename == "":

        flash(
            "Please select a resume."
        )

        return redirect(
            url_for("dashboard")
        )


    if not allowed_file(
        file.filename
    ):

        flash(
            "Only PDF and DOCX files are supported."
        )

        return redirect(
            url_for("dashboard")
        )


    filename = secure_filename(
        file.filename
    )


    filepath = os.path.join(
        app.config["UPLOAD_FOLDER"],
        filename
    )


    try:

        file.save(
            filepath
        )


        extension = filename.rsplit(
            ".",
            1
        )[1].lower()


        if extension == "pdf":

            text = extract_pdf_text(
                filepath
            )

        else:

            text = extract_docx_text(
                filepath
            )


    except Exception as error:

        flash(
            "Resume processing failed: "
            + str(error)
        )

        return redirect(
            url_for("dashboard")
        )


    if not text.strip():

        flash(
            "No readable text found in the resume."
        )

        return redirect(
            url_for("dashboard")
        )


    result = analyze_resume(
        text
    )


    # Store data in session

    session["resume_text"] = text

    session["resume_filename"] = filename

    session["analysis_result"] = result


    return render_template(
        "result.html",
        result=result,
        filename=filename,
        username=session.get(
            "username",
            "User"
        )
    )


# ==========================================================
# IMPROVE RESUME
# ==========================================================

@app.route("/rewrite")
def rewrite():

    # Check login

    if "user_id" not in session:

        return redirect(
            url_for("login")
        )


    # Get uploaded resume text

    resume_text = session.get(
        "resume_text",
        ""
    )


    # If there is no resume

    if not resume_text:

        flash(
            "Please upload and analyze a resume first."
        )

        return redirect(
            url_for("dashboard")
        )


    # Generate improvements

    improved_resume = generate_improved_resume(
        resume_text
    )


    # Display improvement page

    return render_template(
        "rewrite.html",
        rewritten=improved_resume,
        username=session.get(
            "username",
            "User"
        )
    )


# ==========================================================
# DOWNLOAD PDF REPORT
# ==========================================================

@app.route("/download-report")
def download_report():

    if "user_id" not in session:

        return redirect(
            url_for("login")
        )


    result = session.get(
        "analysis_result"
    )


    filename = session.get(
        "resume_filename",
        "resume.pdf"
    )


    if not result:

        flash(
            "Please analyze a resume first."
        )

        return redirect(
            url_for("dashboard")
        )


    buffer = BytesIO()


    pdf = SimpleDocTemplate(

        buffer,

        pagesize=A4,

        rightMargin=18 * mm,

        leftMargin=18 * mm,

        topMargin=18 * mm,

        bottomMargin=18 * mm

    )


    styles = getSampleStyleSheet()


    title_style = ParagraphStyle(

        "TitleStyle",

        parent=styles["Title"],

        fontSize=24,

        alignment=TA_CENTER,

        textColor=colors.HexColor(
            "#4F46E5"
        ),

        spaceAfter=10

    )


    heading_style = ParagraphStyle(

        "HeadingStyle",

        parent=styles["Heading2"],

        fontSize=15,

        textColor=colors.HexColor(
            "#111827"
        ),

        spaceBefore=15,

        spaceAfter=8

    )


    normal_style = ParagraphStyle(

        "NormalStyle",

        parent=styles["Normal"],

        fontSize=9.5,

        leading=14

    )


    story = []


    story.append(
        Paragraph(
            "ResumeAI",
            title_style
        )
    )


    story.append(
        Paragraph(
            "Professional Resume Analysis Report",
            normal_style
        )
    )


    story.append(
        Spacer(
            1,
            15
        )
    )


    # SCORE

    story.append(
        Paragraph(
            "ATS Score",
            heading_style
        )
    )


    score_data = [

        [
            "ATS Score",
            str(result["ats_score"]) + "/100"
        ],

        [
            "Resume Strength",
            result["strength"]
        ],

        [
            "Word Count",
            str(result["word_count"])
        ]

    ]


    table = Table(
        score_data,
        colWidths=[
            70 * mm,
            70 * mm
        ]
    )


    table.setStyle(
        TableStyle([

            (
                "GRID",
                (0, 0),
                (-1, -1),
                0.5,
                colors.grey
            ),

            (
                "FONTNAME",
                (0, 0),
                (0, -1),
                "Helvetica-Bold"
            ),

            (
                "PADDING",
                (0, 0),
                (-1, -1),
                8
            )

        ])
    )


    story.append(
        table
    )


    # STRENGTHS

    story.append(
        Paragraph(
            "Resume Strengths",
            heading_style
        )
    )


    for item in result["strengths"]:

        story.append(
            Paragraph(
                "• " + item,
                normal_style
            )
        )


        story.append(
            Spacer(
                1,
                4
            )
        )


    # SKILLS

    story.append(
        Paragraph(
            "Detected Skills",
            heading_style
        )
    )


    skills_text = ", ".join(
        result["skills"]
    )


    if not skills_text:

        skills_text = "No skills detected."


    story.append(
        Paragraph(
            skills_text,
            normal_style
        )
    )


    # MISSING SKILLS

    story.append(
        Paragraph(
            "Recommended Skills",
            heading_style
        )
    )


    missing_text = ", ".join(
        result["missing_skills"]
    )


    if not missing_text:

        missing_text = "No major missing skills."


    story.append(
        Paragraph(
            missing_text,
            normal_style
        )
    )


    # SUGGESTIONS

    story.append(
        Paragraph(
            "AI Suggestions",
            heading_style
        )
    )


    for item in result["suggestions"]:

        story.append(
            Paragraph(
                "• " + item,
                normal_style
            )
        )


    # IMPROVEMENTS

    story.append(
        Paragraph(
            "Professional Improvements",
            heading_style
        )
    )


    for item in result["improvements"]:

        story.append(
            Paragraph(
                "• " + item,
                normal_style
            )
        )


    pdf.build(
        story
    )


    buffer.seek(0)


    return send_file(

        buffer,

        as_attachment=True,

        download_name="ResumeAI_Report.pdf",

        mimetype="application/pdf"

    )


# ==========================================================
# ERROR PAGES
# ==========================================================

@app.errorhandler(404)
def not_found(error):

    return """

    <h1>404 - Page Not Found</h1>

    <p>The requested page does not exist.</p>

    <a href="/">Go to ResumeAI</a>

    """, 404


@app.errorhandler(500)
def server_error(error):

    return """

    <h1>500 - Server Error</h1>

    <p>Something went wrong.</p>

    <a href="/">Go to ResumeAI</a>

    """, 500


# ==========================================================
# START
# ==========================================================

if __name__ == "__main__":

    init_db()

    print("")
    print("========================================")
    print("       RESUME AI SERVER")
    print("========================================")
    print("URL: http://127.0.0.1:5000")
    print("========================================")
    print("")

    app.run(
        debug=True,
        host="127.0.0.1",
        port=5000
    )
