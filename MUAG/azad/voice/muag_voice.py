#!/usr/bin/env python3
"""Lightweight MUAG voice loop scaffold for AZAD.

Uses available system tools when present. No network calls are made here.
"""

from __future__ import annotations
import os
import shutil
import subprocess

def speak(text: str) -> bool:
    for cmd in ("espeak-ng", "espeak"):
        if shutil.which(cmd):
            subprocess.Popen([cmd, text], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
            return True
    return False

def microphone_device() -> str | None:
    path="/dev/snd"
    if os.path.isdir(path):
        return path
    return None

def main() -> int:
    print("AZAD voice runtime: microphone=%s" % ("available" if microphone_device() else "not-detected"))
    speak("AZAD voice runtime is ready.")
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
