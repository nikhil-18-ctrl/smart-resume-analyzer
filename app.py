# Render redeploy trigger
import os
from flask import Flask, render_template, request
from extractor import extract_text
from matcher import (
    load_skills,
    extract_skills,
    match_skills,
    calculate_ats_score,
    generate_suggestions
)

app = Flask(__name__)

# Folder to store uploaded resumes
UPLOAD_FOLDER = "uploads"
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

# Load skills database once when app starts
skills_list = load_skills("skills.json")


@app.route("/")
def index():
    """
    Home page: Resume upload + Job Description form
    """
    return render_template("index.html")


@app.route("/upload", methods=["POST"])
def upload():
    """
    Handle resume upload, JD matching, ATS scoring, and suggestions
    """
    # Get uploaded resume file
    file = request.files.get("resume")

    # Get job description text safely
    jd_text = request.form.get("jd", "")

    if not file or file.filename == "":
        return "No resume file uploaded"

    # Save resume file
    filepath = os.path.join(UPLOAD_FOLDER, file.filename)
    file.save(filepath)

    # 1️⃣ Extract text from resume
    resume_text = extract_text(filepath)

    # 2️⃣ Extract skills from resume and JD
    resume_skills = extract_skills(resume_text, skills_list)
    jd_skills = extract_skills(jd_text, skills_list)

    # 3️⃣ Match skills
    matched, missing = match_skills(resume_skills, jd_skills)

    # 4️⃣ Calculate ATS score
    score = calculate_ats_score(matched, jd_skills)

    # 5️⃣ Generate resume improvement suggestions
    suggestions = generate_suggestions(missing)

    # 6️⃣ Show results in UI
    return render_template(
        "result.html",
        score=score,
        matched=sorted(matched),
        missing=sorted(missing),
        suggestions=suggestions
    )


if __name__ == "__main__":
    app.run(debug=True)
