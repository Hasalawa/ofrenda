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


def test_transcribe_endpoint(base, monkeypatch):
    from ofrenda import stt

    monkeypatch.setattr(stt, "transcribe", lambda wav: "hello " + str(len(wav)))
    audio = "data:audio/wav;base64,AAAA"
    assert call(base + "/api/transcribe", {"audio": audio}) == (200, '{"text": "hello 3"}')
    assert call(base + "/api/transcribe", {"audio": "nope"})[0] == 400


def test_transcribe_reports_missing_whisper(base, monkeypatch):
    from ofrenda import stt

    def missing(wav):
        raise stt.STTUnavailable("Voice calls need Whisper. Run: pip install faster-whisper")

    monkeypatch.setattr(stt, "transcribe", missing)
    s, b = call(base + "/api/transcribe", {"audio": "data:audio/wav;base64,AAAA"})
    assert s == 501 and "faster-whisper" in b


def test_spoken_prompt_is_short_and_follow_ups_keep_context():
    from ofrenda import cli

    person = json.loads(DEMO.read_text(encoding="utf-8"))["people"][0]
    first = cli.ask_prompt(person, "what happened with the mole", spoken=True)
    assert "phone call" in first and "three short sentences" in first
    history = [{"who": "me", "text": "what happened with the mole"}, {"who": "ai", "text": "It burned."}]
    follow = cli.ask_prompt(person, "and then?", history=history)
    assert follow and "forgot the chocolate" in follow and "Companion: It burned." in follow
    assert cli.ask_prompt(person, "stock market") is None


def test_wav_decoding_does_not_need_pyav():
    np = pytest.importorskip("numpy")
    import io
    import wave

    from ofrenda import stt

    buf = io.BytesIO()
    with wave.open(buf, "wb") as f:
        f.setnchannels(1)
        f.setsampwidth(2)
        f.setframerate(16000)
        f.writeframes(np.array([0, 16384, -16384], dtype="<i2").tobytes())
    out = stt.wav_to_array(buf.getvalue())
    assert out.dtype == np.float32 and out.tolist() == [0.0, 0.5, -0.5]
    with pytest.raises(ValueError):
        stt.wav_to_array(b"RIFF....not a wav")
