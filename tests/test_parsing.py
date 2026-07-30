from app.parsing.document import load_text
from app.parsing.extractor import extract_profile


def test_txt_loads():
    assert load_text(".txt", b"hello world") == "hello world"


def test_extract_finds_skills_and_role():
    text = (
        "Senior Backend Engineer\nPython, Django, PostgreSQL, Docker, Kubernetes\n"
        "8 years of experience\nAustin, TX"
    )
    profile = extract_profile(text)
    assert "Python" in profile.skills
    assert "Django" in profile.skills
    assert profile.years_experience == 8
    assert profile.target_role is not None
