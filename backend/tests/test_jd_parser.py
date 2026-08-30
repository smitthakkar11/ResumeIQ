"""Phase A: job-description parsing and partial skill matching."""

import pytest

from app.core.config import settings
from app.services.matching.engine import analyse
from app.services.nlp.jd_parser import parse_job_description
from app.services.nlp.skill_extractor import all_skills

STRUCTURED_JD = """Senior Backend Engineer

About us
We build payments infrastructure.

Requirements
- 3+ years of professional experience with Python
- Strong SQL and MySQL knowledge
- Bachelor's degree in Computer Science
- Excellent communication and a collaborative mindset

Preferred qualifications
- Experience with Docker and Kubernetes
- Familiarity with AWS
"""

PROSE_JD = (
    "Software Engineer Intern. Looking for someone with Python, React and MySQL. "
    "Docker is a plus. You will build REST APIs in an Agile team."
)


def names(skills):
    return sorted(s.name for s in skills)


class TestRoleExtraction:
    def test_reads_an_explicit_job_title_line(self) -> None:
        assert parse_job_description("Job Title: Data Analyst\n...").role == "Data Analyst"

    def test_falls_back_to_a_short_leading_line_naming_a_role(self) -> None:
        assert parse_job_description(STRUCTURED_JD).role == "Senior Backend Engineer"

    def test_returns_empty_rather_than_guessing(self) -> None:
        parsed = parse_job_description("We need someone great to join the team and help out.")
        assert parsed.role == ""
        assert parsed.confidence["role"] is False


class TestRequiredVersusPreferred:
    def test_splits_on_a_preferred_heading(self) -> None:
        parsed = parse_job_description(STRUCTURED_JD)
        assert "Python" in names(parsed.required_skills)
        assert "MySQL" in names(parsed.required_skills)
        assert {"Docker", "Kubernetes", "AWS"} <= set(names(parsed.preferred_skills))

    def test_an_inline_plus_marks_only_that_sentence(self) -> None:
        """A one-paragraph posting must not send every skill to 'preferred'."""
        parsed = parse_job_description(PROSE_JD)
        assert {"Python", "React", "MySQL"} <= set(names(parsed.required_skills))
        assert names(parsed.preferred_skills) == ["Docker"]

    def test_a_heading_line_that_also_carries_content_keeps_the_content(self) -> None:
        parsed = parse_job_description("Required: Python, React, Docker")
        assert names(parsed.required_skills) == ["Docker", "Python", "React"]

    def test_a_skill_in_both_buckets_counts_as_required(self) -> None:
        parsed = parse_job_description("Requirements\nPython\nPreferred\nPython and Docker")
        assert "Python" in names(parsed.required_skills)
        assert "Python" not in names(parsed.preferred_skills)


class TestSoftSkillsEducationExperience:
    def test_detects_soft_skills(self) -> None:
        assert {"Communication", "Teamwork"} <= set(parse_job_description(STRUCTURED_JD).soft_skills)

    def test_detects_the_degree_required(self) -> None:
        assert parse_job_description(STRUCTURED_JD).education == "Bachelor's"

    @pytest.mark.parametrize(
        "text,expected",
        [
            ("Master's degree preferred", "Master's"),
            ("PhD in machine learning", "PhD"),
            ("B.Tech in any discipline", "Bachelor's"),
            ("No formal requirements", ""),
        ],
    )
    def test_degree_variants(self, text: str, expected: str) -> None:
        assert parse_job_description(text).education == expected

    def test_reads_years_of_experience(self) -> None:
        parsed = parse_job_description(STRUCTURED_JD)
        assert parsed.experience == "3+ years"
        assert parsed.min_years == 3

    @pytest.mark.parametrize(
        "text,expected",
        [
            ("Summer internship programme", "Internship"),
            ("Entry level position for new grads", "Entry level"),
            ("Senior staff engineer role", "Senior"),
        ],
    )
    def test_experience_level_variants(self, text: str, expected: str) -> None:
        assert parse_job_description(text).experience == expected

    def test_confidence_reports_what_was_actually_found(self) -> None:
        parsed = parse_job_description("We are hiring.")
        assert parsed.confidence == {
            "role": False, "education": False, "experience": False, "skills": False
        }


class TestCapabilityTags:
    def test_related_skills_share_a_tag(self) -> None:
        by_name = {s.name: s for s in all_skills()}
        assert by_name["Docker"].is_related_to(by_name["Kubernetes"])
        assert by_name["FastAPI"].is_related_to(by_name["Django"])
        assert not by_name["Docker"].is_related_to(by_name["React"])

    def test_an_untagged_skill_is_related_to_nothing(self) -> None:
        by_name = {s.name: s for s in all_skills()}
        assert not by_name["Rust"].is_related_to(by_name["Python"])


class TestPartialMatching:
    def test_related_experience_becomes_a_partial_match(self) -> None:
        result = analyse(
            "Deployed services with Kubernetes.",
            "Requirements: Docker experience needed for our platform team.",
        )
        assert [p.skill.name for p in result.partial_skills] == ["Docker"]
        assert [e.name for e in result.partial_skills[0].evidence] == ["Kubernetes"]
        assert result.partial_skills[0].shared_tags == ["devops"]
        assert result.missing_skills == []

    def test_unrelated_gaps_stay_missing(self) -> None:
        result = analyse(
            "I write Python and React.",
            "Requirements: Python, React and Tableau are needed.",
        )
        assert [s.name for s in result.missing_skills] == ["Tableau"]
        assert result.partial_skills == []

    def test_partial_matches_earn_partial_credit(self) -> None:
        """One exact match and one partial out of two requirements."""
        result = analyse(
            "Python developer who has used Kubernetes.",
            "Requirements: Python and Docker.",
        )
        expected = (1 + settings.PARTIAL_SKILL_CREDIT) / 2 * 100
        assert result.skill_match == pytest.approx(expected)

    def test_partial_credit_is_less_than_a_real_match(self) -> None:
        partial = analyse("Used Kubernetes.", "Requirements: Docker.")
        exact = analyse("Used Docker.", "Requirements: Docker.")
        assert partial.skill_match < exact.skill_match

    def test_preferred_skills_do_not_affect_the_score(self) -> None:
        """A nice-to-have must never drag the score down."""
        without = analyse("I know Python.", "Requirements: Python.")
        with_pref = analyse("I know Python.", "Requirements: Python.\nPreferred: Tableau, Hadoop.")
        assert with_pref.skill_match == without.skill_match
        assert "Tableau" not in {s.name for s in with_pref.missing_skills}


class TestRequirementsOnResult:
    def test_analysis_carries_the_parsed_requirements(self) -> None:
        result = analyse("Python developer.", STRUCTURED_JD)
        assert result.requirements is not None
        assert result.requirements.role == "Senior Backend Engineer"
        assert result.requirements.education == "Bachelor's"
        assert result.requirements.min_years == 3
