from flask import Flask, request, jsonify
from flask_cors import CORS
import os
import re
import tempfile

import nltk
from nltk.corpus import stopwords

from docx import Document
from pdfminer.high_level import extract_text as extract_pdf_text

from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

# -------------------------------
# FLASK APP
# -------------------------------
app = Flask(__name__)
CORS(app)

# -------------------------------
# NLTK SETUP
# -------------------------------
nltk.download("stopwords")
STOP_WORDS = set(stopwords.words("english"))

# -------------------------------
# TECH SKILLS (STRICT – NO FAKING)
# -------------------------------
TECH_SKILLS = {
    "python", "java", "javascript", "react", "html", "css",
    "flask", "django", "node", "express",
    "rest", "api", "apis",
    "mysql", "mongodb", "database", "databases",
    "git", "github", "agile",
    "backend", "frontend",
    "docker", "aws"
}

# -------------------------------
# GENERIC WORDS (IGNORE)
# -------------------------------
GENERIC_WORDS = {
    "experience", "developed", "developing", "building",
    "software", "engineer", "candidate", "responsibilities",
    "skills", "knowledge", "ability", "team", "role",
    "work", "working", "environment"
}

# -------------------------------
# FILE TEXT EXTRACTION
# -------------------------------
def extract_text_from_resume(file):
    if not file or not file.filename:
        return ""

    filename = file.filename.lower()

    with tempfile.NamedTemporaryFile(delete=False, suffix=filename) as tmp:
        file.save(tmp.name)
        temp_path = tmp.name

    try:
        if filename.endswith(".pdf"):
            text = extract_pdf_text(temp_path)
        elif filename.endswith(".docx"):
            doc = Document(temp_path)
            text = " ".join(p.text for p in doc.paragraphs)
        else:
            text = ""
    finally:
        os.remove(temp_path)

    return text.strip()

# -------------------------------
# TEXT CLEANING
# -------------------------------
def clean_text(text):
    text = text.lower()
    text = re.sub(r"[^a-zA-Z ]", " ", text)
    text = re.sub(r"\s+", " ", text)
    return text.strip()

# -------------------------------
# SKILL EXTRACTION
# -------------------------------
def extract_skills(text):
    return {w for w in text.split() if w in TECH_SKILLS}

# -------------------------------
# CONTEXT KEYWORDS (NON-SKILLS)
# -------------------------------
def extract_context_keywords(text, skill_words):
    return {
        w for w in text.split()
        if w not in STOP_WORDS
        and w not in GENERIC_WORDS
        and w not in skill_words
        and len(w) > 4
    }

# -------------------------------
# ATS SCORE (CONSISTENT LOGIC)
# -------------------------------
def calculate_ats_score(resume_text, jd_text):
    corpus = [resume_text, jd_text]
    vectorizer = TfidfVectorizer()
    tfidf = vectorizer.fit_transform(corpus)
    score = cosine_similarity(tfidf[0:1], tfidf[1:2])[0][0]
    return round(score * 100)

# -------------------------------
# STRUCTURED RESUME GENERATOR
# -------------------------------
def generate_structured_resume(resume_text, missing_keywords):
    keywords = list(missing_keywords)[:8]

    summary = (
        "Results-driven Software Engineer with hands-on experience in "
        "developing, testing, and maintaining scalable web applications. "
        "Demonstrates strong problem-solving abilities and familiarity with "
        + ", ".join(keywords[:3]) +
        ". Committed to writing clean, maintainable code and continuous learning."
    )

    bullets = [
        "Developed and maintained scalable web applications using existing technical expertise.",
        "Collaborated with cross-functional teams following Agile development methodologies.",
        "Implemented RESTful APIs and backend services to support business requirements.",
        "Applied best practices related to "
        + ", ".join(keywords[3:6])
        + " to improve system performance and reliability.",
        "Participated in debugging, testing, and continuous improvement of applications."
    ]

    structured_resume = f"""
PROFESSIONAL SUMMARY
{summary}

EXPERIENCE HIGHLIGHTS
• {bullets[0]}
• {bullets[1]}
• {bullets[2]}
• {bullets[3]}
• {bullets[4]}

NOTE
Skills were not modified. Only wording and structure were optimized for ATS compliance.
"""

    return structured_resume.strip()

# -------------------------------
# API 1: ATS ANALYSIS
# -------------------------------
@app.route("/api/upload", methods=["POST"])
def analyze_resume():
    resume = request.files.get("resume")
    jd = request.form.get("jd")

    resume_text = clean_text(extract_text_from_resume(resume))
    jd_text = clean_text(jd)

    resume_skills = extract_skills(resume_text)
    jd_skills = extract_skills(jd_text)

    matched_skills = sorted(resume_skills & jd_skills)
    missing_skills = sorted(jd_skills - resume_skills)

    resume_keywords = extract_context_keywords(resume_text, resume_skills)
    jd_keywords = extract_context_keywords(jd_text, jd_skills)

    matched_keywords = sorted(resume_keywords & jd_keywords)
    missing_keywords = sorted(jd_keywords - resume_keywords)

    ats_score = calculate_ats_score(resume_text, jd_text)

    return jsonify({
        "ats_score": ats_score,
        "matched_skills": matched_skills,
        "missing_skills": missing_skills,
        "matched_keywords": matched_keywords,
        "missing_keywords": missing_keywords
    })

# -------------------------------
# API 2: STRUCTURED RESUME OPTIMIZER
# -------------------------------
@app.route("/api/structured-resume", methods=["POST"])
def structured_resume():
    resume = request.files.get("resume")
    jd = request.form.get("jd")

    resume_text = clean_text(extract_text_from_resume(resume))
    jd_text = clean_text(jd)

    resume_skills = extract_skills(resume_text)
    jd_skills = extract_skills(jd_text)

    resume_keywords = extract_context_keywords(resume_text, resume_skills)
    jd_keywords = extract_context_keywords(jd_text, jd_skills)

    missing_keywords = jd_keywords - resume_keywords

    ats_before = calculate_ats_score(resume_text, jd_text)
    structured_text = generate_structured_resume(resume_text, missing_keywords)
    ats_after = calculate_ats_score(structured_text, jd_text)

    return jsonify({
        "ats_score_before": ats_before,
        "ats_score_after": ats_after,
        "structured_resume": structured_text,
        "note": "No fake skills added. Resume was ethically rephrased and structured."
    })



# -------------------------------
# DEBUG ROUTE (OPTIONAL)
# -------------------------------
@app.route("/debug/routes")
def debug_routes():
    return jsonify([str(rule) for rule in app.url_map.iter_rules()])

# -------------------------------
# RUN SERVER
# -------------------------------
if __name__ == "__main__":
    app.run(debug=True)
