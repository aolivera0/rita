"""Voz a texto (faster-whisper) y texto a voz (Piper), los dos en CPU."""

from __future__ import annotations

import io
import os
import threading
import wave
from pathlib import Path

RAIZ = Path(__file__).resolve().parent.parent
MODELOS = RAIZ / "modelos"

WHISPER = os.environ.get("WHISPER_MODEL", "base")
VOZ = os.environ.get("PIPER_VOICE", "es_MX-claude-high")
# Contexto para Whisper: mejora la puntuación y frases típicas de una llamada.
CONTEXTO = ("Llamada telefónica en español de Colombia. Buenas tardes, le habla Andrea, "
            "de la empresa. Lo llamo para...")

_lock = threading.Lock()
_whisper = None
_piper = None


def _modelo_whisper():
    global _whisper
    if _whisper is None:
        from faster_whisper import WhisperModel
        _whisper = WhisperModel(WHISPER, device="cpu", compute_type="int8",
                                download_root=str(MODELOS / "whisper"))
    return _whisper


def _voz_piper():
    global _piper
    if _piper is None:
        from piper import PiperVoice
        _piper = PiperVoice.load(str(MODELOS / "voces" / f"{VOZ}.onnx"))
    return _piper


def precargar() -> None:
    _modelo_whisper()
    _voz_piper()


def transcribir(audio: bytes) -> str:
    """Recibe un WAV (o cualquier formato que entienda ffmpeg) y devuelve el texto."""
    with _lock:
        segmentos, _ = _modelo_whisper().transcribe(
            io.BytesIO(audio), language="es", beam_size=1, vad_filter=True,
            condition_on_previous_text=False, initial_prompt=CONTEXTO,
        )
        return " ".join(s.text.strip() for s in segmentos).strip()


def sintetizar(texto: str) -> bytes:
    """Devuelve un WAV con la frase dicha por la voz de Rita."""
    buf = io.BytesIO()
    with _lock, wave.open(buf, "wb") as w:
        _voz_piper().synthesize_wav(texto, w)
    return buf.getvalue()
