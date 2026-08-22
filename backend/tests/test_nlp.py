"""Phase 4: preprocessing and skill extraction."""

import pytest

from app.services.nlp.preprocessing import (
    STOP_WORDS,
    lemmatize,
    preprocess,
    remove_stop_words,
    tokenize,
)
from app.services.nlp.skill_extractor import all_skills, count_skills, extract_skills


def names(text: str) -> list[str]:
    return [s.name for s in extract_skills(text)]


class TestTokenizer:
    @pytest.mark.parametrize(
        "text,expected",
        [
            ("C++", ["c++"]),
            ("C#", ["c#"]),
            (".NET", [".net"]),
            ("Node.js", ["node.js"]),
            ("scikit-learn", ["scikit-learn"]),
            ("React.js", ["react.js"]),
        ],
    )
    def test_technical_terms_stay_intact(self, text: str, expected: list[str]) -> None:
        """A plain \\w+ tokenizer turns C++ into 'c' — this is the whole point."""
        assert tokenize(text) == expected

    def test_strips_punctuation_between_words(self) -> None:
        assert tokenize("React, FastAPI and MySQL.") == ["react", "fastapi", "and", "mysql"]

    def test_lowercases(self) -> None:
        assert tokenize("PYTHON Python python") == ["python"] * 3

    def test_collapses_whitespace(self) -> None:
        assert tokenize("Python\n\n   and\t\tSQL") == ["python", "and", "sql"]


class TestStopWords:
    def test_removes_common_words(self) -> None:
        assert remove_stop_words(["the", "python", "and", "developer"]) == [
            "python",
            "developer",
        ]

    def test_keeps_technical_tokens(self) -> None:
        assert remove_stop_words(["c++", ".net", "node.js"]) == ["c++", ".net", "node.js"]

    def test_stop_list_is_not_empty(self) -> None:
        assert {"the", "and", "of", "with"} <= STOP_WORDS


class TestLemmatization:
    @pytest.mark.parametrize(
        "word,lemma",
        [("studies", "study"), ("managing", "manage"), ("running", "run"), ("was", "be")],
    )
    def test_reduces_to_dictionary_form(self, word: str, lemma: str) -> None:
        """Note these are real words. A stemmer would give 'studi', 'manag'."""
        assert lemmatize([word]) == [lemma]

    def test_leaves_technical_tokens_alone(self) -> None:
        tokens = ["c++", ".net", "node.js", "scikit-learn"]
        assert lemmatize(tokens) == tokens

    def test_handles_empty_input(self) -> None:
        assert lemmatize([]) == []


class TestFullPipeline:
    def test_end_to_end(self) -> None:
        result = preprocess("He was managing several studies using Python and C++")
        assert "manage" in result and "study" in result
        assert "c++" in result and "python" in result
        assert "he" not in result and "was" not in result


class TestSkillExtraction:
    def test_dictionary_loads(self) -> None:
        assert len(all_skills()) > 50

    @pytest.mark.parametrize(
        "text,skill",
        [
            ("reactjs", "React"),
            ("React.js", "React"),
            ("react js", "React"),
            ("nodejs", "Node.js"),
            ("postgres", "PostgreSQL"),
            ("postgresql", "PostgreSQL"),
            ("sklearn", "scikit-learn"),
            ("scikit learn", "scikit-learn"),
            ("k8s", "Kubernetes"),
            ("golang", "Go"),
            ("gcp", "Google Cloud"),
            ("asp.net", ".NET"),
        ],
    )
    def test_aliases_normalise_to_the_canonical_name(self, text: str, skill: str) -> None:
        assert skill in names(text)

    def test_distinguishes_c_from_cpp_and_csharp(self) -> None:
        assert names("Languages: C, C++, C#") == ["C", "C#", "C++"]

    def test_a_trailing_full_stop_does_not_block_a_match(self) -> None:
        """`.` is a word character for .NET, so this needed care."""
        assert "Python" in names("I have worked with Python.")
        assert "Unit Testing" in names("Wrote unit tests.")

    def test_does_not_fire_on_ordinary_english(self) -> None:
        """The words that made these aliases dangerous in the first place."""
        assert names("We go to production and are ongoing with the rest of the team") == []
        assert names("Studied in the spring semester and can express ideas clearly") == []

    def test_matches_inside_hyphenated_terms(self) -> None:
        assert "React" in names("used react-router for navigation")

    def test_is_case_insensitive(self) -> None:
        assert names("PYTHON") == names("python") == ["Python"]

    def test_deduplicates(self) -> None:
        assert names("Python python PYTHON python3") == ["Python"]

    def test_returns_empty_for_text_with_no_skills(self) -> None:
        assert names("I enjoy long walks and good coffee") == []

    def test_counts_mentions(self) -> None:
        counts = count_skills("Python for scripting. Python for ML. Also Docker.")
        assert counts["Python"] == 2
        assert counts["Docker"] == 1
