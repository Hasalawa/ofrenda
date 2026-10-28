"""Local web app: an interactive candle-lit ofrenda you can talk with.

Standard library only. Binds to 127.0.0.1, so nothing leaves your machine.
"""

from __future__ import annotations

import base64
import binascii
import json
import mimetypes
import re
import threading
import webbrowser
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path

from . import cli, llm, store, stt
from .page import PAGE

MAX_BODY = 8 * 1024 * 1024
MAX_PHOTO = 6 * 1024 * 1024
WAV_RE = re.compile(r"^data:audio/(?:x-)?wav;base64,([A-Za-z0-9+/=]+)$")
MAX_WAV = 4 * 1024 * 1024
PHOTO_RE = re.compile(r"^data:image/(png|jpeg|webp|gif);base64,([A-Za-z0-9+/=]+)$")
EXT = {"png": "png", "jpeg": "jpg", "webp": "webp", "gif": "gif"}
ALLOWED_HOSTS = {"localhost", "127.0.0.1", "[::1]"}


class ApiError(Exception):
    def __init__(self, status: int, message: str):
        super().__init__(message)
        self.status = status
        self.message = message


def _text(body: dict, key: str, limit: int, required: bool = False) -> str:
    value = str(body.get(key) or "").strip()[:limit]
    if required and not value:
        raise ApiError(400, f"{key} is required")
    return value


class App:
    def __init__(self, data_path):
        self.path = Path(data_path).resolve()
        self.base = self.path.parent
        self.lock = threading.Lock()

    # ---- helpers -------------------------------------------------------
    def photo_path(self, person: dict) -> Path | None:
        if not person.get("photo"):
            return None
        f = Path(person["photo"])
        f = f if f.is_absolute() else self.base / f
        return f if f.is_file() else None

    def public(self, person: dict) -> dict:
        out = dict(person)
        out.setdefault("relation", "")
        out.setdefault("candles", 0)
        photo = self.photo_path(person)
        out["photo_url"] = f"/media/{person['slug']}?v={int(photo.stat().st_mtime)}" if photo else ""
        return out

    def _person(self, data: dict, slug) -> dict:
        person = store.find(data, str(slug or ""))
        if not person:
            raise ApiError(404, "No one by that name on this ofrenda")
        return person

    def _save_photo(self, slug: str, data_url: str) -> str:
        match = PHOTO_RE.match(data_url or "")
        if not match:
            raise ApiError(400, "Photo must be a png, jpeg, webp or gif image")
        try:
            raw = base64.b64decode(match.group(2), validate=True)
        except (binascii.Error, ValueError):
            raise ApiError(400, "Could not read that photo") from None
        if len(raw) > MAX_PHOTO:
            raise ApiError(413, "Photo is too large")
        folder = self.base / "photos"
        folder.mkdir(parents=True, exist_ok=True)
        name = f"{slug}.{EXT[match.group(1)]}"
        (folder / name).write_bytes(raw)
        return f"photos/{name}"

    # ---- api actions ---------------------------------------------------
    def people(self) -> list[dict]:
        return [self.public(p) for p in store.load(self.path)["people"]]

    def info(self) -> dict:
        return {
            "model": llm.model_name(),
            "ai": llm.is_online(),
            "stt": stt.available(),
            "stt_model": stt.model_name(),
        }

    def warmup(self, body: dict) -> dict:
        try:
            stt.warmup()
        except stt.STTUnavailable as exc:
            raise ApiError(501, str(exc)) from None
        return {"ok": True}

    def transcribe(self, body: dict) -> dict:
        match = WAV_RE.match(str(body.get("audio") or ""))
        if not match:
            raise ApiError(400, "Send 16 kHz mono WAV audio")
        try:
            raw = base64.b64decode(match.group(1), validate=True)
        except (binascii.Error, ValueError):
            raise ApiError(400, "Could not read that audio") from None
        if len(raw) > MAX_WAV:
            raise ApiError(413, "That recording is too long")
        try:
            return {"text": stt.transcribe(raw)}
        except stt.STTUnavailable as exc:
            raise ApiError(501, str(exc)) from None
        except Exception as exc:  # noqa: BLE001 - decoding errors from the audio library
            raise ApiError(422, f"Could not understand that audio: {exc}") from None

    def add_person(self, body: dict) -> dict:
        name = _text(body, "name", 80, required=True)
        with self.lock:
            data = store.load(self.path)
            try:
                person = store.add_person(
                    data, name, _text(body, "years", 40), "", _text(body, "relation", 40)
                )
            except ValueError:
                raise ApiError(409, f"{name} is already on the ofrenda") from None
            if body.get("photo"):
                person["photo"] = self._save_photo(person["slug"], body["photo"])
            store.save(self.path, data)
            return self.public(person)

    def add_story(self, body: dict) -> dict:
        text = _text(body, "text", 5000, required=True)
        title = _text(body, "title", 120) or "A memory"
        with self.lock:
            data = store.load(self.path)
            person = self._person(data, body.get("slug"))
            store.add_story(person, title, text)
            store.save(self.path, data)
            return self.public(person)

    def add_fav(self, body: dict) -> dict:
        kind = body.get("kind")
        if kind not in ("food", "song", "flower"):
            raise ApiError(400, "kind must be food, song or flower")
        value = _text(body, "value", 80, required=True)
        with self.lock:
            data = store.load(self.path)
            person = self._person(data, body.get("slug"))
            store.add_favorite(person, kind, value)
            store.save(self.path, data)
            return self.public(person)

    def light_candle(self, body: dict) -> dict:
        with self.lock:
            data = store.load(self.path)
            person = self._person(data, body.get("slug"))
            person["candles"] = person.get("candles", 0) + 1
            store.save(self.path, data)
            return self.public(person)

    def remember(self, body: dict) -> dict:
        with self.lock:
            person = dict(self._person(store.load(self.path), body.get("slug")))
        text = cli.remember(person)  # slow: runs outside the lock
        with self.lock:
            data = store.load(self.path)
            self._person(data, body.get("slug"))["remembrance"] = text
            store.save(self.path, data)
        return {"text": text}

    def ask_stream(self, body: dict):
        """Yield the answer in pieces. Never invents: no matching story, no model call."""
        question = _text(body, "question", 500, required=True)
        with self.lock:
            person = self._person(store.load(self.path), body.get("slug"))
        history = body.get("history") if isinstance(body.get("history"), list) else None
        prompt = cli.ask_prompt(person, question, spoken=bool(body.get("spoken")), history=history)
        if prompt is None:
            yield f"I have no story about that for {person['name']} yet. Add one and ask again."
            return
        try:
            produced = False
            for piece in llm.stream(prompt, system=cli.SYSTEM):
                produced = True
                yield piece
            if not produced:
                yield "The model had nothing to say. Try asking another way."
        except llm.LLMUnavailable:
            context = prompt.split("\n\nQuestion:")[0]
            yield "(The AI model is not running, so here are the matching stories.)\n\n" + context


def make_handler(app: App):
    posts = {
        "/api/person": app.add_person,
        "/api/story": app.add_story,
        "/api/fav": app.add_fav,
        "/api/candle": app.light_candle,
        "/api/remember": app.remember,
        "/api/transcribe": app.transcribe,
        "/api/warmup": app.warmup,
    }

    class Handler(BaseHTTPRequestHandler):
        server_version = "Ofrenda"

        def log_message(self, *args):  # keep the terminal quiet
            pass

        def _host_ok(self) -> bool:
            host = (self.headers.get("Host") or "").rsplit(":", 1)[0]
            return host in ALLOWED_HOSTS

        def _send(self, status: int, body: bytes, ctype: str, extra: dict | None = None):
            self.send_response(status)
            self.send_header("Content-Type", ctype)
            self.send_header("Content-Length", str(len(body)))
            self.send_header("Cache-Control", "no-store")
            self.send_header("X-Content-Type-Options", "nosniff")
            for k, v in (extra or {}).items():
                self.send_header(k, v)
            self.end_headers()
            self.wfile.write(body)

        def _json(self, obj, status: int = 200):
            self._send(status, json.dumps(obj).encode("utf-8"), "application/json")

        def do_GET(self):
            if not self._host_ok():
                return self._json({"error": "forbidden"}, 403)
            path = self.path.split("?", 1)[0]
            try:
                if path == "/":
                    self._send(200, PAGE.encode("utf-8"), "text/html; charset=utf-8")
                elif path == "/api/people":
                    self._json(app.people())
                elif path == "/api/info":
                    self._json(app.info())
                elif path.startswith("/media/"):
                    person = app._person(store.load(app.path), path[len("/media/") :])
                    photo = app.photo_path(person)
                    if not photo:
                        raise ApiError(404, "No photo")
                    ctype = mimetypes.guess_type(photo.name)[0] or "application/octet-stream"
                    self._send(200, photo.read_bytes(), ctype)
                else:
                    raise ApiError(404, "Not found")
            except ApiError as exc:
                self._json({"error": exc.message}, exc.status)

        def do_POST(self):
            if not self._host_ok():
                return self._json({"error": "forbidden"}, 403)
            path = self.path.split("?", 1)[0]
            try:
                ctype = (self.headers.get("Content-Type") or "").split(";")[0].strip()
                if ctype != "application/json":
                    raise ApiError(415, "Send JSON")
                length = int(self.headers.get("Content-Length") or 0)
                if length > MAX_BODY:
                    raise ApiError(413, "Request too large")
                try:
                    body = json.loads(self.rfile.read(length) or b"{}")
                except json.JSONDecodeError:
                    raise ApiError(400, "Invalid JSON") from None
                if not isinstance(body, dict):
                    raise ApiError(400, "Expected a JSON object")
                if path == "/api/ask":
                    return self._stream_ask(body)
                if path not in posts:
                    raise ApiError(404, "Not found")
                self._json(posts[path](body))
            except ApiError as exc:
                self._json({"error": exc.message}, exc.status)

        def _stream_ask(self, body: dict):
            gen = app.ask_stream(body)
            try:
                first = next(gen, "")
            except ApiError as exc:
                return self._json({"error": exc.message}, exc.status)
            self.send_response(200)
            self.send_header("Content-Type", "text/plain; charset=utf-8")
            self.send_header("Cache-Control", "no-store")
            self.send_header("Connection", "close")
            self.end_headers()
            try:
                self.wfile.write(first.encode("utf-8"))
                self.wfile.flush()
                for piece in gen:
                    self.wfile.write(piece.encode("utf-8"))
                    self.wfile.flush()
            except (BrokenPipeError, ConnectionResetError):
                pass
            self.close_connection = True

    return Handler


def serve(data_path, port: int = 8765, open_browser: bool = True) -> None:
    app = App(data_path)
    try:
        httpd = ThreadingHTTPServer(("127.0.0.1", port), make_handler(app))
    except OSError as exc:
        raise SystemExit(f"Could not start on port {port}: {exc}. Try --port 8800") from exc
    url = f"http://localhost:{httpd.server_address[1]}/"
    print(f"Ofrenda is lit at {url}  (Ctrl+C to stop)")
    print(f"Your memories live in: {app.path}")
    if open_browser:
        webbrowser.open(url)
    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        print("\nGoodnight. The candles stay lit.")
    finally:
        httpd.server_close()
