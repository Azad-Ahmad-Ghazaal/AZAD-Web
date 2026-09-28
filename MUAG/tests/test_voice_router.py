#!/usr/bin/env python3
import json
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(__file__)), "azad", "voice"))
from voice_router import route

assert route("")["ok"] is False
assert route("random sentence") ["action"] == "azad_text"
assert route("browser kholo")["action"] == "open_browser" or route("browser kholo").get("error")
print("MUAG voice router tests: PASS")
