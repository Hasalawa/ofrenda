"""Tiny keyword retrieval so the model only sees the stories that matter."""

from __future__ import annotations

import re

STOP = {
    "the", "and", "for", "was", "were", "with", "that", "this", "from", "have", "had", "has",
    "his", "her", "she", "him", "they", "them", "what", "when", "where", "who", "how", "why",
    "did", "does", "you", "your", "are", "about", "tell",
}  # fmt: skip


def _stem(word: str) -> str:
    """Very small suffix stripper: fished/fishing/fishes -> fish."""
    for suffix in ("ing", "ed", "es", "s"):
        if word.endswith(suffix) and len(word) - len(suffix) >= 3:
            return word[: -len(suffix)]
    return word


def tokens(text: str) -> set[str]:
    return {
        _stem(w) for w in re.findall(r"[\w']+", text.lower()) if len(w) > 2 and w not in STOP
    }


def top_stories(person: dict, question: str, k: int = 3) -> list[dict]:
    q = tokens(question)
    scored = []
    for story in person["stories"]:
        score = len(q & tokens(story["title"] + " " + story["text"]))
        if score:
            scored.append((score, story))
    scored.sort(key=lambda s: -s[0])
    return [s for _, s in scored[:k]]
