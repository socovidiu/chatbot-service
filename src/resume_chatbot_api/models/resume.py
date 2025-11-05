class Resume:
    def __init__(self, name, contact_info, education, experience, skills):
        self.name = name
        self.contact_info = contact_info
        self.education = education
        self.experience = experience
        self.skills = skills

    def add_experience(
        self, job_title, company, start_date, end_date, responsibilities
    ):
        self.experience.append(
            {
                "job_title": job_title,
                "company": company,
                "start_date": start_date,
                "end_date": end_date,
                "responsibilities": responsibilities,
            }
        )

    def add_education(self, degree, institution, graduation_year):
        self.education.append(
            {
                "degree": degree,
                "institution": institution,
                "graduation_year": graduation_year,
            }
        )

    def add_skill(self, skill):
        if skill not in self.skills:
            self.skills.append(skill)

    def to_dict(self):
        return {
            "name": self.name,
            "contact_info": self.contact_info,
            "education": self.education,
            "experience": self.experience,
            "skills": self.skills,
        }
