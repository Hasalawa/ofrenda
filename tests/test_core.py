import json
from pathlib import Path

import pytest

from ofrenda import cli, llm, retrieve, store
from ofrenda.render import render_html

ROOT = Path(__file__).resolve().parent.parent


@pytest.fixture
def demo():
    return json.loads((ROOT / "examples" / "demo.json").read_text(encoding="utf-8"))


def test_slug_and_roundtrip(tmp_path):
    f = tmp_path / "d.json"
    data = store.load(f)
    p = store.add_person(data, "José Luis", "1930-2001")
    store.add_story(p, "Guitar", "He played every Sunday.")
    store.add_favorite(p, "song", "La Llorona")
    store.save(f, data)
    again = store.load(f)
    assert store.find(again, "jose luis") is None  # accents are not folded
    assert store.find(again, "José Luis")["favorites"]["songs"] == ["La Llorona"]


def test_duplicate_person_rejected():
    data = {"people": []}
    store.add_person(data, "Ana")
    with pytest.raises(ValueError):
        store.add_person(data, "ana")


def test_retrieval_picks_relevant_story(demo):
    person = demo["people"][0]
    hits = retrieve.top_stories(person, "Why did the mole burn?")
    assert hits and hits[0]["title"] == "The night the mole burned"
    assert retrieve.top_stories(person, "quantum chromodynamics") == []


def test_render_escapes_html(demo):
    demo["people"][0]["name"] = "<script>alert(1)</script>"
    html = render_html(demo)
    assert "<script>alert(1)</script>" not in html
    assert "&lt;script&gt;" in html


def test_cli_works_without_model(tmp_path, monkeypatch, capsys):
    def boom(*a, **k):
        raise llm.LLMUnavailable("offline")

    monkeypatch.setattr(llm, "generate", boom)
    f = str(tmp_path / "o.json")
    assert cli.main(["--data", f, "add-person", "Tío Beto", "--years", "1950-2020"]) == 0
    cli.main(["--data", f, "add-story", "Tío Beto", "--title", "Fishing", "--text", "He fished at dawn."])
    cli.main(["--data", f, "add-fav", "Tío Beto", "food", "tamales"])
    cli.main(["--data", f, "remember", "Tío Beto"])
    assert "Tío Beto" in capsys.readouterr().out
    cli.main(["--data", f, "ask", "Tío Beto", "when did he fish"])
    assert "He fished at dawn." in capsys.readouterr().out
    out = tmp_path / "o.html"
    cli.main(["--data", f, "build", "--out", str(out)])
    assert "tamales" in out.read_text(encoding="utf-8")


def test_ask_uses_model_with_retrieved_context(demo, monkeypatch):
    seen = {}

    def fake(prompt, system=None, **k):
        seen["prompt"], seen["system"] = prompt, system
        return "She laughed and started again."

    monkeypatch.setattr(llm, "generate", fake)
    answer = cli.ask(demo["people"][0], "what happened with the mole")
    assert answer == "She laughed and started again."
    assert "forgot the chocolate" in seen["prompt"]
    assert "Never speak as the person" in seen["system"]


def test_ask_unknown_topic_does_not_hallucinate(demo, monkeypatch):
    monkeypatch.setattr(llm, "generate", lambda *a, **k: pytest.fail("model must not be called"))
    assert "No story about that" in cli.ask(demo["people"][0], "stock market")
