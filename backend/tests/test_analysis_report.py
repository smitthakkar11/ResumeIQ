"""Phase 6: section detection and rule-based recommendations."""

from app.services.analysis.recommendations import build_recommendations
from app.services.analysis.sections import detect_sections

RESUME = """SMIT THAKKAR
smit@example.com | +91 98765 43210 | github.com/smitthakkar11

PROFESSIONAL SUMMARY
Final-year computer science student.

TECHNICAL SKILLS
Python, React, MySQL

WORK EXPERIENCE
Software Engineering Intern, 2025

PROJECTS
ResumeIQ - a resume analyser

EDUCATION
B.Tech Computer Science, 2026

CERTIFICATIONS
AWS Cloud Practitioner
"""


def categories(tips) -> set[str]:
    return {t.category for t in tips}


def messages(tips) -> str:
    return " ".join(t.message for t in tips)


class TestSectionDetection:
    def test_detects_every_section_in_a_conventional_resume(self) -> None:
        found = detect_sections(RESUME)
        for section in ("Contact", "Summary", "Education", "Experience", "Projects",
                        "Skills", "Certifications"):
            assert found[section] is True, section

    def test_reports_absent_sections_as_false(self) -> None:
        found = detect_sections("EDUCATION\nB.Tech Computer Science")
        assert found["Education"] is True
        assert found["Experience"] is False
        assert found["Projects"] is False

    def test_contact_is_detected_from_an_email_without_a_heading(self) -> None:
        assert detect_sections("Smit Thakkar\nsmit@example.com")["Contact"] is True

    def test_contact_is_detected_from_a_github_url(self) -> None:
        assert detect_sections("github.com/smitthakkar11")["Contact"] is True

    def test_contact_is_detected_from_a_phone_number(self) -> None:
        assert detect_sections("Smit Thakkar\n+91 98765 43210")["Contact"] is True

    def test_no_contact_details_means_not_detected(self) -> None:
        assert detect_sections("EDUCATION\nB.Tech")["Contact"] is False

    def test_heading_matching_is_case_insensitive(self) -> None:
        assert detect_sections("education\nB.Tech")["Education"] is True
        assert detect_sections("EDUCATION\nB.Tech")["Education"] is True

    def test_a_long_line_is_not_treated_as_a_heading(self) -> None:
        """Prose mentioning a word must not be mistaken for a section heading."""
        prose = (
            "During my education I completed a wide range of coursework covering "
            "algorithms, databases and distributed systems across several years."
        )
        assert detect_sections(prose)["Education"] is False

    def test_returns_sections_in_a_stable_order(self) -> None:
        assert list(detect_sections(RESUME)) == list(detect_sections("anything"))


class TestRecommendations:
    def _build(self, **overrides):
        defaults = dict(
            resume_text=RESUME,
            missing_skills=[],
            matched_skills=["Python"],
            keywords=[("python", True)],
            sections=detect_sections(RESUME),
            text_similarity=80.0,
            keyword_match=80.0,
        )
        return build_recommendations(**{**defaults, **overrides})

    def test_names_the_missing_skills(self) -> None:
        tips = self._build(missing_skills=["Docker", "Kubernetes"])
        assert "Docker" in messages(tips) and "Kubernetes" in messages(tips)
        assert "skills" in categories(tips)

    def test_truncates_a_long_missing_skill_list(self) -> None:
        tips = self._build(missing_skills=[f"Skill{i}" for i in range(9)])
        assert "and 4 more" in messages(tips)

    def test_says_so_when_nothing_is_missing(self) -> None:
        assert "positive" in categories(self._build(missing_skills=[]))

    def test_flags_low_keyword_match_with_the_actual_terms(self) -> None:
        tips = self._build(keyword_match=20.0, keywords=[("docker", False), ("aws", False)])
        assert "docker" in messages(tips)

    def test_stays_quiet_about_keywords_when_the_match_is_good(self) -> None:
        tips = self._build(keyword_match=90.0, keywords=[("docker", False)])
        assert "keywords" not in categories(tips)

    def test_flags_a_missing_expected_section_gently(self) -> None:
        sections = {**detect_sections(RESUME), "Skills": False}
        tips = self._build(sections=sections)
        assert "was not detected" in messages(tips)
        # Spec: never assert the resume is bad, only that we could not find it.
        assert "missing" not in messages(tips).lower()

    def test_stays_quiet_about_optional_sections(self) -> None:
        sections = {**detect_sections(RESUME), "Certifications": False, "Achievements": False}
        tips = self._build(sections=sections)
        assert "Certifications" not in messages(tips)

    def test_suggests_quantifying_when_no_numbers_are_present(self) -> None:
        tips = self._build(resume_text="Built things. Led a team. Wrote code.")
        assert "Measurable results" in messages(tips)

    def test_stays_quiet_when_numbers_are_present(self) -> None:
        tips = self._build(resume_text="Reduced load time by 40% for 5000 users. " * 40)
        assert "Measurable results" not in messages(tips)

    def test_flags_weak_phrasing(self) -> None:
        tips = self._build(resume_text="Responsible for maintaining the build system.")
        assert "action verb" in messages(tips)

    def test_flags_a_very_short_resume(self) -> None:
        assert "short" in messages(self._build(resume_text="Smit. Python."))

    def test_flags_a_very_long_resume(self) -> None:
        assert "long" in messages(self._build(resume_text="word " * 1200))

    def test_is_deterministic(self) -> None:
        """Same input, same advice — the reason this is rules and not an LLM."""
        assert [t.message for t in self._build()] == [t.message for t in self._build()]

    def test_a_perfect_resume_gets_no_criticism(self) -> None:
        text = (
            RESUME
            + "\nReduced page load time by 40% for 5000 monthly users. " * 20
        )
        tips = self._build(resume_text=text, missing_skills=[])
        assert categories(tips) <= {"positive"}
