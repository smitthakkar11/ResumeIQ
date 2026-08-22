"""TF-IDF vectors, cosine similarity and job-description keywords."""

from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

from app.services.nlp.preprocessing import preprocess, preprocess_to_string


# Domain-specific stop words: filler that appears in almost every job posting
# and that no resume would ever be penalised for lacking. Removing them is the
# same idea as ordinary stop words, applied to this domain.
JOB_BOILERPLATE = frozenset("""
ability able candidate career company culture degree desirable duty encourage
environment essential excellent experience familiarity field good great hire
ideal include intern internship job join knowledge look mandatory must nice
opportunity partner plus position preferred proficiency proficient qualification
requirement responsibility role skill strong team understanding work year
""".split())


def text_similarity(resume_text: str, job_text: str) -> float:
    """Cosine similarity of the two TF-IDF vectors, in 0..1.

    Both documents are preprocessed first (lowercased, stop words dropped,
    lemmatised) so that "managing" and "managed" land in the same dimension.

    TfidfVectorizer L2-normalises each row, so both vectors have length 1 and
    the cosine reduces to a plain dot product.
    """
    resume = preprocess_to_string(resume_text)
    job = preprocess_to_string(job_text)
    if not resume.strip() or not job.strip():
        return 0.0

    matrix = TfidfVectorizer().fit_transform([resume, job])
    return float(cosine_similarity(matrix[0], matrix[1])[0][0])


def top_keywords(job_text: str, limit: int) -> list[str]:
    """The most important terms in the job description.

    Fitted on the job description alone, so every term has the same IDF and
    this reduces to a term-frequency ranking. That is honest for a single
    document — real IDF needs a corpus of many job descriptions, which is the
    obvious future improvement.

    Unigrams only. Bigrams on a single short document are mostly noise
    (adjacent pairs like "docker aws" tie with everything else), and genuine
    multi-word technologies are already covered by the skill dictionary.
    """
    text = preprocess_to_string(job_text)
    if not text.strip():
        return []

    vectorizer = TfidfVectorizer()
    try:
        matrix = vectorizer.fit_transform([text])
    except ValueError:
        return []  # nothing but stop words

    weights = matrix.toarray()[0]
    terms = vectorizer.get_feature_names_out()
    ranked = sorted(zip(terms, weights), key=lambda pair: pair[1], reverse=True)
    return [
        term
        for term, weight in ranked
        if weight > 0 and term not in JOB_BOILERPLATE
    ][:limit]


def resume_token_set(resume_text: str) -> set[str]:
    return set(preprocess(resume_text))
