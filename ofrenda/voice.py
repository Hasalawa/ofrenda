"""Optional offline text-to-speech (pip install 'ofrenda[voice]')."""

from __future__ import annotations


def speak(text: str, rate: int = 150) -> None:
    try:
        import pyttsx3
    except ImportError:
        raise SystemExit("Install the voice extra: pip install -e \".[voice]\"") from None
    engine = pyttsx3.init()
    engine.setProperty("rate", rate)
    engine.say(text)
    engine.runAndWait()
