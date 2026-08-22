"""Rule-based resume suggestions.

Every message traces to a condition you can read in this file. No LLM: the
advice must be deterministic (same resume -> same advice), testable, and
incapable of inventing a skill the candidate does not have.
"""

import re
from dataclasses import dataclass

WEAK_PHRASES = ("responsible for", "duties included", "worked on", "helped with")
NUMBER_RE = re.compile(r"\d+\s*%|\b\d[\d,.]*\b")

MIN_RESUME_WORDS = 200
MAX_RESUME_WORDS = 1000
LOW_KEYWORD_MATCH = 50.0
LOW_TEXT_SIMILARITY = 25.0

# Sections whose absence is worth mentioning. Certifications and Achievements
# are genuinely optional, so we stay quiet about them.
EXPECTED_SECTIONS = ("Contact", "Education", "Skills")
VALUABLE_SECTIONS = ("Experience", "Projects")


@dataclass
class Recommendation:
    category: str  # skills | keywords | structure | content | positive
    message: str


def build_recommendations(
    *,
    resume_text: str,
    missing_skills: list[str],
    matched_skills: list[str],
    keywords: list[tuple[str, bool]],
    sections: dict[str, bool],
    text_similarity: float,
    keyword_match: float,
) -> list[Recommendation]:
    tips: list[Recommendation] = []
    words = resume_text.split()

    # --- skills -------------------------------------------------------------
    if missing_skills:
        shown = ", ".join(missing_skills[:5])
        more = f" (and {len(missing_skills) - 5} more)" if len(missing_skills) > 5 else ""
        # "Docker appears" but "Docker and AWS appear".
        verb = "appears" if len(missing_skills) == 1 else "appear"
        it = "it" if len(missing_skills) == 1 else "them"
        tips.append(
            Recommendation(
                "skills",
                f"{shown}{more} {verb} in the job description but "
                f"{'was' if len(missing_skills) == 1 else 'were'} not detected in your "
                f"resume. If you have used {it}, name {it} explicitly.",
            )
        )

    if matched_skills and not missing_skills:
        tips.append(
            Recommendation(
                "positive",
                "Your resume names every skill the job description asks for.",
            )
        )

    # --- keywords -----------------------------------------------------------
    absent = [term for term, found in keywords if not found]
    if keyword_match < LOW_KEYWORD_MATCH and absent:
        tips.append(
            Recommendation(
                "keywords",
                f"Important terms from the posting are absent: {', '.join(absent[:6])}. "
                f"Where they describe work you have actually done, use the posting's wording.",
            )
        )

    if text_similarity < LOW_TEXT_SIMILARITY:
        tips.append(
            Recommendation(
                "keywords",
                "Overall wording overlap with this posting is low. Mirroring the "
                "vocabulary the employer uses — honestly — usually helps.",
            )
        )

    # --- structure ----------------------------------------------------------
    for section in EXPECTED_SECTIONS:
        if not sections.get(section):
            tips.append(
                Recommendation(
                    "structure",
                    f"A {section} section was not detected. If you have one, a clearer "
                    f"heading may help automated parsers find it.",
                )
            )

    if not any(sections.get(s) for s in VALUABLE_SECTIONS):
        tips.append(
            Recommendation(
                "structure",
                "Neither an Experience nor a Projects section was detected. One of "
                "the two is what most technical roles look for first.",
            )
        )

    # --- content ------------------------------------------------------------
    if not NUMBER_RE.search(resume_text):
        tips.append(
            Recommendation(
                "content",
                "No figures were detected. Measurable results — team size, "
                "percentage improvements, user counts — make achievements concrete.",
            )
        )

    found_weak = [p for p in WEAK_PHRASES if p in resume_text.lower()]
    if found_weak:
        tips.append(
            Recommendation(
                "content",
                f'Phrases like "{found_weak[0]}" describe duties rather than results. '
                f"Leading with an action verb (built, designed, reduced) reads stronger.",
            )
        )

    if len(words) < MIN_RESUME_WORDS:
        tips.append(
            Recommendation(
                "content",
                f"The extracted text is short ({len(words)} words). If your resume is "
                f"longer than this, some of it may not be machine-readable.",
            )
        )
    elif len(words) > MAX_RESUME_WORDS:
        tips.append(
            Recommendation(
                "content",
                f"The resume is long ({len(words)} words). Tightening it usually "
                f"raises the proportion of text that is relevant to any one job.",
            )
        )

    return tips
