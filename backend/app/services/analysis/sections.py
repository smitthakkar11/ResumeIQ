"""Detect which standard sections a resume contains.

Extracted PDF text has no structure, so this is a heuristic: a section is
present if a short, heading-like line matches its vocabulary. Contact is the
exception — it is detected by content, because nobody writes "CONTACT" above
their own email address.

Deliberately reported as "not detected", never as "missing" or "wrong": a
sidebar layout or a creative heading ("Where I've Worked") will defeat this.
"""

import re

MAX_HEADING_CHARS = 60

SECTION_KEYWORDS: dict[str, tuple[str, ...]] = {
    "Summary": ("summary", "objective", "profile", "about me", "career objective"),
    "Education": ("education", "academic", "qualification", "scholastic"),
    "Experience": (
        "experience", "employment", "work history", "professional background",
        "internship", "career history",
    ),
    "Projects": ("project", "portfolio"),
    "Skills": ("skill", "technical proficienc", "technolog", "competenc", "tech stack"),
    "Certifications": ("certification", "certificate", "licence", "license", "course"),
    "Achievements": ("achievement", "award", "honor", "honour", "accomplishment"),
}

EMAIL_RE = re.compile(r"[\w.+-]+@[\w-]+\.[\w.]+")
PHONE_RE = re.compile(r"(?:\+?\d[\d\s().-]{7,}\d)")
PROFILE_RE = re.compile(r"(?:linkedin\.com|github\.com)/\S+", re.I)


def _heading_lines(text: str) -> list[str]:
    """Lines short enough to plausibly be a heading."""
    return [
        line.strip().lower()
        for line in text.splitlines()
        if 0 < len(line.strip()) <= MAX_HEADING_CHARS
    ]


def detect_sections(text: str) -> dict[str, bool]:
    headings = _heading_lines(text)

    found = {
        section: any(keyword in line for line in headings for keyword in keywords)
        for section, keywords in SECTION_KEYWORDS.items()
    }
    # Content-based, not heading-based.
    found["Contact"] = bool(
        EMAIL_RE.search(text) or PHONE_RE.search(text) or PROFILE_RE.search(text)
    )

    # Stable, human order rather than dict insertion order.
    order = [
        "Contact", "Summary", "Education", "Experience",
        "Projects", "Skills", "Certifications", "Achievements",
    ]
    return {section: found[section] for section in order}
