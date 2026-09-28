#!/usr/bin/env python3
"""Lightweight local voice runtime for AZAD inside MUAG.

This layer intentionally owns device discovery and TTS only. STT is loaded
through a local command when available; it never performs a network call.
"""

from __future__ import annotations

import os
import shutil
import subprocess
from typing import Optional


STT_COMMANDS = ("whisper", "whisper-cpp", "whisper-cli")
TTS_COMMANDS = ("espeak-ng", "espeak")


def microphone_device() -> Optional[str]:
    if os.path.isdir("/dev/snd"):
        return "/dev/snd"
    return None


def speak(text: str) -> bool:
    text = str(text).strip()
    if not text:
        return False
    for cmd in TTS_COMMANDS:
        executable = shutil.which(cmd)
        if executable:
            subprocess.Popen(
                [executable, text],
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL,
            )
            return True
    return False


def find_stt() -> Optional[str]:
    for cmd in STT_COMMANDS:
        executable = shutil.which(cmd)
        if executable:
            return executable
    return None


def record_audio(output: str = "/tmp/azad-input.wav", seconds: int = 5) -> bool:
    """Record a short local sample with ALSA when arecord is available."""
    arecord = shutil.which("arecord")
    if not arecord or not microphone_device():
        return False
    result = subprocess.run(
        [arecord, "-q", "-f", "S16_LE", "-r", "16000", "-c", "1", "-d", str(seconds), output],
        check=False,
        timeout=seconds + 5,
    )
    return result.returncode == 0 and os.path.exists(output)


def main() -> int:
    mic = microphone_device()
    stt = find_stt()
    print("AZAD voice runtime")
    print("microphone=%s" % ("available" if mic else "not-detected"))
    print("stt=%s" % (stt or "not-installed"))
    print("tts=%s" % next((x for x in TTS_COMMANDS if shutil.which(x)), "not-installed"))
    if mic:
        speak("AZAD voice runtime is ready.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
