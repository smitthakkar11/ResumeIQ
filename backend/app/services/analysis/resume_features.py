"""One structured read of a resume, shared by scoring and recommendations.

Everything here is observable in the text: counts, patterns, presence. No
judgements are made at this layer — quality_score.py and recommendations.py
decide what the numbers mean.
"""

import re
from dataclasses import dataclass, field
from functools import cached_property

from app.services.analysis.sections import EMAIL_RE, PHONE_RE, detect_sections
from app.services.nlp.skill_extractor import Skill, extract_skills

GITHUB_RE = re.compile(r"github\.com/[\w-]+", re.I)
LINKEDIN_RE = re.compile(r"linkedin\.com/in/[\w-]+", re.I)

BULLET_CHARS = ("•", "▪", "‣", "●", "-", "–", "*", "·")

# A number that says how much: "40%", "5000 users", "reduced by 3x".
QUANTIFIED_RE = re.compile(r"\b\d[\d,.]*\s*(?:%|x\b|k\b|m\b|\+)|\b\d[\d,.]{2,}\b|\b\d+\s+\w+s\b")

# Month-year, year ranges, numeric dates — used to check date consistency.
DATE_PATTERNS = {
    "month_year": re.compile(
        r"\b(?:jan|feb|mar|apr|may|jun|jul|aug|sep|oct|nov|dec)[a-z]*\.?\s+\d{4}\b", re.I
    ),
    "year_range": re.compile(r"\b(19|20)\d{2}\s*[-–—]\s*(?:(19|20)\d{2}|present|current)\b", re.I),
    "numeric": re.compile(r"\b\d{1,2}/\d{4}\b"),
    # A lone year, as in "Intern, 2025". Common, and previously missed.
    "bare_year": re.compile(r"\b(?:19|20)\d{2}\b"),
}

STRONG_VERBS = frozenset("""
built designed implemented developed led created engineered architected automated
optimised optimized reduced improved increased launched shipped migrated delivered
integrated deployed refactored scaled published analysed analyzed researched
trained mentored founded initiated streamlined resolved debugged
""".split())

WEAK_OPENERS = (
    "responsible for", "duties included", "worked on", "helped with", "assisted with",
    "involved in", "participated in", "tasked with", "in charge of",
)

# Claims about yourself that carry no evidence.
FILLER_PHRASES = (
    "team player", "hard working", "hardworking", "self starter", "go-getter",
    "results-driven", "detail oriented", "detail-oriented", "passionate about",
    "think outside the box", "synergy", "dynamic individual", "excellent communication",
)

MAX_BULLET_WORDS = 35
MIN_BULLET_WORDS = 4


@dataclass
class ResumeFeatures:
    text: str
    sections: dict[str, bool] = field(default_factory=dict)
    skills: list[Skill] = field(default_factory=list)

    # ---- basic shape ----

    @cached_property
    def words(self) -> list[str]:
        return self.text.split()

    @cached_property
    def lines(self) -> list[str]:
        return [ln.strip() for ln in self.text.splitlines() if ln.strip()]

    @cached_property
    def bullets(self) -> list[str]:
        """Bullet lines.

        PDF extraction sometimes loses bullet glyphs entirely, so if we find
        almost none we fall back to treating substantial non-heading lines as
        bullets. Otherwise a resume would score zero on bullet quality purely
        because of how it was exported.
        """
        marked = [
            ln.lstrip("".join(BULLET_CHARS) + " ").strip()
            for ln in self.lines
            if ln.startswith(BULLET_CHARS)
        ]
        if len(marked) >= 3:
            return [b for b in marked if b]

        return [ln for ln in self.lines if len(ln.split()) >= 5]

    # ---- contact ----

    @cached_property
    def has_email(self) -> bool:
        return bool(EMAIL_RE.search(self.text))

    @cached_property
    def has_phone(self) -> bool:
        return bool(PHONE_RE.search(self.text))

    @cached_property
    def has_github(self) -> bool:
        return bool(GITHUB_RE.search(self.text))

    @cached_property
    def has_linkedin(self) -> bool:
        return bool(LINKEDIN_RE.search(self.text))

    # ---- content quality ----

    @cached_property
    def quantified_bullets(self) -> list[str]:
        return [b for b in self.bullets if QUANTIFIED_RE.search(b)]

    @cached_property
    def strong_opener_bullets(self) -> list[str]:
        """Bullets whose first word is a strong action verb."""
        out = []
        for b in self.bullets:
            first = re.sub(r"[^a-z]", "", b.split()[0].lower()) if b.split() else ""
            if first in STRONG_VERBS:
                out.append(b)
        return out

    @cached_property
    def weak_opener_bullets(self) -> list[str]:
        return [b for b in self.bullets if b.lower().startswith(WEAK_OPENERS)]

    @cached_property
    def long_bullets(self) -> list[str]:
        return [b for b in self.bullets if len(b.split()) > MAX_BULLET_WORDS]

    @cached_property
    def short_bullets(self) -> list[str]:
        return [b for b in self.bullets if len(b.split()) < MIN_BULLET_WORDS]

    @cached_property
    def filler_phrases(self) -> list[str]:
        low = self.text.lower()
        return [p for p in FILLER_PHRASES if p in low]

    @cached_property
    def overused_words(self) -> list[tuple[str, int]]:
        """Content words repeated a lot across bullets — usually a sign of
        every bullet being phrased the same way."""
        counts: dict[str, int] = {}
        for b in self.bullets:
            for word in {w for w in re.findall(r"[a-z]{5,}", b.lower())}:
                counts[word] = counts.get(word, 0) + 1

        threshold = max(3, len(self.bullets) // 3)
        return sorted(
            ((w, c) for w, c in counts.items() if c >= threshold),
            key=lambda pair: -pair[1],
        )[:5]

    # ---- dates ----

    @cached_property
    def date_formats_used(self) -> list[str]:
        return [name for name, pattern in DATE_PATTERNS.items() if pattern.search(self.text)]

    @cached_property
    def has_dates(self) -> bool:
        return bool(self.date_formats_used)

    # ---- skills ----

    @cached_property
    def skill_categories(self) -> set[str]:
        return {s.category for s in self.skills}

    @staticmethod
    def _is_enumeration(line: str) -> bool:
        """True for comma-separated lists like "Python, Docker, React, MySQL".

        These are inventories, not descriptions of work, so they must not count
        as evidence that a skill was used.
        """
        words = line.split()
        return bool(words) and line.count(",") / len(words) >= 0.25

    @cached_property
    def prose_bullets(self) -> list[str]:
        """Bullets that describe work, with skill inventories filtered out."""
        return [b for b in self.bullets if not self._is_enumeration(b)]

    @cached_property
    def skills_in_bullets(self) -> list[Skill]:
        """Skills demonstrated in a bullet rather than only listed.

        A skills section proves you can type the word; a bullet describing
        what you built with it is evidence.
        """
        return extract_skills(" ".join(self.prose_bullets))

    @cached_property
    def bullets_naming_a_skill(self) -> list[str]:
        names = {s.name.lower() for s in self.skills}
        return [b for b in self.prose_bullets if any(n in b.lower() for n in names)]


def extract_features(text: str) -> ResumeFeatures:
    return ResumeFeatures(
        text=text,
        sections=detect_sections(text),
        skills=extract_skills(text),
    )
