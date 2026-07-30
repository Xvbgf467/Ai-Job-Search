from app.matching.taxonomy import is_tech_text


def test_tech_filter_keeps_tech():
    assert is_tech_text("Senior Software Engineer — React, Node.js")


def test_tech_filter_drops_non_tech():
    assert not is_tech_text("Experienced barista needed for busy cafe")


def test_keyword_score_basic():
    from app.db.models import Resume
    from app.matching.keywords import skill_overlap

    resume = Resume(name="x", raw_text="", skills="Python,Django")
    job = "We need a Python and Django backend engineer."
    assert skill_overlap(resume, job) == 1.0
