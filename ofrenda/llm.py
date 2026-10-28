"""Minimal client for a local Ollama server (open-weight models, no cloud)."""

from __future__ import annotations

import json
import os
import urllib.error
import urllib.request
from collections.abc import Iterator

DEFAULT_MODEL = "llama3.2:3b"
DEFAULT_HOST = "http://localhost:11434"


class LLMUnavailable(RuntimeError):
    """Raised when the local model server cannot be reached."""


def model_name() -> str:
    return os.environ.get("OFRENDA_MODEL", DEFAULT_MODEL)


def _host(host: str | None = None) -> str:
    host = (host or os.environ.get("OLLAMA_HOST") or DEFAULT_HOST).rstrip("/")
    return host if host.startswith("http") else "http://" + host


def _request(prompt, system, model, host, temperature, stream) -> urllib.request.Request:
    body = {
        "model": model or model_name(),
        "prompt": prompt,
        "stream": stream,
        "options": {"temperature": temperature},
    }
    if system:
        body["system"] = system
    return urllib.request.Request(
        f"{_host(host)}/api/generate",
        data=json.dumps(body).encode("utf-8"),
        headers={"Content-Type": "application/json"},
    )


def generate(
    prompt: str,
    system: str | None = None,
    model: str | None = None,
    host: str | None = None,
    timeout: float = 180,
    temperature: float = 0.4,
) -> str:
    req = _request(prompt, system, model, host, temperature, stream=False)
    try:
        with urllib.request.urlopen(req, timeout=timeout) as resp:
            payload = json.loads(resp.read().decode("utf-8"))
    except (urllib.error.URLError, TimeoutError, ConnectionError, OSError) as exc:
        raise LLMUnavailable(f"Could not reach Ollama at {_host(host)}: {exc}") from exc
    except json.JSONDecodeError as exc:
        raise LLMUnavailable(f"Bad response from Ollama: {exc}") from exc
    return str(payload.get("response", "")).strip()


def stream(
    prompt: str,
    system: str | None = None,
    model: str | None = None,
    host: str | None = None,
    timeout: float = 180,
    temperature: float = 0.4,
) -> Iterator[str]:
    """Yield the answer piece by piece as the model produces it."""
    req = _request(prompt, system, model, host, temperature, stream=True)
    try:
        with urllib.request.urlopen(req, timeout=timeout) as resp:
            for line in resp:
                if not line.strip():
                    continue
                obj = json.loads(line.decode("utf-8"))
                if obj.get("response"):
                    yield obj["response"]
                if obj.get("done"):
                    break
    except (urllib.error.URLError, TimeoutError, ConnectionError, OSError) as exc:
        raise LLMUnavailable(f"Could not reach Ollama at {_host(host)}: {exc}") from exc
    except json.JSONDecodeError as exc:
        raise LLMUnavailable(f"Bad response from Ollama: {exc}") from exc


def is_online(host: str | None = None) -> bool:
    try:
        with urllib.request.urlopen(f"{_host(host)}/api/tags", timeout=1.5):
            return True
    except (urllib.error.URLError, TimeoutError, ConnectionError, OSError):
        return False
