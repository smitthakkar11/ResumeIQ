"""Pull structured requirements out of a free-text job description.

Rule-based on purpose: every field below can be traced to a phrase in the
posting. Job descriptions have no standard format, so this is a heuristic —
`confidence` flags which fields we actually found rather than guessed.
"""

import re
from dataclasses import dataclass, field

from app.services.nlp.skill_extractor import Skill, extract_skills

# A line that switches everything after it into the "preferred" bucket.
PREFERRED_HEADINGS = (
    "preferred", "nice to have", "nice-to-have", "bonus", "desirable",
    "good to have", "pluses", "optional",
)
# ...and back into "required".
REQUIRED_HEADINGS = (
    "required", "requirement", "must have", "must-have", "qualification",
    "responsibilities", "what you", "you will", "minimum",
)
# Cues that mark a single line as preferred regardless of the heading above it.
INLINE_PREFERRED = ("is a plus", "a plus", "nice to have", "bonus", "preferred", "desirable")

SOFT_SKILLS = {
    "Communication": ("communication", "communicate", "written and verbal"),
    "Teamwork": ("teamwork", "team player", "collaborat", "cross-functional"),
    "Problem solving": ("problem solving", "problem-solving", "troubleshoot"),
    "Leadership": ("leadership", "lead a team", "mentor"),
    "Adaptability": ("adaptab", "fast-paced", "ambiguity"),
    "Time management": ("time management", "prioriti", "deadline"),
    "Attention to detail": ("attention to detail", "detail-oriented"),
    "Analytical thinking": ("analytical", "critical thinking"),
    "Ownership": ("ownership", "self-motivated", "self-starter", "autonom"),
}

DEGREES = (
    ("PhD", r"\bph\.?\s?d\b|\bdoctorate\b"),
    ("Master's", r"\bmaster'?s?\b|\bm\.?tech\b|\bm\.?s\.?\b(?!\w)|\bmca\b"),
    ("Bachelor's", r"\bbachelor'?s?\b|\bb\.?tech\b|\bb\.?e\.?\b(?!\w)|\bb\.?s\.?c?\b(?!\w)|\bundergraduate\b"),
)

ROLE_WORDS = (
    "engineer", "developer", "analyst", "scientist", "intern", "manager",
    "designer", "architect", "administrator", "consultant", "specialist",
)

YEARS_RE = re.compile(r"(\d+)\s*\+?\s*(?:-\s*\d+\s*)?year", re.I)

# Split on sentence-ending punctuation followed by whitespace. Requiring the
# whitespace keeps "Node.js" and "B.Tech" intact.
SENTENCE_RE = re.compile(r"(?<=[.!?;])\s+")


@dataclass
class JobRequirements:
    role: str = ""
    required_skills: list[Skill] = field(default_factory=list)
    preferred_skills: list[Skill] = field(default_factory=list)
    soft_skills: list[str] = field(default_factory=list)
    education: str = ""          # "Bachelor's", "Master's", "PhD" or ""
    experience: str = ""         # e.g. "2+ years", "Internship", "Entry level"
    min_years: int | None = None

    @property
    def confidence(self) -> dict[str, bool]:
        """Which fields were actually found in the text, not inferred."""
        return {
            "role": bool(self.role),
            "education": bool(self.education),
            "experience": bool(self.experience),
            "skills": bool(self.required_skills or self.preferred_skills),
        }


def _split_buckets(text: str) -> tuple[str, str]:
    """Return (required_text, preferred_text).

    Walks the posting line by line. A short line naming a bucket switches the
    current bucket; a line with an inline cue like "is a plus" is treated as
    preferred on its own, whatever heading it sits under.
    """
    required, preferred = [], []
    bucket = required

    for raw in text.splitlines():
        line = raw.strip()
        if not line:
            continue
        low = line.lower()

        # Headings are short. A long sentence mentioning "preferred" is prose.
        if len(line) <= 80:
            switched = None
            if any(h in low for h in PREFERRED_HEADINGS):
                switched = preferred
            elif any(h in low for h in REQUIRED_HEADINGS):
                switched = required

            if switched is not None:
                bucket = switched
                # "Required: Python, React" is a heading AND content. Keep
                # whatever follows the colon rather than discarding the skills.
                _, _, rest = line.partition(":")
                if len(re.sub(r"[^a-z0-9]", "", rest.lower())) >= 2:
                    bucket.append(rest.strip())
                continue

        # Classify per sentence, not per line. A prose posting is often one
        # paragraph, and "Kubernetes is a plus" at the end of it must not push
        # every requirement in that paragraph into the preferred bucket.
        for sentence in SENTENCE_RE.split(line):
            sentence = sentence.strip()
            if not sentence:
                continue
            low_sentence = sentence.lower()
            target = preferred if any(c in low_sentence for c in INLINE_PREFERRED) else bucket
            target.append(sentence)

    return "\n".join(required), "\n".join(preferred)


def _extract_role(text: str) -> str:
    """The job title, if the posting states one near the top."""
    match = re.search(r"^\s*(?:job\s*title|position|role)\s*[:\-]\s*(.+)$", text, re.I | re.M)
    if match:
        return match.group(1).strip()[:160]

    # Otherwise the first short line that names a role.
    for line in text.splitlines()[:8]:
        line = line.strip(" .-–—")
        if 3 < len(line) <= 80 and any(w in line.lower() for w in ROLE_WORDS):
            return re.split(r"[.|·•]", line)[0].strip()[:160]
    return ""


def _extract_education(text: str) -> str:
    """Highest degree the posting mentions."""
    for label, pattern in DEGREES:
        if re.search(pattern, text, re.I):
            return label
    return ""


def _extract_experience(text: str) -> tuple[str, int | None]:
    low = text.lower()

    years = [int(m) for m in YEARS_RE.findall(text) if int(m) <= 30]
    if years:
        smallest = min(years)
        return f"{smallest}+ years", smallest

    if "intern" in low:
        return "Internship", 0
    if any(w in low for w in ("entry level", "entry-level", "fresher", "new grad", "graduate")):
        return "Entry level", 0
    if any(w in low for w in ("senior", "principal", "staff engineer")):
        return "Senior", 5
    return "", None


def parse_job_description(text: str) -> JobRequirements:
    required_text, preferred_text = _split_buckets(text)

    required = extract_skills(required_text)
    preferred = extract_skills(preferred_text)
    # A skill named in both buckets is required; don't list it twice.
    preferred = [s for s in preferred if s not in set(required)]

    low = text.lower()
    soft = [name for name, cues in SOFT_SKILLS.items() if any(c in low for c in cues)]

    experience, min_years = _extract_experience(text)

    return JobRequirements(
        role=_extract_role(text),
        required_skills=required,
        preferred_skills=preferred,
        soft_skills=sorted(soft),
        education=_extract_education(text),
        experience=experience,
        min_years=min_years,
    )
