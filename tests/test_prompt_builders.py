from resume_chatbot_api.services import prompts as pb

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

def test_analyze_profile_builder_types():
    system, user, schema = pb.analyze_profile({"name": "Ada"})
    assert isinstance(system, str)
    assert isinstance(user, str)
    assert isinstance(schema, dict)

def test_analyze_profile_builder_empty_profile():
    system, user, schema = pb.analyze_profile({})
    assert "structuring" in system.lower()
    assert "profile" in user.lower()
    assert isinstance(schema, dict)

def test_tailor_bullets_builder_empty_skills():
    system, user, schema = pb.tailor_bullets({}, "Improve teamwork", "")
    assert "teamwork" in user
    assert "tone" not in user.lower()  # no tone injected if empty


