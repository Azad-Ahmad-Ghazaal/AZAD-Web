#!/usr/bin/env python3
"""Local continuous voice loop for MUAG/AZAD.

Records short WAV chunks, transcribes with whisper-cli when available, and
hands recognized text to an optional AZAD command handler. No network access.
"""
from __future__ import annotations
import os
import shutil
import subprocess
import tempfile
import time

MODEL = os.environ.get("AZAD_WHISPER_MODEL", "/usr/share/muag/models/ggml-tiny.bin")
SECONDS = int(os.environ.get("AZAD_VOICE_SECONDS", "4"))


def record(path: str) -> bool:
    arecord = shutil.which("arecord")
    if not arecord or not os.path.isdir("/dev/snd"):
        return False
    r = subprocess.run([arecord, "-q", "-f", "S16_LE", "-r", "16000", "-c", "1", "-d", str(SECONDS), path], check=False, timeout=SECONDS + 5)
    return r.returncode == 0 and os.path.exists(path)


def transcribe(path: str) -> str:
    cli = shutil.which("whisper-cli") or shutil.which("whisper-cpp")
    if not cli or not os.path.exists(MODEL):
        return ""
    r = subprocess.run([cli, "-m", MODEL, "-f", path, "-l", "auto", "-nt", "-otxt"], capture_output=True, text=True, check=False, timeout=45)
    # whisper-cli writes transcript to stdout in common builds; ignore timing noise.
    lines = [x.strip() for x in r.stdout.splitlines() if x.strip() and not x.startswith("whisper_")]
    return " ".join(lines).strip()


def main() -> int:
    print("AZAD continuous voice: ready")
    while True:
        path = os.path.join(tempfile.gettempdir(), "azad-voice.wav")
        try:
            if record(path):
                text = transcribe(path)
                if text:
                    print("AZAD_INPUT=" + text, flush=True)
            else:
                time.sleep(2)
        except KeyboardInterrupt:
            return 0
        except Exception as exc:
            print("AZAD_VOICE_ERROR=" + str(exc), flush=True)
            time.sleep(2)
        finally:
            try:
                os.remove(path)
            except FileNotFoundError:
                pass


if __name__ == "__main__":
    raise SystemExit(main())
