"""Rule-based resume suggestions.

Every message traces to a condition you can read in this file. No LLM: the
advice must be deterministic (same resume -> same advice), testable, and
incapable of inventing a skill or a metric the candidate does not have.

`severity` ranks how much a finding costs the candidate, and is what Phase C's
"what is holding you back" list sorts on.
"""

from dataclasses import dataclass

from app.services.analysis.resume_features import (
    MAX_BULLET_WORDS,
    MIN_BULLET_WORDS,
    ResumeFeatures,
)

LOW_KEYWORD_MATCH = 50.0
LOW_TEXT_SIMILARITY = 25.0
MIN_RESUME_WORDS = 200
MAX_RESUME_WORDS = 1000

# Absence worth mentioning. Certifications and Achievements are genuinely
# optional, so we stay quiet about them.
EXPECTED_SECTIONS = ("Contact", "Education", "Skills")
VALUABLE_SECTIONS = ("Experience", "Projects")

HIGH, MEDIUM, LOW = 3, 2, 1


@dataclass
class Recommendation:
    category: str  # skills | keywords | structure | content | positive
    message: str
    severity: int = MEDIUM


def build_recommendations(
    *,
    features: ResumeFeatures,
    missing_skills: list[str],
    matched_skills: list[str],
    keywords: list[tuple[str, bool]],
    text_similarity: float,
    keyword_match: float,
) -> list[Recommendation]:
    f = features
    tips: list[Recommendation] = []

    # --- skills ---------------------------------------------------------
    if missing_skills:
        shown = ", ".join(missing_skills[:5])
        more = f" (and {len(missing_skills) - 5} more)" if len(missing_skills) > 5 else ""
        verb = "appears" if len(missing_skills) == 1 else "appear"
        was = "was" if len(missing_skills) == 1 else "were"
        it = "it" if len(missing_skills) == 1 else "them"
        tips.append(Recommendation(
            "skills",
            f"{shown}{more} {verb} in the job description but {was} not detected in "
            f"your resume. If you have used {it}, name {it} explicitly.",
            HIGH,
        ))

    if matched_skills and not missing_skills:
        tips.append(Recommendation(
            "positive", "Your resume names every skill the job description asks for.", LOW
        ))

    # Listing a skill is cheap; showing where you used it is the evidence.
    unevidenced = {s.name for s in f.skills} - {s.name for s in f.skills_in_bullets}
    if len(unevidenced) >= 4:
        tips.append(Recommendation(
            "content",
            f"{len(unevidenced)} skills appear only in a list, never in a bullet "
            f"describing what you built with them — for example "
            f"{', '.join(sorted(unevidenced)[:3])}.",
            MEDIUM,
        ))

    # --- keywords -------------------------------------------------------
    absent = [term for term, found in keywords if not found]
    if keyword_match < LOW_KEYWORD_MATCH and absent:
        tips.append(Recommendation(
            "keywords",
            f"Important terms from the posting are absent: {', '.join(absent[:6])}. "
            f"Where they describe work you have actually done, use the posting's wording.",
            MEDIUM,
        ))

    if text_similarity < LOW_TEXT_SIMILARITY:
        tips.append(Recommendation(
            "keywords",
            "Overall wording overlap with this posting is low. Mirroring the "
            "vocabulary the employer uses — honestly — usually helps.",
            MEDIUM,
        ))

    # --- structure ------------------------------------------------------
    for section in EXPECTED_SECTIONS:
        if not f.sections.get(section):
            tips.append(Recommendation(
                "structure",
                f"A {section} section was not detected. If you have one, a clearer "
                f"heading may help automated parsers find it.",
                HIGH if section == "Contact" else MEDIUM,
            ))

    if not any(f.sections.get(s) for s in VALUABLE_SECTIONS):
        tips.append(Recommendation(
            "structure",
            "Neither an Experience nor a Projects section was detected. One of the "
            "two is what most technical roles look for first.",
            HIGH,
        ))

    if not (f.has_github or f.has_linkedin):
        tips.append(Recommendation(
            "structure",
            "No GitHub or LinkedIn link was detected. For technical roles a "
            "profile link is usually expected.",
            MEDIUM,
        ))

    if not f.has_dates:
        tips.append(Recommendation(
            "structure",
            "No dates were detected. Employers look for when each role or project "
            "happened, and for how long.",
            MEDIUM,
        ))
    elif "numeric" in f.date_formats_used and len(f.date_formats_used) > 1:
        # Mixing 06/2024 with "Jun 2024" is genuinely inconsistent; using years
        # for education and months for jobs is not.
        tips.append(Recommendation(
            "structure",
            "Dates are written in more than one format. Picking one style reads "
            "more consistently.",
            LOW,
        ))

    # --- content --------------------------------------------------------
    if not f.quantified_bullets:
        tips.append(Recommendation(
            "content",
            "No figures were detected. Measurable results — team size, percentage "
            "improvements, user counts — make achievements concrete.",
            HIGH,
        ))

    if f.weak_opener_bullets:
        opener = f.weak_opener_bullets[0].split(",")[0][:60]
        tips.append(Recommendation(
            "content",
            f'{len(f.weak_opener_bullets)} bullet(s) open with a phrase describing '
            f'duties rather than results, such as "{opener}…". Leading with an '
            f"action verb (built, designed, reduced) reads stronger.",
            MEDIUM,
        ))

    if f.long_bullets:
        tips.append(Recommendation(
            "content",
            f"{len(f.long_bullets)} bullet(s) run past {MAX_BULLET_WORDS} words. "
            f"Splitting them makes each achievement easier to scan.",
            LOW,
        ))

    if f.short_bullets:
        tips.append(Recommendation(
            "content",
            f"{len(f.short_bullets)} bullet(s) are under {MIN_BULLET_WORDS} words and "
            f"may not say enough on their own.",
            LOW,
        ))

    if f.filler_phrases:
        tips.append(Recommendation(
            "content",
            f'Phrases like "{f.filler_phrases[0]}" describe you without evidence. '
            f"Space spent on them is usually better used on what you built.",
            MEDIUM,
        ))

    if f.overused_words:
        word, count = f.overused_words[0]
        tips.append(Recommendation(
            "content",
            f'"{word}" appears in {count} bullets. Varying the wording keeps them '
            f"from reading as the same sentence repeated.",
            LOW,
        ))

    words = len(f.words)
    if words < MIN_RESUME_WORDS:
        tips.append(Recommendation(
            "content",
            f"The extracted text is short ({words} words). If your resume is longer "
            f"than this, some of it may not be machine-readable.",
            HIGH,
        ))
    elif words > MAX_RESUME_WORDS:
        tips.append(Recommendation(
            "content",
            f"The resume is long ({words} words). Tightening it usually raises the "
            f"proportion of text relevant to any one job.",
            LOW,
        ))

    return tips
