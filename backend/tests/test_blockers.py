"""Phase C: experience/education matching and ranked blockers."""

import pytest

from app.services.matching.credentials import (
    estimate_experience,
    highest_degree,
    match_education,
    match_experience,
)
from app.services.matching.engine import analyse

RESUME = """SMIT THAKKAR
smit@example.com | github.com/smitt

EDUCATION
B.Tech Computer Science, 2022 - 2026

EXPERIENCE
Software Intern, Jan 2024 - Jun 2024
Backend Developer, Jul 2024 - Jun 2025

SKILLS
Python, MySQL, FastAPI
"""

DEMANDING_JOB = """Backend Engineer
Requirements
- 5+ years building services with Python and Docker
- Strong MySQL and REST API design
- Kubernetes for orchestration
- Master's degree in Computer Science
"""


class TestExperienceEstimation:
    def test_counts_months_not_whole_years(self) -> None:
        """A six-month internship is not zero experience."""
        estimate = estimate_experience("EXPERIENCE\nIntern, Jan 2024 - Jun 2024")
        assert 0.3 <= estimate.years <= 0.6

    def test_counts_overlapping_roles_once(self) -> None:
        overlapping = estimate_experience(
            "EXPERIENCE\nA, Jan 2023 - Dec 2024\nB, Jun 2023 - Dec 2024"
        )
        assert overlapping.years == pytest.approx(2.0, abs=0.2)

    def test_ignores_education_dates(self) -> None:
        """A 2022-2026 degree is not four years of work."""
        estimate = estimate_experience("EDUCATION\nB.Tech, 2022 - 2026\nSKILLS\nPython")
        assert estimate.years == 0.0
        assert estimate.confident is False

    def test_prefers_an_explicit_claim(self) -> None:
        estimate = estimate_experience("5+ years of professional experience")
        assert estimate.years == 5.0
        assert "stated" in estimate.source

    def test_reports_when_it_could_not_tell(self) -> None:
        assert estimate_experience("SKILLS\nPython").confident is False


class TestCredentialMatching:
    def test_no_requirement_means_no_score(self) -> None:
        """Not measurable is not the same as failed."""
        assert match_experience(RESUME, None).score is None
        assert match_education(RESUME, "").score is None

    def test_entry_level_is_always_satisfied(self) -> None:
        assert match_experience(RESUME, 0).score == 100.0

    def test_meeting_the_requirement_scores_full(self) -> None:
        assert match_experience("8 years of experience", 3).score == 100.0

    def test_falling_short_scores_proportionally(self) -> None:
        score = match_experience("2 years of experience", 4).score
        assert score == pytest.approx(50.0)

    @pytest.mark.parametrize(
        "required,expected", [("Bachelor's", 100.0), ("Master's", 50.0), ("PhD", 0.0)]
    )
    def test_degree_levels(self, required: str, expected: float) -> None:
        assert match_education(RESUME, required).score == expected

    def test_detects_the_highest_degree_held(self) -> None:
        assert highest_degree("B.Tech and later an M.Tech in AI") == "Master's"
        assert highest_degree("No schooling mentioned") == ""

    def test_every_result_explains_itself(self) -> None:
        assert match_experience(RESUME, 5).detail
        assert match_education(RESUME, "PhD").detail


class TestScoreComponents:
    def test_credentials_join_the_score_when_stated(self) -> None:
        result = analyse(RESUME, DEMANDING_JOB)
        assert result.experience_match is not None
        assert result.education_match is not None
        assert "experience_match" in result.weights
        assert "education_match" in result.weights

    def test_credentials_are_dropped_when_not_stated(self) -> None:
        result = analyse(RESUME, "We need someone to write Python and use MySQL daily.")
        assert result.experience_match is None
        assert "experience_match" not in result.weights
        assert sum(result.weights.values()) == pytest.approx(1.0, abs=0.005)


class TestBlockers:
    def test_are_ranked_by_what_they_cost(self) -> None:
        blockers = analyse(RESUME, DEMANDING_JOB).blockers
        assert blockers
        costs = [b.cost for b in blockers]
        assert costs == sorted(costs, reverse=True)

    def test_each_one_says_why_and_what_to_do(self) -> None:
        for b in analyse(RESUME, DEMANDING_JOB).blockers:
            assert b.detail and b.fix and b.title
            assert b.cost > 0

    def test_names_the_specific_missing_skills(self) -> None:
        titles = " ".join(b.title for b in analyse(RESUME, DEMANDING_JOB).blockers)
        assert "Docker" in titles or "Kubernetes" in titles

    def test_a_partial_match_costs_less_than_a_full_gap(self) -> None:
        """Related evidence earns partial credit, so it holds you back less."""
        partial = analyse("Used Kubernetes daily.", "Requirements: Docker and Python.")
        missing = analyse("Used Tableau daily.", "Requirements: Docker and Python.")

        partial_cost = next(b.cost for b in partial.blockers if "Docker" in b.title)
        missing_cost = next(b.cost for b in missing.blockers if "Docker" in b.title)
        assert partial_cost < missing_cost

    def test_a_strong_match_has_few_blockers(self) -> None:
        strong = analyse(
            RESUME + "\nBuilt REST APIs with Docker and Kubernetes on AWS.",
            "Requirements: Python and MySQL.",
        )
        assert len(strong.blockers) < len(analyse(RESUME, DEMANDING_JOB).blockers)

    def test_never_suggests_claiming_a_skill_you_lack(self) -> None:
        """Spec: do not encourage users to falsely add skills."""
        for b in analyse(RESUME, DEMANDING_JOB).blockers:
            text = f"{b.detail} {b.fix}".lower()
            assert "if you have" in text or "where these describe" in text or b.category in (
                "wording", "experience", "education"
            ), b.fix

    def test_is_deterministic(self) -> None:
        first = [(b.title, b.cost) for b in analyse(RESUME, DEMANDING_JOB).blockers]
        second = [(b.title, b.cost) for b in analyse(RESUME, DEMANDING_JOB).blockers]
        assert first == second
