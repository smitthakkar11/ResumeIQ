"""Local sentence-embedding similarity (optional).

Runs entirely on this machine — no API, nothing leaves the host. If
sentence-transformers is not installed, every function here reports
unavailable and the rest of the app carries on unchanged.

Same cosine formula as the TF-IDF path; only the vectors differ. TF-IDF
produces sparse word counts, this produces 384 dense learned coordinates
where geometry encodes meaning.
"""

import functools
import logging

import numpy as np

from app.core.config import settings

logger = logging.getLogger(__name__)

MODEL_NAME = "all-MiniLM-L6-v2"
# The model truncates at 256 word-pieces (~200 words). A resume is longer than
# that, so we chunk and mean-pool rather than silently discarding the tail.
CHUNK_WORDS = 180


def is_available() -> bool:
    """True only if the optional dependency is installed and enabled."""
    if not settings.SEMANTIC_SIMILARITY_ENABLED:
        return False
    try:
        import sentence_transformers  # noqa: F401
    except ImportError:
        return False
    return True


@functools.lru_cache(maxsize=1)
def _model():
    """Loaded once, on first use. Costs a few seconds and ~90MB of RAM."""
    from sentence_transformers import SentenceTransformer

    logger.info("Loading sentence-transformer %s", MODEL_NAME)
    return SentenceTransformer(MODEL_NAME)


def _chunks(text: str) -> list[str]:
    words = text.split()
    if not words:
        return []
    return [
        " ".join(words[i : i + CHUNK_WORDS]) for i in range(0, len(words), CHUNK_WORDS)
    ]


def _embed(text: str) -> np.ndarray | None:
    """One unit-length vector for a document of any length.

    Averaging chunk vectors blurs distinct topics together — a real cost — but
    it beats throwing away everything past the first ~200 words.
    """
    pieces = _chunks(text)
    if not pieces:
        return None

    vectors = _model().encode(pieces, normalize_embeddings=True, show_progress_bar=False)
    mean = np.asarray(vectors).mean(axis=0)

    norm = np.linalg.norm(mean)
    return mean / norm if norm else None


def semantic_similarity(resume_text: str, job_text: str) -> float | None:
    """Cosine similarity of the two embeddings, 0..1, or None if unavailable.

    Raw text is used, NOT the TF-IDF preprocessing pipeline: the model was
    trained on ordinary sentences, so stripping stop words and lemmatising
    would move the input away from what it understands.
    """
    if not is_available():
        return None

    try:
        a, b = _embed(resume_text), _embed(job_text)
    except Exception:  # noqa: BLE001 — a model failure must not break analysis
        logger.exception("Semantic similarity failed; continuing without it")
        return None

    if a is None or b is None:
        return None

    # Both vectors are unit length, so the cosine is just the dot product.
    # Clipped because floating point can produce 1.0000000002.
    return float(np.clip(np.dot(a, b), 0.0, 1.0))
