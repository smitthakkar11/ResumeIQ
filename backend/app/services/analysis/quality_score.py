"""Resume quality score — how strong the resume is on its own terms.

Independent of any job description. Every point is earned by a rule below, and
each component reports the checks it ran, so the number is always traceable.

The thresholds (15 skills, 200-1000 words, 35-word bullets) are judgement
calls, not fitted values. They are stated here rather than buried so they can
be argued with.
"""

from dataclasses import dataclass, field

from app.core.config import settings
from app.services.analysis.resume_features import ResumeFeatures, extract_features

TARGET_SKILLS = 15
TARGET_CATEGORIES = 5
IDEAL_MIN_WORDS = 200
IDEAL_MAX_WORDS = 1000


@dataclass
class Check:
    """One rule, and whether the resume satisfied it."""

    label: str
    earned: float
    maximum: float
    detail: str


@dataclass
class Component:
    key: str
    label: str
    score: float                      # 0-100
    checks: list[Check] = field(default_factory=list)


@dataclass
class QualityScore:
    overall: float                    # 0-100
    components: list[Component] = field(default_factory=list)
    weights: dict[str, float] = field(default_factory=dict)


def _pct(earned: float, maximum: float) -> float:
    return round(earned / maximum * 100, 1) if maximum else 0.0


def _ratio(value: float, target: float) -> float:
    """Progress towards a target, capped at 1. Diminishing returns are handled
    by the cap: 30 skills is not twice as good as 15."""
    return min(value / target, 1.0) if target else 0.0


# ---------------------------------------------------------------------------
# Components
# ---------------------------------------------------------------------------

def _skills(f: ResumeFeatures) -> Component:
    count, categories = len(f.skills), len(f.skill_categories)
    checks = [
        Check(
            "Recognised skills named", round(70 * _ratio(count, TARGET_SKILLS), 1), 70,
            f"{count} found; {TARGET_SKILLS} scores full marks",
        ),
        Check(
            "Spread across areas", round(30 * _ratio(categories, TARGET_CATEGORIES), 1), 30,
            f"{categories} of {TARGET_CATEGORIES} categories represented",
        ),
    ]
    return Component("skills", "Skills", _pct(sum(c.earned for c in checks), 100), checks)


def _keywords(f: ResumeFeatures) -> Component:
    """Vocabulary strength: density, evidence, and freedom from filler.

    The evidence check is the important one. Listing "Docker" in a skills
    section costs nothing; describing what you built with it is the claim an
    employer can actually assess — and it is what keyword stuffing cannot fake.
    """
    per_hundred = len(f.skills) / max(len(f.words) / 100, 1)
    evidenced = len(f.skills_in_bullets)
    coverage = evidenced / len(f.skills) if f.skills else 0.0
    filler = len(f.filler_phrases)

    checks = [
        Check(
            "Technical terms per 100 words", round(30 * _ratio(per_hundred, 3.0), 1), 30,
            f"{per_hundred:.1f} per 100 words; 3.0 scores full marks",
        ),
        Check(
            "Skills backed by a bullet", round(45 * _ratio(coverage, 0.6), 1), 45,
            f"{evidenced} of {len(f.skills)} skills appear in a bullet, not just a list",
        ),
        Check(
            "Free of filler phrases", max(0.0, 25 - 8 * filler), 25,
            "none found" if not filler else f"found: {', '.join(f.filler_phrases[:3])}",
        ),
    ]
    return Component("keywords", "Keywords", _pct(sum(c.earned for c in checks), 100), checks)


def _projects(f: ResumeFeatures) -> Component:
    present = f.sections.get("Projects", False)
    naming = len(f.bullets_naming_a_skill)
    quantified = len(f.quantified_bullets)

    checks = [
        Check("Projects section detected", 40.0 if present else 0.0, 40,
              "found" if present else "no Projects heading detected"),
        Check("Projects name their technologies", round(35 * _ratio(naming, 4), 1), 35,
              f"{naming} bullet(s) name a recognised technology; 4 scores full marks"),
        Check("Projects show measurable outcomes", round(25 * _ratio(quantified, 3), 1), 25,
              f"{quantified} bullet(s) contain a figure; 3 scores full marks"),
    ]
    return Component("projects", "Projects", _pct(sum(c.earned for c in checks), 100), checks)


def _experience(f: ResumeFeatures) -> Component:
    present = f.sections.get("Experience", False)
    strong = len(f.strong_opener_bullets)
    weak = len(f.weak_opener_bullets)

    checks = [
        Check("Experience section detected", 40.0 if present else 0.0, 40,
              "found" if present else "no Experience heading detected"),
        Check("Dates present", 25.0 if f.has_dates else 0.0, 25,
              "found" if f.has_dates else "no date ranges detected"),
        # Proportion, not count: one weak bullet among three matters more than
        # one among twenty, and adding bullets should not paper over phrasing.
        Check("Bullets lead with action verbs",
              round(35 * (strong / (strong + weak)) if (strong + weak) else 0.0, 1), 35,
              f"{strong} strong, {weak} weak"
              + (' ("responsible for", "worked on"…)' if weak else "")),
    ]
    return Component("experience", "Experience", _pct(sum(c.earned for c in checks), 100), checks)


def _education(f: ResumeFeatures) -> Component:
    present = f.sections.get("Education", False)
    has_degree = any(
        term in f.text.lower()
        for term in ("bachelor", "master", "phd", "b.tech", "btech", "b.e", "m.tech", "degree")
    )
    checks = [
        Check("Education section detected", 50.0 if present else 0.0, 50,
              "found" if present else "no Education heading detected"),
        Check("Degree named", 30.0 if has_degree else 0.0, 30,
              "found" if has_degree else "no degree named"),
        Check("Dates present", 20.0 if f.has_dates else 0.0, 20,
              "found" if f.has_dates else "no dates detected"),
    ]
    return Component("education", "Education", _pct(sum(c.earned for c in checks), 100), checks)


def _formatting(f: ResumeFeatures) -> Component:
    contact_bits = sum([f.has_email, f.has_phone, f.has_github or f.has_linkedin])
    words = len(f.words)
    in_range = IDEAL_MIN_WORDS <= words <= IDEAL_MAX_WORDS
    bad_bullets = len(f.long_bullets) + len(f.short_bullets)
    core_sections = sum(f.sections.get(s, False) for s in ("Education", "Skills"))

    checks = [
        Check("Contact details", round(30 * _ratio(contact_bits, 3), 1), 30,
              f"{contact_bits} of 3 (email, phone, profile link)"),
        Check("Length", 30.0 if in_range else 10.0, 30,
              f"{words} words"
              + ("" if in_range else f"; {IDEAL_MIN_WORDS}-{IDEAL_MAX_WORDS} reads best")),
        Check("Bullet lengths", max(0.0, 20 - 5 * bad_bullets), 20,
              "all within range" if not bad_bullets
              else f"{len(f.long_bullets)} too long, {len(f.short_bullets)} too short"),
        Check("Core sections present", round(20 * _ratio(core_sections, 2), 1), 20,
              f"{core_sections} of 2 (Education, Skills)"),
    ]
    return Component("formatting", "Formatting", _pct(sum(c.earned for c in checks), 100), checks)


BUILDERS = (_skills, _keywords, _projects, _experience, _education, _formatting)


def score_resume(text: str) -> QualityScore:
    features = extract_features(text)
    components = [build(features) for build in BUILDERS]

    weights = settings.quality_weights
    total = sum(weights.get(c.key, 0) for c in components)
    overall = (
        sum(c.score * weights.get(c.key, 0) for c in components) / total if total else 0.0
    )

    return QualityScore(
        overall=round(overall, 1),
        components=components,
        weights={c.key: round(weights.get(c.key, 0) / total, 3) for c in components},
    )
