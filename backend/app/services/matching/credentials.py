"""Experience and education matching.

Both are noisy: resumes state dates a dozen ways and rarely say "3 years of
experience" outright. Each result therefore carries `confident`, and both
components are given low weights, so an estimate cannot swing the headline
score. When nothing can be read, the component is dropped rather than scored 0.
"""

import re
from dataclasses import dataclass
from datetime import date

from app.services.analysis.sections import section_text

# "3+ years of experience", "over 2 years' experience"
EXPLICIT_YEARS_RE = re.compile(
    r"(\d+)\s*\+?\s*years?[\s'’]*(?:of\s+)?(?:professional\s+|work\s+|industry\s+|relevant\s+)?experience",
    re.I,
)

MONTHS = "jan|feb|mar|apr|may|jun|jul|aug|sep|oct|nov|dec"

# "Jan 2024 - Jun 2024", "2022 – Present", "06/2023 to 09/2024".
# Months are captured so a six-month internship is not counted as zero years.
RANGE_RE = re.compile(
    rf"(?:({MONTHS})[a-z]*\.?\s+)?((?:19|20)\d{{2}})"
    rf"\s*(?:-|–|—|to)\s*"
    rf"(?:({MONTHS})[a-z]*\.?\s+)?((?:19|20)\d{{2}}|present|current|now)",
    re.I,
)

MONTH_INDEX = {m: i + 1 for i, m in enumerate(MONTHS.split("|"))}

DEGREE_LEVELS = {"": 0, "Bachelor's": 1, "Master's": 2, "PhD": 3}

RESUME_DEGREES = (
    ("PhD", r"\bph\.?\s?d\b|\bdoctorate\b"),
    ("Master's", r"\bmaster'?s?\b|\bm\.?tech\b|\bm\.?sc?\b(?!\w)|\bmca\b|\bmba\b"),
    ("Bachelor's", r"\bbachelor'?s?\b|\bb\.?tech\b|\bb\.?e\.?\b(?!\w)|\bb\.?sc?\b(?!\w)|\bbca\b"),
)


@dataclass
class ExperienceEstimate:
    years: float
    confident: bool
    source: str  # how we arrived at it, shown to the user


@dataclass
class CredentialMatch:
    score: float | None      # 0-100, or None when the job states no requirement
    detail: str


def _merge(intervals: list[tuple[int, int]]) -> float:
    """Total years covered by these month intervals, overlaps counted once."""
    if not intervals:
        return 0.0

    merged: list[list[int]] = []
    for start, end in sorted(intervals):
        if merged and start <= merged[-1][1]:
            merged[-1][1] = max(merged[-1][1], end)
        else:
            merged.append([start, end])

    months = sum(end - start for start, end in merged)
    return round(months / 12, 1)


def estimate_experience(resume_text: str) -> ExperienceEstimate:
    """Years of experience the resume evidences."""
    stated = EXPLICIT_YEARS_RE.search(resume_text)
    if stated:
        return ExperienceEstimate(float(stated.group(1)), True, "stated on the resume")

    # Only dates inside Experience count. A 2022-2026 degree is not four years
    # of work.
    block = section_text(resume_text, "Experience")
    if not block:
        return ExperienceEstimate(0.0, False, "no Experience section detected")

    today = date.today()
    intervals: list[tuple[int, int]] = []

    for start_month, start_year, end_month, end_year in RANGE_RE.findall(block):
        # Work in absolute months so ranges can be merged arithmetically.
        start = int(start_year) * 12 + MONTH_INDEX.get(start_month.lower(), 1)

        if end_year.lower() in ("present", "current", "now"):
            end = today.year * 12 + today.month
        else:
            # A bare end year means "through that year", so default to December.
            end = int(end_year) * 12 + MONTH_INDEX.get(end_month.lower(), 12)

        if start <= end <= (today.year + 1) * 12:
            intervals.append((start, end))

    if not intervals:
        return ExperienceEstimate(0.0, False, "no dated roles found in Experience")

    years = _merge(intervals)
    return ExperienceEstimate(years, True, f"{len(intervals)} dated role(s) in Experience")


def highest_degree(resume_text: str) -> str:
    for label, pattern in RESUME_DEGREES:
        if re.search(pattern, resume_text, re.I):
            return label
    return ""


def match_experience(resume_text: str, required_years: int | None) -> CredentialMatch:
    if required_years is None:
        return CredentialMatch(None, "the posting does not state an experience requirement")

    estimate = estimate_experience(resume_text)

    # Internships and entry-level roles ask for 0 years: anything counts.
    if required_years == 0:
        return CredentialMatch(100.0, f"entry level — {estimate.source}")

    if estimate.years >= required_years:
        return CredentialMatch(
            100.0, f"{estimate.years:g} years found, {required_years} asked for"
        )

    ratio = estimate.years / required_years
    return CredentialMatch(
        round(ratio * 100, 1),
        f"{estimate.years:g} years found, {required_years} asked for ({estimate.source})",
    )


def match_education(resume_text: str, required: str) -> CredentialMatch:
    if not required:
        return CredentialMatch(None, "the posting does not state a degree requirement")

    held = highest_degree(resume_text)
    have, want = DEGREE_LEVELS.get(held, 0), DEGREE_LEVELS.get(required, 0)

    if have >= want:
        return CredentialMatch(100.0, f"{held or 'no degree'} meets {required}")
    if have == want - 1:
        # One level short is a partial match, not a disqualification.
        return CredentialMatch(50.0, f"{held or 'no degree'} found, {required} asked for")
    return CredentialMatch(0.0, f"{held or 'no degree detected'}, {required} asked for")
