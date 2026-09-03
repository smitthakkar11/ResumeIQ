"""What is holding this resume back, ranked by what it actually costs.

Each blocker carries an estimated number of points off the overall score,
computed from the same weights the score itself uses. That makes the ranking
defensible: the top item is the one worth fixing first, not the one that
sounds worst.

Nothing here suggests claiming a skill the candidate does not have. Where the
gap is genuine, the suggested fix says so.
"""

from dataclasses import dataclass

MAX_BLOCKERS = 6
# Below this a blocker is noise rather than a finding.
MIN_COST_POINTS = 1.0


@dataclass
class Blocker:
    title: str
    detail: str          # why it matters, from the actual analysis
    fix: str             # what to do about it
    cost: float          # estimated points off the overall score
    category: str        # skills | keywords | wording | experience | education


def _skill_reason(name: str, mentions: int) -> str:
    if mentions >= 3:
        return f"{name} appears {mentions} times in the posting, so it is central to the role."
    if mentions == 2:
        return f"{name} is mentioned twice in the posting."
    return f"{name} is listed among the requirements."


def build_blockers(
    *,
    weights: dict[str, float],
    missing_skills: list[str],
    partial_skills: list[tuple[str, list[str]]],   # (skill, evidence)
    required_count: int,
    jd_skill_mentions: dict[str, int],
    absent_keywords: list[str],
    keyword_match: float,
    text_similarity: float,
    experience_match: float | None,
    experience_detail: str,
    education_match: float | None,
    education_detail: str,
    partial_credit: float,
) -> list[Blocker]:
    blockers: list[Blocker] = []

    skill_weight = weights.get("skill_match", 0)
    per_skill = (skill_weight * 100 / required_count) if required_count else 0

    # --- one blocker per missing required skill -----------------------------
    for name in missing_skills:
        blockers.append(Blocker(
            title=f"Missing: {name}",
            detail=_skill_reason(name, jd_skill_mentions.get(name, 1))
                   + " Your resume shows no evidence of it, related or otherwise.",
            fix=f"If you have used {name}, name it explicitly and say what you built "
                f"with it. If you have not, this is a real gap worth closing.",
            cost=round(per_skill, 1),
            category="skills",
        ))

    # --- partial matches cost the fraction not credited ---------------------
    for name, evidence in partial_skills:
        blockers.append(Blocker(
            title=f"Weak evidence: {name}",
            detail=f"The posting asks for {name}. Your resume shows "
                   f"{', '.join(evidence)}, which is related but not the same thing.",
            fix=f"If you have used {name} directly, say so. Otherwise make the "
                f"related work more concrete so the overlap is obvious.",
            cost=round(per_skill * (1 - partial_credit), 1),
            category="skills",
        ))

    # --- keywords -----------------------------------------------------------
    keyword_cost = weights.get("keyword_match", 0) * (100 - keyword_match)
    if absent_keywords and keyword_cost >= MIN_COST_POINTS:
        blockers.append(Blocker(
            title="Low keyword coverage",
            detail=f"{len(absent_keywords)} important terms from the posting do not "
                   f"appear in your resume: {', '.join(absent_keywords[:6])}.",
            fix="Where these describe work you have actually done, use the "
                "posting's wording rather than your own.",
            cost=round(keyword_cost, 1),
            category="keywords",
        ))

    # --- overall wording ----------------------------------------------------
    wording_cost = weights.get("text_similarity", 0) * (100 - text_similarity)
    if wording_cost >= MIN_COST_POINTS:
        blockers.append(Blocker(
            title="Wording overlap is low",
            detail=f"Only {text_similarity}% of the vocabulary is shared with this "
                   f"posting. Screening tools compare the words themselves.",
            fix="Rewrite bullets that describe the same work in different words, "
                "using the employer's terms where they are accurate.",
            cost=round(wording_cost, 1),
            category="wording",
        ))

    # --- credentials --------------------------------------------------------
    if experience_match is not None and experience_match < 100:
        cost = weights.get("experience_match", 0) * (100 - experience_match)
        if cost >= MIN_COST_POINTS:
            blockers.append(Blocker(
                title="Less experience than asked for",
                detail=f"{experience_detail}. This is read from dates in your "
                       f"Experience section, so it can undercount.",
                fix="If you have relevant experience the dates do not capture — "
                    "freelance, open source, coursework — give it a dated entry.",
                cost=round(cost, 1),
                category="experience",
            ))

    if education_match is not None and education_match < 100:
        cost = weights.get("education_match", 0) * (100 - education_match)
        if cost >= MIN_COST_POINTS:
            blockers.append(Blocker(
                title="Degree below the stated requirement",
                detail=f"{education_detail}.",
                fix="If you hold or are studying for the degree, make sure it is "
                    "written plainly in an Education section.",
                cost=round(cost, 1),
                category="education",
            ))

    ranked = sorted(blockers, key=lambda b: -b.cost)
    return [b for b in ranked if b.cost >= MIN_COST_POINTS][:MAX_BLOCKERS]
