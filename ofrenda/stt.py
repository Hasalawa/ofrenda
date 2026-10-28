"""Offline speech-to-text for voice calls, using Whisper via faster-whisper.

Audio is transcribed on your own machine. The model is downloaded once (about 150 MB for the
default `base.en`) and then works with no internet.
"""

from __future__ import annotations

import importlib.util
import io
import os
import threading

_model = None
_lock = threading.Lock()


class STTUnavailable(RuntimeError):
    """Raised when speech-to-text cannot be used (not installed, or model missing)."""


def available() -> bool:
    return importlib.util.find_spec("faster_whisper") is not None


def model_name() -> str:
    return os.environ.get("OFRENDA_STT_MODEL", "base.en")


def _load():
    global _model
    with _lock:
        if _model is None:
            if not available():
                raise STTUnavailable("Voice calls need Whisper. Run: pip install faster-whisper")
            from faster_whisper import WhisperModel

            try:
                _model = WhisperModel(model_name(), device="cpu", compute_type="int8")
            except Exception as exc:
                raise STTUnavailable(
                    f"Could not load the speech model '{model_name()}'. "
                    f"The first run needs internet once to download it. ({exc})"
                ) from exc
    return _model


def warmup() -> None:
    _load()


def transcribe(wav: bytes) -> str:
    """Turn 16 kHz mono WAV bytes into text. Returns '' when nothing was said."""
    model = _load()
    segments, _ = model.transcribe(
        io.BytesIO(wav),
        language="en",
        beam_size=1,
        vad_filter=True,
        condition_on_previous_text=False,
    )
    return " ".join(s.text.strip() for s in segments if s.no_speech_prob < 0.6).strip()
