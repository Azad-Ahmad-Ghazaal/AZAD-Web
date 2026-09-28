#!/usr/bin/env python3
"""Host-side tests for the MUAG AZAD action allowlist."""

import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT, "azad"))

from muag_action_bridge import handle


assert handle({"action": "system_status"})["ok"] is True
assert handle({"action": "not_allowed"})["ok"] is False
assert handle({"action": "shutdown"})["error"] == "explicit confirmation required"
assert handle({"action": "reboot", "confirm": False})["error"] == "explicit confirmation required"
assert handle({"action": "open_path", "path": "/etc/passwd"})["ok"] is False

print("MUAG AZAD bridge tests: PASS")
