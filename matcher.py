import json

def load_skills(path="skills.json"):
    with open(path, "r") as f:
        data = json.load(f)
    return [skill.lower() for skill in data["skills"]]

def extract_skills(text, skills_list):
    text = text.lower()
    found_skills = set()

    for skill in skills_list:
        if skill in text:
            found_skills.add(skill)

    return found_skills
def match_skills(resume_skills, jd_skills):
    matched = resume_skills.intersection(jd_skills)
    missing = jd_skills - resume_skills
    return matched, missing

def calculate_ats_score(matched, jd_skills):
    if len(jd_skills) == 0:
        return 0
    return round((len(matched) / len(jd_skills)) * 100, 2)
def generate_suggestions(missing_skills):
    suggestions = []
    for skill in missing_skills:
        suggestions.append(f"Consider adding projects or experience related to {skill}")
    return suggestions
