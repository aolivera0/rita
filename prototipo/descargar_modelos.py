"""Descarga la voz de Piper y el modelo de Whisper en ./modelos (unos 300 MB con Whisper base)."""

import os
import subprocess
import sys
from pathlib import Path

RAIZ = Path(__file__).resolve().parent
VOZ = os.environ.get("PIPER_VOICE", "es_MX-claude-high")
WHISPER = os.environ.get("WHISPER_MODEL", "base")

(RAIZ / "modelos" / "voces").mkdir(parents=True, exist_ok=True)
subprocess.run([sys.executable, "-m", "piper.download_voices", "--download-dir",
                str(RAIZ / "modelos" / "voces"), VOZ], check=True)

from faster_whisper import WhisperModel  # noqa: E402

WhisperModel(WHISPER, device="cpu", compute_type="int8",
             download_root=str(RAIZ / "modelos" / "whisper"))
print(f"Listo: voz {VOZ} y Whisper {WHISPER} en {RAIZ / 'modelos'}")
