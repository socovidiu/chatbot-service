def test_resume_analyze(client, monkeypatch):
    from resume_chatbot_api.api import resume as resume_api
    async def mock_analyze(profile):
        return {"name": "Ada", "title": "Engineer", "summary": None, "skills": [], "experience": [], "education": []}
    monkeypatch.setattr(resume_api.llm, "analyze_profile", mock_analyze)

    r = client.post("/resume/analyze", json={"profile": {"name": "Ada"}})
    assert r.status_code == 200
    data = r.json()
    assert data["canonical"]["name"] == "Ada"

def test_resume_keywords(client, monkeypatch):
    from resume_chatbot_api.api import resume as resume_api
    async def mock_keywords(jd):
        return {"skills": ["Python"], "keywords": ["REST"], "seniority": "mid", "nice_to_have": []}
    monkeypatch.setattr(resume_api.llm, "extract_keywords", mock_keywords)

    r = client.post("/resume/keywords", json={"job_description": "Build APIs in Python"})
    assert r.status_code == 200
    data = r.json()
    assert "Python" in data["skills"]

def test_resume_tailor(client, monkeypatch):
    from resume_chatbot_api.api import resume as resume_api
    async def mock_tailor(profile, jd, tone="concise"):
        return {"bullets": ["Improved p95 latency by 38%"], "removed": [], "focus": ["API", "Python"]}
    monkeypatch.setattr(resume_api.llm, "tailor_bullets", mock_tailor)

    body = {"profile": {"skills": ["Python"]}, "job_description": "APIs", "tone": "impactful"}
    r = client.post("/resume/tailor", json=body)
    assert r.status_code == 200
    data = r.json()
    assert data["bullets"]
    assert "Python" in data["focus"]

def test_resume_summary(client, monkeypatch):
    from resume_chatbot_api.api import resume as resume_api
    async def mock_summary(profile, jd):
        return {"summary": "Backend engineer with 5+ years in APIs."}
    monkeypatch.setattr(resume_api.llm, "write_summary", mock_summary)

    r = client.post("/resume/summary", json={"profile": {"skills": ["Go"]}, "job_description": "Backend role"})
    assert r.status_code == 200
    assert "summary" in r.json()

def test_resume_cover_letter(client, monkeypatch):
    from resume_chatbot_api.api import resume as resume_api
    async def mock_cl(profile, jd, company, role):
        return {"cover_letter": "Dear Hiring Manager, ..."}
    monkeypatch.setattr(resume_api.llm, "write_cover_letter", mock_cl)

    r = client.post("/resume/cover-letter", json={
        "profile": {"skills": ["Go"]},
        "job_description": "Backend role",
        "company": "Acme",
        "role": "Backend Engineer"
    })
    assert r.status_code == 200
    assert "cover_letter" in r.json()

def test_resume_ats_score(client, monkeypatch):
    from resume_chatbot_api.api import resume as resume_api
    async def mock_ats(resume_text, jd):
        return {
            "score": 82, "gaps": [], "recommendations": ["Quantify outcomes"],
            "keyword_match": {"present": ["Python"], "missing": ["Kubernetes"]}
        }
    monkeypatch.setattr(resume_api.llm, "ats_score", mock_ats)

    r = client.post("/resume/ats-score", json={"resume_text": "Python dev", "job_description": "Cloud APIs"})
    assert r.status_code == 200
    data = r.json()
    assert isinstance(data["score"], int)
    assert "keyword_match" in data
