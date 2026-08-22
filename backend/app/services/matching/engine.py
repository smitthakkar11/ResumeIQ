"""Composite match scoring.

    Overall = w1 * text similarity   (TF-IDF cosine)
            + w2 * skill match       (matched required / total required)
            + w3 * keyword match     (top JD terms present in the resume)

Every component is reported separately so a user can see which part is weak.
Weights are configurable in .env.
"""

from dataclasses import dataclass, field

from app.core.config import settings
from app.services.matching.similarity import resume_token_set, text_similarity, top_keywords
from app.services.nlp.skill_extractor import Skill, extract_skills


@dataclass
class KeywordHit:
    term: str
    found: bool


@dataclass
class MatchResult:
    overall_score: float
    text_similarity: float
    skill_match: float | None  # None when the job description names no known skills
    keyword_match: float
    matched_skills: list[Skill] = field(default_factory=list)
    missing_skills: list[Skill] = field(default_factory=list)
    extra_skills: list[Skill] = field(default_factory=list)
    keywords: list[KeywordHit] = field(default_factory=list)
    weights: dict[str, float] = field(default_factory=dict)


def _pct(value: float) -> float:
    return round(value * 100, 1)


def analyse(resume_text: str, job_text: str) -> MatchResult:
    # --- 1. Text similarity -------------------------------------------------
    similarity = text_similarity(resume_text, job_text)

    # --- 2. Skill match -----------------------------------------------------
    required = set(extract_skills(job_text))
    present = set(extract_skills(resume_text))

    matched = required & present
    missing = required - present
    # Skills the candidate has that the job did not ask for. Reported for
    # interest only — they earn no points, since the job did not request them.
    extra = present - required

    skill_ratio = len(matched) / len(required) if required else None

    # --- 3. Keyword match ---------------------------------------------------
    resume_tokens = resume_token_set(resume_text)
    keywords = [
        KeywordHit(term=term, found=term in resume_tokens)
        for term in top_keywords(job_text, settings.TOP_KEYWORDS)
    ]
    keyword_ratio = (
        sum(k.found for k in keywords) / len(keywords) if keywords else 0.0
    )

    # --- 4. Weighted total --------------------------------------------------
    components = {
        "text_similarity": (similarity, settings.TEXT_SIMILARITY_WEIGHT),
        "keyword_match": (keyword_ratio, settings.KEYWORD_MATCH_WEIGHT),
    }
    if skill_ratio is not None:
        components["skill_match"] = (skill_ratio, settings.SKILL_MATCH_WEIGHT)

    # If the job description names no recognised skills, that component is
    # dropped and the remaining weights are rescaled. Scoring it as 0 would
    # be misleading — we did not measure it, we could not measure it.
    total_weight = sum(weight for _, weight in components.values())
    overall = (
        sum(value * weight for value, weight in components.values()) / total_weight
        if total_weight
        else 0.0
    )

    return MatchResult(
        overall_score=_pct(overall),
        text_similarity=_pct(similarity),
        skill_match=_pct(skill_ratio) if skill_ratio is not None else None,
        keyword_match=_pct(keyword_ratio),
        matched_skills=sorted(matched),
        missing_skills=sorted(missing),
        extra_skills=sorted(extra),
        keywords=keywords,
        weights={name: round(w / total_weight, 3) for name, (_, w) in components.items()},
    )
