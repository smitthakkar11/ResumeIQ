"""Phase 5: TF-IDF, cosine similarity, skill matching and composite scoring."""

import numpy as np
import pytest
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

from app.core.config import settings
from app.services.matching.engine import analyse
from app.services.matching.similarity import text_similarity, top_keywords

JOB = """
Software Engineer. We are looking for an engineer with Python, React, MySQL,
Docker and AWS experience. Kubernetes knowledge is a plus. You will build
REST APIs and work in an Agile team.
"""

STRONG_RESUME = """
Smit Thakkar. Skills: Python, React, MySQL, Docker, AWS, Kubernetes.
Built REST APIs in an Agile team. Deployed containers to AWS.
"""

WEAK_RESUME = """
Marketing coordinator. Managed social media campaigns, wrote copy,
organised events and produced monthly newsletters using Canva.
"""


class TestTfidfMaths:
    """Pin the arithmetic from the worked example, so the theory is testable."""

    def test_idf_matches_the_smoothed_formula(self) -> None:
        docs = ["python developer python", "python engineer"]
        vec = TfidfVectorizer().fit(docs)
        idf = dict(zip(vec.get_feature_names_out(), vec.idf_))

        n = len(docs)
        # ln((1+n)/(1+df)) + 1
        assert idf["python"] == pytest.approx(np.log((1 + n) / (1 + 2)) + 1)
        assert idf["developer"] == pytest.approx(np.log((1 + n) / (1 + 1)) + 1)

    def test_rows_are_l2_normalised(self) -> None:
        matrix = TfidfVectorizer().fit_transform(["python developer python", "python engineer"])
        for row in matrix.toarray():
            assert np.linalg.norm(row) == pytest.approx(1.0)

    def test_cosine_equals_dot_product_because_rows_are_unit_length(self) -> None:
        matrix = TfidfVectorizer().fit_transform(["python developer python", "python engineer"])
        cosine = cosine_similarity(matrix[0], matrix[1])[0][0]
        dot = float(matrix[0].multiply(matrix[1]).sum())
        assert cosine == pytest.approx(dot)

    def test_worked_example_value(self) -> None:
        """The number computed by hand in the Phase 5 explanation."""
        matrix = TfidfVectorizer().fit_transform(["python developer python", "python engineer"])
        assert cosine_similarity(matrix[0], matrix[1])[0][0] == pytest.approx(0.4743, abs=1e-4)


class TestTextSimilarity:
    def test_identical_text_scores_one(self) -> None:
        assert text_similarity(JOB, JOB) == pytest.approx(1.0)

    def test_unrelated_text_scores_near_zero(self) -> None:
        assert text_similarity("python docker kubernetes", "poetry baking gardening") < 0.05

    def test_relevant_resume_beats_irrelevant_one(self) -> None:
        assert text_similarity(STRONG_RESUME, JOB) > text_similarity(WEAK_RESUME, JOB)

    def test_is_symmetric(self) -> None:
        assert text_similarity(STRONG_RESUME, JOB) == pytest.approx(
            text_similarity(JOB, STRONG_RESUME)
        )

    def test_empty_input_scores_zero(self) -> None:
        assert text_similarity("", JOB) == 0.0
        assert text_similarity(STRONG_RESUME, "") == 0.0

    def test_length_alone_does_not_change_the_score(self) -> None:
        """Cosine measures angle, not magnitude — repeating a document
        triples its vector's length but not its direction."""
        doc = "python react mysql docker"
        tripled = (doc + " ") * 3  # note the space: doc*3 would glue "docker" to "python"
        assert text_similarity(doc, JOB) == pytest.approx(
            text_similarity(tripled, JOB), abs=1e-6
        )


class TestKeywords:
    def test_returns_meaningful_terms(self) -> None:
        terms = top_keywords(JOB, 15)
        assert "python" in terms and "docker" in terms and "kubernetes" in terms

    def test_drops_job_posting_boilerplate(self) -> None:
        terms = top_keywords(JOB, 15)
        for filler in ("experience", "knowledge", "plus", "look", "team", "work"):
            assert filler not in terms

    def test_respects_the_limit(self) -> None:
        assert len(top_keywords(JOB, 5)) == 5

    def test_empty_job_description_gives_no_keywords(self) -> None:
        assert top_keywords("", 10) == []


class TestSkillMatching:
    def test_splits_required_skills_into_matched_and_missing(self) -> None:
        result = analyse(
            "I know Python, React, AWS and MySQL.",
            "Required: Python, React, Docker, AWS, MySQL.",
        )
        assert {s.name for s in result.matched_skills} == {"Python", "React", "AWS", "MySQL"}
        assert {s.name for s in result.missing_skills} == {"Docker"}

    def test_skill_match_is_matched_over_required(self) -> None:
        result = analyse(
            "I know Python, React, AWS and MySQL.",
            "Required: Python, React, Docker, AWS, MySQL.",
        )
        assert result.skill_match == pytest.approx(80.0)  # 4 of 5

    def test_irrelevant_extra_skills_earn_no_points(self) -> None:
        """Spec: do not give extra credit for skills the job never asked for."""
        plain = analyse("I know Python.", "Required: Python and Docker.")
        padded = analyse(
            "I know Python, Rust, Scala, Kotlin, Swift, PHP, Tableau.",
            "Required: Python and Docker.",
        )
        assert padded.skill_match == plain.skill_match
        assert len(padded.extra_skills) > len(plain.extra_skills)

    def test_all_skills_present_scores_full_marks(self) -> None:
        result = analyse("Python, React, Docker", "Need Python, React and Docker")
        assert result.skill_match == 100.0
        assert result.missing_skills == []


class TestCompositeScore:
    def test_components_combine_with_the_configured_weights(self) -> None:
        r = analyse(STRONG_RESUME, JOB)
        expected = (
            r.text_similarity * r.weights["text_similarity"]
            + r.skill_match * r.weights["skill_match"]
            + r.keyword_match * r.weights["keyword_match"]
        )
        assert r.overall_score == pytest.approx(expected, abs=0.15)

    def test_weights_sum_to_one(self) -> None:
        assert sum(analyse(STRONG_RESUME, JOB).weights.values()) == pytest.approx(1.0)

    def test_configured_weights_are_the_documented_ones(self) -> None:
        assert settings.TEXT_SIMILARITY_WEIGHT == pytest.approx(0.4)
        assert settings.SKILL_MATCH_WEIGHT == pytest.approx(0.4)
        assert settings.KEYWORD_MATCH_WEIGHT == pytest.approx(0.2)

    def test_a_strong_resume_outscores_a_weak_one(self) -> None:
        assert analyse(STRONG_RESUME, JOB).overall_score > analyse(WEAK_RESUME, JOB).overall_score

    def test_scores_are_percentages(self) -> None:
        r = analyse(STRONG_RESUME, JOB)
        for value in (r.overall_score, r.text_similarity, r.skill_match, r.keyword_match):
            assert 0.0 <= value <= 100.0

    def test_skill_component_is_dropped_not_zeroed_when_no_skills_are_named(self) -> None:
        """Scoring an unmeasurable component as 0 would be misleading."""
        r = analyse("I write clearly and work well with others.", "We need a great communicator "
                    "who can write clearly and collaborate with a wide range of people daily.")
        assert r.skill_match is None
        assert "skill_match" not in r.weights
        assert sum(r.weights.values()) == pytest.approx(1.0)
