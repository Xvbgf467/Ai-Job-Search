"""Sourcing tests use respx to mock httpx so no real network calls happen."""
import httpx
import pytest
import respx

from app.sourcing import remotive


@respx.mock
def test_remotive_normalizes_and_filters():
    respx.get("https://remotive.com/api/remote-jobs").respond(
        json={
            "jobs": [
                {
                    "id": 1,
                    "title": "Senior Software Engineer",
                    "category": "Software Development",
                    "company_name": "Acme",
                    "candidate_required_location": "USA",
                    "url": "https://example.com/1",
                    "description": "Python Django backend",
                },
                {
                    "id": 2,
                    "title": "Marketing Manager",
                    "category": "Marketing",
                    "description": "social media campaigns",
                },
            ]
        }
    )

    jobs = remotive.fetch_tech_jobs()
    assert len(jobs) == 1
    assert jobs[0]["source"] == "remotive"
    assert jobs[0]["title"] == "Senior Software Engineer"
