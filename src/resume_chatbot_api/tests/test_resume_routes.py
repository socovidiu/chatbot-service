import pytest
from fastapi.testclient import TestClient
from resume_chatbot_api.app import app
from resume_chatbot_api.api import resume as resume_api

@pytest.fixture(scope="session")
def client():
    return TestClient(app)


# ---------- Helpers to monkeypatch chain.ainvoke ----------

class _DummyChain:
    def __init__(self, payload):
        self._payload = payload
    async def ainvoke(self, *_args, **_kwargs):
        return self._payload


# def test_resume_analyze(client, monkeypatch):
#     # Provide a fully valid AnalyzeResponse payload (meets all validators).
#     payload = {
#         "quality": 75,
#         "strengths": ["Quantified impact", "Strong backend focus"],
#         "gaps": ["Missing Kubernetes", "Sparse achievements in last role"],
#         "risks": [],
#         "recommendations": ["Quantify outcomes", "Add relevant metrics", "Highlight cloud work"],
#         "section_scores": {"summary": 4, "experience": 4, "education": 3, "skills": 4},
#         "keyword_clusters": {"core": ["APIs"], "tools": ["Python", "Postgres"], "soft": ["Collaboration"]},
#         "anomalies": []
#     }
#     monkeypatch.setattr(resume_api, "analyze_chain", _DummyChain(payload))

#     body = {"resumedata": {
#         "name": "Ada",
#         "skills": ["Python"],
#         "experience": [],
#         "education": []
#     }}
#     r = client.post("/resume/analyze", json=body)
#     assert r.status_code == 200
#     data = r.json()
#     assert data["quality"] == 75
#     assert len(data["recommendations"]) >= 3
#     assert set(data["keyword_clusters"].keys()) == {"core", "tools", "soft"}


def test_resume_keywords(client, monkeypatch):
    payload = {
        "skills": ["Python", "REST"],
        "keywords": ["API design", "Latency"],
        "seniority": "mid",
        "nice_to_have": ["Kubernetes"]
    }
    monkeypatch.setattr(resume_api, "keywords_chain", _DummyChain(payload))

    r = client.post("/resume/keywords", json={"job_description": "Build Python REST APIs"})
    assert r.status_code == 200
    data = r.json()
    assert "Python" in data["skills"]
    assert "API design" in data["keywords"]


def test_resume_tailor(client, monkeypatch):
    payload = {
        "bullets": [
            "Improved p95 latency by 38% for critical API endpoints",
            "Cut infra costs by 22% via query optimization",
            "Shipped auth rate limiting to reduce abuse by 70%",
            "Automated CI checks, reducing PR cycle time 35%"
        ],
        "removed": ["Outdated tech stack details", "Irrelevant course projects"],
        "focus": ["APIs", "Python", "Scalability"]
    }
    monkeypatch.setattr(resume_api, "tailor_chain", _DummyChain(payload))

    body = {
        "profile": {"name": "Ada", "skills": ["Python"], "experience": [], "education": []},
        "job_description": "APIs",
        "tone": "impactful"
    }
    r = client.post("/resume/tailor", json=body)
    assert r.status_code == 200
    data = r.json()
    assert 4 <= len(data["bullets"]) <= 6
    assert 2 <= len(data["removed"]) <= 4
    assert 3 <= len(data["focus"]) <= 5


def test_resume_summary(client, monkeypatch):
    payload = {"summary": "Backend engineer with 5+ years building APIs and improving reliability."}
    monkeypatch.setattr(resume_api, "summary_chain", _DummyChain(payload))

    body = {
        "profile": {"name": "Ada", "skills": ["Go"], "experience": [], "education": []},
        "job_description": "Backend role"
    }
    r = client.post("/resume/summary", json=body)
    assert r.status_code == 200
    text = r.json()["summary"]
    assert 0 < len(text) <= 320


def test_resume_cover_letter(client, monkeypatch):
    payload = {
        "cover_letter": (
            "Dear Hiring Manager,\n"
            "I’ve shipped reliable APIs, improved latency, and led cross-team initiatives. "
            "I’m excited about Acme’s mission and this Backend Engineer role, where I can "
            "apply my experience to deliver measurable outcomes.\n"
            "Sincerely,\nAda"
        )
    }
    monkeypatch.setattr(resume_api, "cover_chain", _DummyChain(payload))

    body = {
        "profile": {"name": "Ada", "skills": ["Go"]},
        "job_description": "Backend role",
        "company": "Acme",
        "role": "Backend Engineer"
    }
    r = client.post("/resume/cover-letter", json=body)
    assert r.status_code == 200
    assert "cover_letter" in r.json()
    assert len(r.json()["cover_letter"].split()) <= 180


def test_resume_ats_score(client, monkeypatch):
    payload = {
        "score": 82,
        "gaps": ["Missing Kubernetes"],
        "recommendations": ["Quantify outcomes", "Add cloud projects", "Highlight SLO impact"],
        "keyword_match": {"present": ["Python", "REST"], "missing": ["Kubernetes"]}
    }
    monkeypatch.setattr(resume_api, "ats_chain", _DummyChain(payload))

    r = client.post("/resume/ats-score", json={"resume_text": "Python dev", "job_description": "Cloud APIs"})
    assert r.status_code == 200
    data = r.json()
    assert isinstance(data["score"], int)
    assert "present" in data["keyword_match"] and "missing" in data["keyword_match"]
    assert len(data["recommendations"]) >= 3
