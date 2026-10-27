"""Minimal client for a local Ollama server (open-weight models, no cloud)."""

from __future__ import annotations

import json
import os
import urllib.error
import urllib.request

DEFAULT_MODEL = "llama3.2:3b"
DEFAULT_HOST = "http://localhost:11434"


class LLMUnavailable(RuntimeError):
    """Raised when the local model server cannot be reached."""


def generate(
    prompt: str,
    system: str | None = None,
    model: str | None = None,
    host: str | None = None,
    timeout: float = 180,
    temperature: float = 0.4,
) -> str:
    host = (host or os.environ.get("OLLAMA_HOST") or DEFAULT_HOST).rstrip("/")
    if not host.startswith("http"):
        host = "http://" + host
    body = {
        "model": model or os.environ.get("OFRENDA_MODEL", DEFAULT_MODEL),
        "prompt": prompt,
        "stream": False,
        "options": {"temperature": temperature},
    }
    if system:
        body["system"] = system
    req = urllib.request.Request(
        f"{host}/api/generate",
        data=json.dumps(body).encode("utf-8"),
        headers={"Content-Type": "application/json"},
    )
    try:
        with urllib.request.urlopen(req, timeout=timeout) as resp:
            payload = json.loads(resp.read().decode("utf-8"))
    except (urllib.error.URLError, TimeoutError, ConnectionError, OSError) as exc:
        raise LLMUnavailable(f"Could not reach Ollama at {host}: {exc}") from exc
    except json.JSONDecodeError as exc:
        raise LLMUnavailable(f"Bad response from Ollama: {exc}") from exc
    return str(payload.get("response", "")).strip()
