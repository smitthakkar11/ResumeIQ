"""Dictionary-based skill extraction.

Runs on lightly-normalised text (lowercased, whitespace collapsed) so that
C++, C#, .NET and Node.js are still intact when we look for them.
"""

import functools
import json
import re
from dataclasses import dataclass
from pathlib import Path

SKILLS_FILE = Path(__file__).parent / "skills.json"

# Boundaries. A dot must only block when it is INSIDE a longer term
# ("node" in "node.js"), never when it just ends a sentence ("Python.").
# `-` is deliberately absent so "c-programming" and "react-router" still match.
LEFT = r"(?<![a-z0-9+#])(?<![a-z0-9]\.)"
RIGHT = r"(?![a-z0-9+#])(?!\.[a-z0-9])"


@dataclass(frozen=True, order=True)
class Skill:
    category: str
    name: str


@functools.lru_cache(maxsize=1)
def _compiled() -> list[tuple[Skill, re.Pattern[str]]]:
    """One regex per skill, matching any of its spellings. Built once."""
    entries = json.loads(SKILLS_FILE.read_text())["skills"]
    compiled = []

    for entry in entries:
        terms = list(entry["aliases"])
        if entry.get("match_name", True):
            terms.append(entry["name"])

        # Longest first, so "react js" is tried before "react".
        alternatives = "|".join(
            re.escape(t.lower()) for t in sorted(set(terms), key=len, reverse=True)
        )
        pattern = re.compile(rf"{LEFT}(?:{alternatives}){RIGHT}")
        compiled.append((Skill(entry["category"], entry["name"]), pattern))

    return compiled


def all_skills() -> list[Skill]:
    return sorted(skill for skill, _ in _compiled())


def extract_skills(text: str) -> list[Skill]:
    """Return the distinct skills mentioned in `text`, sorted by category."""
    haystack = " ".join(text.lower().split())
    return sorted(skill for skill, pattern in _compiled() if pattern.search(haystack))


def count_skills(text: str) -> dict[str, int]:
    """How many times each skill is mentioned — used for emphasis hints."""
    haystack = " ".join(text.lower().split())
    counts = {}
    for skill, pattern in _compiled():
        found = len(pattern.findall(haystack))
        if found:
            counts[skill.name] = found
    return counts
