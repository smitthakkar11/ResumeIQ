"""Text preprocessing for the TF-IDF path.

Skill extraction does NOT use this — it runs on lightly-normalised text so
terms like C++ survive. See skill_extractor.py.
"""

import functools
import re

import spacy
from sklearn.feature_extraction.text import ENGLISH_STOP_WORDS

from app.services.nlp.skill_extractor import protected_terms

# Treat + # . - as word-INTERNAL characters so technical terms survive.
# A plain \w+ tokenizer turns "C++" into "C" and ".NET" into "NET".
#   \.?              optional leading dot     -> .net
#   [a-z0-9]+        the word body
#   (?:[.+#-][a-z0-9]+)*  inner punctuation   -> node.js, scikit-learn
#   [+#]*            trailing symbols         -> c++, c#
TOKEN_RE = re.compile(r"\.?[a-z0-9]+(?:[.+#-][a-z0-9]+)*[+#]*")

STOP_WORDS = set(ENGLISH_STOP_WORDS)


@functools.lru_cache(maxsize=1)
def _nlp():
    """spaCy pipeline, loaded once. Only the lemmatizer and its tagger are
    needed, so the parser and NER are disabled — they are the slow parts."""
    return spacy.load("en_core_web_sm", disable=["parser", "ner"])


def normalise(text: str) -> str:
    """Lowercase and collapse whitespace. Characters are left alone."""
    return " ".join(text.lower().split())


def tokenize(text: str) -> list[str]:
    return TOKEN_RE.findall(normalise(text))


def remove_stop_words(tokens: list[str]) -> list[str]:
    return [t for t in tokens if t not in STOP_WORDS]


def lemmatize(tokens: list[str]) -> list[str]:
    """Reduce words to their dictionary form: studies -> study, was -> be.

    Tokens containing symbols (c++, node.js) are passed through untouched —
    spaCy would try to re-tokenize them and we would lose the term. Known
    skill words are protected too, or "kubernetes" becomes "kubernete".
    """
    keep = protected_terms()
    plain = [t for t in tokens if t.isalpha() and t not in keep]
    if not plain:
        return list(tokens)

    # One spaCy call for the whole list. Each token is alphabetic and
    # space-separated, so spaCy's tokens line up 1:1 with ours.
    doc = _nlp()(" ".join(plain))
    lemmas = {word: token.lemma_.lower() for word, token in zip(plain, doc)}
    return [lemmas.get(t, t) for t in tokens]


def preprocess(text: str) -> list[str]:
    """Full pipeline: normalise -> tokenize -> drop stop words -> lemmatize."""
    return lemmatize(remove_stop_words(tokenize(text)))


def preprocess_to_string(text: str) -> str:
    """Same, joined back into a string for scikit-learn's vectorizers."""
    return " ".join(preprocess(text))
