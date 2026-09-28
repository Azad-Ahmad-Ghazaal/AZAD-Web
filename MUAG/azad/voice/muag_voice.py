#!/usr/bin/env python3
"""Local microphone -> Whisper STT -> text handoff for AZAD."""
from __future__ import annotations
import os, shutil, subprocess
from typing import Optional

STT = "/usr/bin/whisper-cli"
MODEL = "/usr/share/muag/models/ggml-tiny.bin"
TTS = ("espeak-ng", "espeak")

def microphone_device() -> Optional[str]:
    return "/dev/snd" if os.path.isdir("/dev/snd") else None

def speak(text: str) -> bool:
    text = str(text).strip()
    if not text: return False
    for name in TTS:
        exe = shutil.which(name)
        if exe:
            subprocess.Popen([exe, text], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
            return True
    return False

def record_audio(path="/tmp/azad-input.wav", seconds=5) -> bool:
    exe = shutil.which("arecord")
    if not exe or not microphone_device(): return False
    r = subprocess.run([exe, "-q", "-f", "S16_LE", "-r", "16000", "-c", "1", "-d", str(seconds), path], check=False, timeout=seconds+5)
    return r.returncode == 0 and os.path.exists(path)

def transcribe(path="/tmp/azad-input.wav") -> Optional[str]:
    if not os.path.exists(STT) or not os.path.exists(MODEL) or not os.path.exists(path): return None
    r = subprocess.run([STT, "-m", MODEL, "-f", path, "-nt", "-otxt"], capture_output=True, text=True, check=False, timeout=120)
    txt = path + ".txt"
    if os.path.exists(txt):
        value = open(txt, encoding="utf-8", errors="replace").read().strip()
        os.unlink(txt)
        return value or None
    return r.stdout.strip() or None

def listen_once(seconds=5) -> Optional[str]:
    path="/tmp/azad-input.wav"
    if not record_audio(path, seconds): return None
    return transcribe(path)

def main() -> int:
    print("AZAD voice: mic=%s stt=%s model=%s" % ("yes" if microphone_device() else "no", os.path.exists(STT), os.path.exists(MODEL)))
    if microphone_device() and os.path.exists(STT) and os.path.exists(MODEL):
        text = listen_once(5)
        if text:
            print(text)
            speak("I heard you.")
    return 0

if __name__ == "__main__": raise SystemExit(main())
