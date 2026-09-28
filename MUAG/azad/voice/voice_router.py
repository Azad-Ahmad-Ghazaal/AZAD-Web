#!/usr/bin/env python3
"""Minimal local voice-to-AZAD router.

Maps only a small, explicit command vocabulary to the MUAG runtime bridge.
Unknown speech is returned to AZAD as text instead of being executed.
"""
from __future__ import annotations

import json
import os
import subprocess
import sys

from runtime_client import call


def route(text: str) -> dict:
    t = " ".join(text.lower().strip().split())
    if not t:
        return {"ok": False, "error": "empty speech"}
    if any(x in t for x in ("browser kholo", "browser open", "open browser", "chrome kholo", "chrome open")):
        return call("open_browser")
    if any(x in t for x in ("terminal kholo", "terminal open", "open terminal")):
        return call("open_terminal")
    if any(x in t for x in ("system status", "system check", "system ki halat")):
        return call("system_status")
    return {"ok": True, "action": "azad_text", "text": text}


if __name__ == "__main__":
    text = " ".join(sys.argv[1:])
    print(json.dumps(route(text), ensure_ascii=False))
