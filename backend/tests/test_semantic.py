"""Phase 9: local sentence-embedding similarity."""

import pytest

from app.services.matching.semantic import is_available, semantic_similarity
from app.services.matching.similarity import text_similarity

requires_model = pytest.mark.skipif(
    not is_available(),
    reason="sentence-transformers not installed (pip install -r requirements-semantic.txt)",
)


class TestAvailability:
    def test_reports_availability_without_raising(self) -> None:
        """The core app must work whether or not the optional dep is present."""
        assert isinstance(is_available(), bool)

    def test_returns_none_rather_than_raising_when_unavailable(self) -> None:
        if is_available():
            pytest.skip("model is installed in this environment")
        assert semantic_similarity("python", "python") is None


@requires_model
class TestSemanticSimilarity:
    def test_identical_text_scores_near_one(self) -> None:
        text = "Built REST APIs with FastAPI and deployed them to AWS."
        assert semantic_similarity(text, text) == pytest.approx(1.0, abs=1e-4)

    def test_unrelated_text_scores_low(self) -> None:
        score = semantic_similarity(
            "I enjoy baking sourdough bread at the weekend",
            "Experience with Kubernetes, Terraform and CI/CD pipelines",
        )
        assert score < 0.2

    def test_is_symmetric(self) -> None:
        a, b = "Managed a team of engineers", "Led a group of developers"
        assert semantic_similarity(a, b) == pytest.approx(semantic_similarity(b, a), abs=1e-5)

    def test_score_is_in_range(self) -> None:
        score = semantic_similarity("Python developer", "Software engineer")
        assert 0.0 <= score <= 1.0

    def test_empty_input_returns_none(self) -> None:
        assert semantic_similarity("", "Python developer") is None
        assert semantic_similarity("Python developer", "   ") is None

    @pytest.mark.parametrize(
        "resume,job",
        [
            ("Built ML models using sklearn",
             "Experience with machine learning and scikit-learn"),
            ("Led a team of five engineers",
             "Managed a group of software developers"),
            ("Deployed containerised services to the cloud",
             "Experience with Docker and AWS"),
        ],
    )
    def test_catches_meaning_that_tfidf_cannot(self, resume: str, job: str) -> None:
        """The entire justification for this phase.

        These pairs share no vocabulary, so TF-IDF scores them at zero, but
        they plainly describe the same experience.
        """
        assert text_similarity(resume, job) < 0.05
        assert semantic_similarity(resume, job) > 0.35

    def test_long_text_is_chunked_not_truncated(self) -> None:
        """The model caps at ~200 words. Text past that must still count.

        A document whose distinctive content sits only in its tail should still
        match a job description about that content.
        """
        filler = "The candidate has general office experience and communication skills. " * 45
        tail = "Extensive work with Kubernetes, Terraform and cloud infrastructure automation."
        job = "We need a Kubernetes and Terraform infrastructure engineer."

        assert len((filler + tail).split()) > 250  # comfortably past the limit
        assert semantic_similarity(filler + tail, job) > semantic_similarity(filler, job)


@requires_model
class TestEngineIntegration:
    def test_analysis_reports_semantic_similarity_separately(self) -> None:
        from app.services.matching.engine import analyse

        result = analyse(
            "Python developer with React and MySQL experience building web apps.",
            "Looking for a Python engineer who knows React and MySQL to build web applications.",
        )
        assert result.semantic_similarity is not None
        assert 0.0 <= result.semantic_similarity <= 100.0

    def test_semantic_score_is_not_part_of_the_overall_score(self) -> None:
        """Spec: the composite must stay explainable, so this is display-only."""
        from app.services.matching.engine import analyse

        result = analyse(
            "Python developer with React and MySQL experience.",
            "Looking for a Python engineer with React and MySQL for our web team.",
        )
        expected = (
            result.text_similarity * result.weights["text_similarity"]
            + (result.skill_match or 0) * result.weights.get("skill_match", 0)
            + result.keyword_match * result.weights["keyword_match"]
        )
        assert result.overall_score == pytest.approx(expected, abs=0.15)
        assert "semantic" not in " ".join(result.weights)
