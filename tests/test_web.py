import json
import threading
import urllib.error
import urllib.request
from http.server import ThreadingHTTPServer
from pathlib import Path

import pytest

from ofrenda import llm
from ofrenda.web import App, make_handler

DEMO = Path(__file__).resolve().parent.parent / "examples" / "demo.json"


@pytest.fixture
def base(tmp_path, monkeypatch):
    (tmp_path / "o.json").write_text(DEMO.read_text(encoding="utf-8"), encoding="utf-8")
    monkeypatch.setattr(llm, "is_online", lambda *a, **k: False)
    httpd = ThreadingHTTPServer(("127.0.0.1", 0), make_handler(App(tmp_path / "o.json")))
    threading.Thread(target=httpd.serve_forever, daemon=True).start()
    yield f"http://127.0.0.1:{httpd.server_address[1]}"
    httpd.shutdown()
    httpd.server_close()


def call(url, body=None, headers=None):
    data = json.dumps(body).encode() if body is not None else None
    h = {"Content-Type": "application/json", **(headers or {})}
    req = urllib.request.Request(url, data=data, headers=h)
    try:
        with urllib.request.urlopen(req) as r:
            return r.status, r.read().decode()
    except urllib.error.HTTPError as e:
        return e.code, e.read().decode()


def test_page_and_people(base):
    status, html = call(base + "/")
    assert status == 200 and "Ofrenda" in html
    status, body = call(base + "/api/people")
    assert json.loads(body)[0]["slug"] == "abuela-rosa"


def test_add_person_story_and_candle(base):
    s, b = call(base + "/api/person", {"name": "Seeya", "relation": "grandfather"})
    assert s == 200 and json.loads(b)["relation"] == "grandfather"
    s, _ = call(base + "/api/person", {"name": "seeya"})
    assert s == 409
    s, b = call(base + "/api/story", {"slug": "seeya", "title": "Dawn", "text": "He walked."})
    assert json.loads(b)["stories"][0]["title"] == "Dawn"
    s, b = call(base + "/api/candle", {"slug": "seeya"})
    assert json.loads(b)["candles"] == 1


def test_ask_streams_grounded_answer(base, monkeypatch):
    monkeypatch.setattr(llm, "stream", lambda *a, **k: iter(["She ", "laughed."]))
    s, b = call(base + "/api/ask", {"slug": "abuela-rosa", "question": "why did the mole burn"})
    assert (s, b) == (200, "She laughed.")


def test_ask_without_matching_story_never_calls_model(base, monkeypatch):
    def boom(*a, **k):
        raise AssertionError("model must not be called")

    monkeypatch.setattr(llm, "stream", boom)
    s, b = call(base + "/api/ask", {"slug": "abuela-rosa", "question": "stock market"})
    assert s == 200 and "no story about that" in b.lower()


def test_ask_when_ai_offline_falls_back_to_stories(base, monkeypatch):
    def down(*a, **k):
        raise llm.LLMUnavailable("offline")
        yield  # pragma: no cover

    monkeypatch.setattr(llm, "stream", down)
    s, b = call(base + "/api/ask", {"slug": "abuela-rosa", "question": "mole chocolate"})
    assert s == 200 and "forgot the chocolate" in b


def test_rejects_foreign_host_and_bad_input(base):
    s, _ = call(base + "/api/people", headers={"Host": "evil.example"})
    assert s == 403
    assert call(base + "/api/person", {"name": ""})[0] == 400
    assert call(base + "/api/person", {"name": "X", "photo": "data:text/html;base64,AAA"})[0] == 400
    assert call(base + "/api/story", {"slug": "nobody", "text": "x"})[0] == 404
