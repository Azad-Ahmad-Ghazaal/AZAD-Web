#!/usr/bin/env python3
"""Allowlisted AZAD -> MUAG runtime action bridge.

This is the only supported runtime control surface for AZAD.
"""

from __future__ import annotations

import json
import os
import shutil
import subprocess
import sys


def _run(argv: list[str], timeout: int = 15) -> subprocess.CompletedProcess[str]:
    return subprocess.run(argv, check=False, capture_output=True, text=True, timeout=timeout)


def handle(request: dict) -> dict:
    action = str(request.get("action", "")).strip().lower()

    if action == "system_status":
        r = _run(["uname", "-a"])
        return {"ok": r.returncode == 0, "action": action, "result": r.stdout.strip()}

    if action == "open_terminal":
        terminal = shutil.which("xterm")
        if not terminal:
            return {"ok": False, "error": "terminal unavailable"}
        subprocess.Popen([terminal], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        return {"ok": True, "action": action}

    if action == "open_browser":
        for name in ("chromium", "chromium-browser", "google-chrome", "firefox"):
            browser = shutil.which(name)
            if browser:
                subprocess.Popen([browser], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
                return {"ok": True, "action": action, "browser": name}
        return {"ok": False, "error": "browser unavailable"}

    if action == "open_path":
        path = os.path.abspath(str(request.get("path", "")))
        home = os.path.expanduser("~")
        if not (path == home or path.startswith(home + os.sep)):
            return {"ok": False, "error": "path outside user area"}
        if not os.path.exists(path):
            return {"ok": False, "error": "path does not exist"}
        return {"ok": True, "action": action, "path": path}

    if action in {"shutdown", "reboot"}:
        if request.get("confirm") is not True:
            return {"ok": False, "error": "explicit confirmation required"}
        cmd = "poweroff" if action == "shutdown" else "reboot"
        executable = shutil.which(cmd)
        if not executable:
            return {"ok": False, "error": f"{cmd} unavailable"}
        subprocess.Popen([executable], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        return {"ok": True, "action": action}

    return {"ok": False, "error": "action not allowlisted"}


if __name__ == "__main__":
    try:
        request = json.loads(sys.stdin.read())
        print(json.dumps(handle(request), ensure_ascii=False))
    except Exception as exc:
        print(json.dumps({"ok": False, "error": str(exc)}, ensure_ascii=False))
        raise SystemExit(1)
