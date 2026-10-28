"""Command line interface for Ofrenda."""

from __future__ import annotations

import argparse
import os
import sys
from pathlib import Path

from . import __version__, llm, retrieve, store, voice
from .render import render_html

SYSTEM = (
    "You help a family remember someone they love. Use ONLY the facts and stories "
    "provided. Never invent details. Never speak as the person who has passed; always "
    "speak about them with warmth and respect. Always reply in English. Refer to them by "
    "name or by the relationship given; if no relationship is given, do not guess one."
)


def _facts(person: dict) -> str:
    fav = person["favorites"]
    lines = [f"Name: {person['name']}", f"Years: {person.get('years') or 'unknown'}"]
    if person.get("relation"):
        lines.append(f"Relationship to the family: {person['relation']}")
    for key, label in (("foods", "Favorite foods"), ("songs", "Favorite songs"),
                       ("flowers", "Favorite flowers")):
        if fav.get(key):
            lines.append(f"{label}: {', '.join(fav[key])}")
    for s in person["stories"]:
        lines.append(f"Story '{s['title']}': {s['text']}")
    return "\n".join(lines)


def remember(person: dict) -> str:
    """Write a short remembrance. Falls back to a template if no model is running."""
    prompt = (
        "Write a warm remembrance of 120 to 160 words for an ofrenda, in prose, "
        f"using only these facts:\n\n{_facts(person)}"
    )
    try:
        text = llm.generate(prompt, system=SYSTEM)
        if text:
            return text
    except llm.LLMUnavailable:
        pass
    name = person["name"]
    bits = [f"We remember {name}."]
    if person["stories"]:
        bits.append(f"They live on in stories like “{person['stories'][0]['title']}”.")
    fav = person["favorites"]
    if fav.get("foods"):
        bits.append(f"Today there is {fav['foods'][0]} on the table for them.")
    return " ".join(bits)


def _recent(history) -> list[tuple[str, str]]:
    out = []
    for item in history or []:
        if isinstance(item, dict) and item.get("who") in ("me", "ai"):
            out.append((item["who"], str(item.get("text", ""))[:400]))
    return out[-6:]


def ask_prompt(person: dict, question: str, spoken: bool = False, history=None) -> str | None:
    """Build the grounded prompt, or None when no story is relevant."""
    recent = _recent(history)
    last_q = next((t for who, t in reversed(recent) if who == "me"), "")
    hits = retrieve.top_stories(person, question)
    if last_q and (not hits or not retrieve.tokens(question)):
        hits = retrieve.top_stories(person, last_q) or hits  # a follow-up like "and then?"
    if not hits:
        return None
    context = "\n\n".join(f"{s['title']}: {s['text']}" for s in hits)
    relation = f" ({person['relation']})" if person.get("relation") else ""
    chat = ""
    if recent:
        lines = [("Visitor" if who == "me" else "Companion") + ": " + t for who, t in recent]
        chat = "Conversation so far:\n" + "\n".join(lines) + "\n\n"
    style = (
        "\nReply as if speaking aloud on a phone call: warm and natural, at most three short "
        "sentences, no lists, no markdown."
        if spoken
        else ""
    )
    return (
        f"Stories about {person['name']}{relation}:\n\n{context}\n\n{chat}Question: {question}\n"
        f"Answer using only these stories. If they do not answer it, say so.{style}"
    )


def ask(person: dict, question: str) -> str:
    """Answer a question strictly from the stored stories."""
    prompt = ask_prompt(person, question)
    if prompt is None:
        return f"No story about that has been written down for {person['name']} yet."
    try:
        text = llm.generate(prompt, system=SYSTEM)
        if text:
            return text
    except llm.LLMUnavailable:
        pass
    return "(model offline, showing matching stories)\n\n" + prompt.split("\n\nQuestion:")[0]


def _need(data: dict, name: str) -> dict:
    person = store.find(data, name)
    if not person:
        raise SystemExit(f"No one named {name!r}. Add them with: ofrenda add-person")
    return person


def build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(prog="ofrenda", description=__doc__)
    p.add_argument("--data", default=os.environ.get("OFRENDA_DATA", "ofrenda.json"))
    p.add_argument("--version", action="version", version=__version__)
    sub = p.add_subparsers(dest="cmd", required=True)

    a = sub.add_parser("add-person")
    a.add_argument("name")
    a.add_argument("--years", default="")
    a.add_argument("--photo", default="")
    a.add_argument("--relation", default="", help="e.g. grandfather, mother, friend")

    a = sub.add_parser("add-story")
    a.add_argument("name")
    a.add_argument("--title", required=True)
    a.add_argument("--text", help="story text (reads stdin if omitted)")

    a = sub.add_parser("add-fav")
    a.add_argument("name")
    a.add_argument("kind", choices=["food", "song", "flower"])
    a.add_argument("value")

    a = sub.add_parser("transcribe", help="turn a recorded family story into text (offline)")
    a.add_argument("name")
    a.add_argument("audio")
    a.add_argument("--title", required=True)

    a = sub.add_parser("remember")
    a.add_argument("name")
    a.add_argument("--speak", action="store_true", help="read the result aloud (offline)")

    a = sub.add_parser("ask")
    a.add_argument("name")
    a.add_argument("question")
    a.add_argument("--speak", action="store_true", help="read the answer aloud (offline)")

    a = sub.add_parser("serve", help="open the interactive ofrenda in your browser")
    a.add_argument("--port", type=int, default=8765)
    a.add_argument("--no-open", action="store_true")

    a = sub.add_parser("build")
    a.add_argument("--out", default="ofrenda.html")
    a.add_argument("--title", default="Ofrenda")
    return p


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    data = store.load(args.data)

    if args.cmd == "add-person":
        store.add_person(data, args.name, args.years, args.photo, args.relation)
    elif args.cmd == "add-story":
        text = args.text if args.text is not None else sys.stdin.read()
        store.add_story(_need(data, args.name), args.title, text)
    elif args.cmd == "add-fav":
        store.add_favorite(_need(data, args.name), args.kind, args.value)
    elif args.cmd == "transcribe":
        try:
            from faster_whisper import WhisperModel
        except ImportError:
            raise SystemExit("Install the audio extra: pip install 'ofrenda[audio]'")
        model = WhisperModel("small", device="cpu", compute_type="int8")
        segments, _ = model.transcribe(args.audio)
        text = " ".join(seg.text.strip() for seg in segments)
        store.add_story(_need(data, args.name), args.title, text)
        print(text)
    elif args.cmd == "remember":
        person = _need(data, args.name)
        person["remembrance"] = remember(person)
        print(person["remembrance"])
        if args.speak:
            voice.speak(person["remembrance"])
    elif args.cmd == "ask":
        answer = ask(_need(data, args.name), args.question)
        print(answer)
        if args.speak:
            voice.speak(answer)
        return 0
    elif args.cmd == "serve":
        from .web import serve

        serve(args.data, args.port, open_browser=not args.no_open)
        return 0
    elif args.cmd == "build":
        base = Path(args.data).resolve().parent
        Path(args.out).write_text(render_html(data, base, args.title), encoding="utf-8")
        print(f"Wrote {args.out}")
        return 0

    store.save(args.data, data)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
