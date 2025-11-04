from resume_chatbot_api.services import prompt_builders as pb

def test_analyze_profile_builder():
    system, user, schema = pb.analyze_profile({"name": "Ada"})
    assert "structuring assistant" in system
    assert '"name"' in user
    assert schema

def test_tailor_bullets_builder():
    system, user, schema = pb.tailor_bullets({"skills": ["Python"]}, "Build APIs", "impactful")
    assert "impact-focused" in system
    assert "Build APIs" in user
    assert "Tone: impactful" in user
    assert "bullets/removed/focus" in schema
