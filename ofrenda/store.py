"""Tiny JSON-file store. Everything stays on the user's own disk."""

from __future__ import annotations

import json
import os
import re
import tempfile
from datetime import date
from pathlib import Path


def slugify(name: str) -> str:
    return re.sub(r"[^a-z0-9]+", "-", name.lower()).strip("-") or "person"


def load(path: str | os.PathLike) -> dict:
    p = Path(path)
    if not p.exists():
        return {"people": []}
    return json.loads(p.read_text(encoding="utf-8"))


def save(path: str | os.PathLike, data: dict) -> None:
    p = Path(path)
    p.parent.mkdir(parents=True, exist_ok=True)
    fd, tmp = tempfile.mkstemp(dir=p.parent, suffix=".tmp")
    with os.fdopen(fd, "w", encoding="utf-8") as fh:
        json.dump(data, fh, indent=2, ensure_ascii=False)
    os.replace(tmp, p)


def find(data: dict, name: str) -> dict | None:
    slug = slugify(name)
    for person in data["people"]:
        if person["slug"] == slug:
            return person
    return None


def add_person(
    data: dict, name: str, years: str = "", photo: str = "", relation: str = ""
) -> dict:
    if find(data, name):
        raise ValueError(f"{name!r} already exists")
    person = {
        "slug": slugify(name),
        "name": name,
        "years": years,
        "relation": relation,
        "photo": photo,
        "candles": 0,
        "favorites": {"foods": [], "songs": [], "flowers": []},
        "stories": [],
        "remembrance": "",
    }
    data["people"].append(person)
    return person


def add_story(person: dict, title: str, text: str) -> dict:
    story = {"title": title, "text": text.strip(), "added": date.today().isoformat()}
    person["stories"].append(story)
    return story


def add_favorite(person: dict, kind: str, value: str) -> None:
    key = {"food": "foods", "song": "songs", "flower": "flowers"}.get(kind, kind)
    if key not in person["favorites"]:
        raise ValueError("kind must be food, song or flower")
    person["favorites"][key].append(value)
