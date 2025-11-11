from resume_chatbot_api.services import prompts as pb

def test_build_analyze_user_basic():
    # Ensure the builder emits JSON from the request and useful guidance.
    class DummyReq:
        def __init__(self, payload):
            self._payload = payload
        def model_dump_json(self):
            return '{"resumedata":{"name":"Ada"}}'
    req = DummyReq({"resumedata": {"name": "Ada"}})

    msg = pb.build_analyze_user(req)
    assert "Analyze the following canonical profile" in msg
    assert '"resumedata"' in msg
    assert '"name"' in msg


def test_build_tailor_user_with_tone():
    class DummyReq:
        def __init__(self, profile, jd, tone):
            self.profile = profile
            self.job_description = jd
            self.tone = tone
    class Profile:
        def __init__(self, name="Ada"):
            self.name = name
        def model_dump_json(self):
            return '{"name":"Ada","skills":["Python"]}'

    req = DummyReq(Profile(), "Build APIs in Python", "impactful")
    msg = pb.build_tailor_user(req)
    assert "Tailor resume bullets" in msg
    assert "Tone: impactful" in msg
    assert "Build APIs in Python" in msg
    assert '"skills"' in msg


def test_build_tailor_user_empty_tone_defaults_to_concise():
    class DummyReq:
        def __init__(self, profile, jd, tone):
            self.profile = profile
            self.job_description = jd
            self.tone = tone
    class Profile:
        def model_dump_json(self):
            return '{"name":"Ada"}'

    req = DummyReq(Profile(), "Improve teamwork", "")
    msg = pb.build_tailor_user(req)
    # Empty tone should fall back to "concise" per implementation.
    assert "Tone: concise" in msg
    assert "Improve teamwork" in msg


def test_build_summary_user_includes_optional_jd():
    class DummyReq:
        def __init__(self, profile, jd=None):
            self.profile = profile
            self.job_description = jd
    class Profile:
        def model_dump_json(self):
            return '{"name":"Ada"}'

    req = DummyReq(Profile(), "Backend role")
    msg = pb.build_summary_user(req)
    assert "Write a concise 2–3 line professional summary" in msg
    assert '"name"' in msg
    assert "Backend role" in msg


def test_build_cover_letter_user_limits():
    class DummyReq:
        def __init__(self, profile, jd, company=None, role=None):
            self.profile = profile
            self.job_description = jd
            self.company = company
            self.role = role
    class Profile:
        def model_dump_json(self):
            return '{"name":"Ada"}'

    req = DummyReq(Profile(), "Backend JD text", "Acme", "Backend Engineer")
    msg = pb.build_cover_letter_user(req)
    assert "≤180 words" in msg
    assert "Company: Acme" in msg
    assert "Role: Backend Engineer" in msg


def test_build_ats_user_accepts_text_or_canonical():
    # canonical path
    class Canonical:
        def model_dump_json(self):
            return '{"name":"Ada","skills":["Python"]}'
    class Req1:
        def __init__(self):
            self.canonical = Canonical()
            self.resume_text = None
            self.job_description = "Cloud APIs"
    msg1 = pb.build_ats_user(Req1())
    assert "Canonical Profile (JSON)" in msg1
    assert "Cloud APIs" in msg1

    # resume_text path
    class Req2:
        canonical = None
        resume_text = "Python dev"
        job_description = "Cloud APIs"
    msg2 = pb.build_ats_user(Req2())
    assert "Resume Text" in msg2
    assert "Python dev" in msg2