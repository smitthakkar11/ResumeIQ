"""Phase B: standalone resume quality score."""

import pytest

from app.core.config import settings
from app.services.analysis.quality_score import score_resume
from app.services.analysis.resume_features import extract_features

STRONG = """SMIT THAKKAR
smit@example.com | +91 98765 43210 | github.com/smitthakkar11 | linkedin.com/in/smitt

EDUCATION
B.Tech Computer Science, 2022 - 2026

TECHNICAL SKILLS
Python, C++, JavaScript, React, MySQL, Docker, FastAPI, Git, Linux, AWS, pandas, NumPy

PROJECTS
- Built a resume analyser using FastAPI and MySQL, cutting screening time by 40%
- Designed a REST API in Python serving 5000 monthly users
- Implemented a React dashboard adopted by 200 students

EXPERIENCE
Software Intern, Jan 2025 - Jun 2025
- Developed internal tooling in Python and deployed it with Docker
- Automated a reporting pipeline, saving 6 hours per week
""" + ("Delivered documentation and tooling improvements for the platform team. " * 12)

WEAK = """John Smith
john@example.com

SKILLS
Python, Java

EXPERIENCE
Worked on various projects
Responsible for maintaining systems
Helped with testing

I am a hard working team player passionate about technology.
"""


def component(text: str, key: str):
    return next(c for c in score_resume(text).components if c.key == key)


class TestOverall:
    def test_scores_are_percentages(self) -> None:
        for text in (STRONG, WEAK):
            score = score_resume(text)
            assert 0.0 <= score.overall <= 100.0
            assert all(0.0 <= c.score <= 100.0 for c in score.components)

    def test_a_strong_resume_clearly_outscores_a_weak_one(self) -> None:
        assert score_resume(STRONG).overall - score_resume(WEAK).overall > 40

    def test_reports_all_six_components(self) -> None:
        keys = [c.key for c in score_resume(STRONG).components]
        assert keys == ["skills", "keywords", "projects", "experience", "education", "formatting"]

    def test_weights_are_normalised(self) -> None:
        assert sum(score_resume(STRONG).weights.values()) == pytest.approx(1.0)

    def test_overall_is_the_weighted_average_of_the_components(self) -> None:
        score = score_resume(STRONG)
        expected = sum(c.score * score.weights[c.key] for c in score.components)
        assert score.overall == pytest.approx(expected, abs=0.1)

    def test_is_deterministic(self) -> None:
        assert score_resume(STRONG).overall == score_resume(STRONG).overall

    def test_empty_text_scores_zero_without_crashing(self) -> None:
        assert score_resume("").overall == pytest.approx(0.0, abs=20.0)


class TestExplainability:
    def test_every_component_reports_the_checks_it_ran(self) -> None:
        for c in score_resume(STRONG).components:
            assert c.checks, c.key
            assert all(k.detail for k in c.checks)

    def test_component_score_is_the_sum_of_its_checks(self) -> None:
        for c in score_resume(STRONG).components:
            earned = sum(k.earned for k in c.checks)
            maximum = sum(k.maximum for k in c.checks)
            assert c.score == pytest.approx(round(earned / maximum * 100, 1), abs=0.1)

    def test_no_check_can_exceed_its_maximum(self) -> None:
        for c in score_resume(STRONG).components:
            assert all(k.earned <= k.maximum for k in c.checks)


class TestComponentsMeasureWhatTheyClaim:
    def test_skills_rewards_breadth(self) -> None:
        few = component("Python and Java only.", "skills").score
        many = component(
            "Python, React, MySQL, Docker, AWS, Git, Linux, pandas, NumPy, TypeScript", "skills"
        ).score
        assert many > few

    def test_education_needs_the_section_and_a_degree(self) -> None:
        assert component("EDUCATION\nB.Tech Computer Science, 2024", "education").score > 90
        assert component("Some text with no schooling mentioned.", "education").score == 0

    def test_formatting_rewards_contact_details(self) -> None:
        bare = component("SKILLS\nPython", "formatting").score
        full = component(
            "a@b.com | +91 98765 43210 | github.com/x\nSKILLS\nPython\nEDUCATION\nB.Tech",
            "formatting",
        ).score
        assert full > bare

    def test_experience_penalises_duty_phrasing(self) -> None:
        strong = component(
            "EXPERIENCE\nIntern, Jan 2025 - Jun 2025\n"
            "- Built a service in Python\n- Designed a schema\n- Automated deploys\n"
            "- Developed an internal dashboard for the operations team",
            "experience",
        ).score
        weak = component(
            "EXPERIENCE\nIntern, Jan 2025 - Jun 2025\n"
            "- Responsible for the service\n- Worked on the schema\n- Helped with deploys\n"
            "- Involved in building an internal dashboard for operations",
            "experience",
        ).score
        assert strong > weak

    def test_keywords_rewards_skills_evidenced_in_bullets(self) -> None:
        """Listing a skill is cheap; showing where you used it is not."""
        listed = component("SKILLS\nPython, Docker, React, MySQL, AWS", "keywords").score
        evidenced = component(
            "SKILLS\nPython, Docker, React, MySQL, AWS\n"
            "PROJECTS\n- Built a Python service deployed with Docker onto AWS\n"
            "- Developed a React frontend backed by MySQL for internal reporting",
            "keywords",
        ).score
        assert evidenced > listed

    def test_projects_rewards_measurable_outcomes(self) -> None:
        plain = component("PROJECTS\n- Built a web app using React and MySQL", "projects").score
        measured = component(
            "PROJECTS\n- Built a React web app on MySQL serving 5000 users\n"
            "- Cut page load time by 40% using caching in Python\n"
            "- Reduced deploy time to 10 minutes with Docker",
            "projects",
        ).score
        assert measured > plain


class TestWeightsAreConfigurable:
    def test_changing_a_weight_changes_the_total(self, monkeypatch) -> None:
        before = score_resume(WEAK).overall
        monkeypatch.setattr(settings, "QUALITY_WEIGHT_EDUCATION", 0.9)
        assert score_resume(WEAK).overall != before


class TestFeatureExtraction:
    def test_falls_back_when_the_pdf_lost_its_bullet_glyphs(self) -> None:
        """Extraction often strips bullets; a resume must not score zero for that."""
        with_glyphs = extract_features(
            "- Built a service in Python\n- Designed a MySQL schema\n- Automated the deploys"
        )
        without = extract_features(
            "Built a service in Python\nDesigned a MySQL schema for reporting\n"
            "Automated the deployment pipeline end to end"
        )
        assert len(with_glyphs.bullets) == 3
        assert len(without.bullets) == 3

    @pytest.mark.parametrize(
        "text", ["Jan 2025", "2022 - 2026", "06/2024", "Graduated 2026"]
    )
    def test_recognises_common_date_formats(self, text: str) -> None:
        assert extract_features(text).has_dates

    def test_detects_profile_links(self) -> None:
        f = extract_features("github.com/smitt and linkedin.com/in/smitt")
        assert f.has_github and f.has_linkedin

    def test_finds_quantified_bullets(self) -> None:
        f = extract_features("- Cut load time by 40%\n- Built a thing\n- Served 5000 users")
        assert len(f.quantified_bullets) == 2
