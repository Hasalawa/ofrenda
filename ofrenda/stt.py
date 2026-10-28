"""Offline speech-to-text for voice calls, using Whisper via faster-whisper.

Audio is transcribed on your own machine. The model is downloaded once (about 150 MB for the
default `base.en`) and then works with no internet.
"""

from __future__ import annotations

import importlib.util
import io
import os
import threading
import wave

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


def wav_to_array(wav: bytes):
    """Decode our own 16 kHz mono 16-bit WAV with the standard library.

    Whisper can then take a plain float array, so we never depend on the audio decoder (PyAV)
    that ships with faster-whisper, whose version differs between computers.
    """
    import numpy as np

    try:
        with wave.open(io.BytesIO(wav), "rb") as f:
            if (f.getnchannels(), f.getsampwidth(), f.getframerate()) != (1, 2, 16000):
                raise ValueError("expected 16 kHz mono 16-bit WAV")
            frames = f.readframes(f.getnframes())
    except (wave.Error, EOFError) as exc:
        raise ValueError(f"not a valid WAV file: {exc}") from exc
    return np.frombuffer(frames, dtype=np.int16).astype(np.float32) / 32768.0


def transcribe(wav: bytes) -> str:
    """Turn 16 kHz mono WAV bytes into text. Returns '' when nothing was said."""
    audio = wav_to_array(wav)
    model = _load()
    segments, _ = model.transcribe(
        audio,
        language="en",
        beam_size=1,
        vad_filter=True,
        condition_on_previous_text=False,
    )
    return " ".join(s.text.strip() for s in segments if s.no_speech_prob < 0.6).strip()
