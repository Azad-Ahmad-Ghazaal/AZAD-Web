#!/usr/bin/env python3
"""Small allowlisted bridge between AZAD and MUAG OS services."""

from __future__ import annotations
import json, os, subprocess, sys


def _run(argv):
    return subprocess.run(argv, check=False, capture_output=True, text=True, timeout=15)


def handle(request):
    action = str(request.get("action", "")).strip().lower()
    if action == "system_status":
        return {"ok": True, "action": action, "result": _run(["uname", "-a"]).stdout.strip()}
    if action == "open_terminal":
        for cmd in (["xterm"], ["sh", "-lc", "command -v xterm"]):
            r = _run(cmd)
            if r.returncode == 0:
                return {"ok": True, "action": action}
        return {"ok": False, "error": "terminal unavailable"}
    if action == "open_browser":
        for browser in ("chromium", "chromium-browser", "google-chrome", "firefox"):
            r = _run(["sh", "-lc", f"command -v {browser}"])
            if r.returncode == 0:
                subprocess.Popen([browser], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
                return {"ok": True, "action": action, "browser": browser}
        return {"ok": False, "error": "browser unavailable"}
    if action == "open_path":
        path = os.path.abspath(str(request.get("path", "")))
        home = os.path.expanduser("~")
        if not (path == home or path.startswith(home + os.sep)):
            return {"ok": False, "error": "path outside user area"}
        return {"ok": True, "action": action, "path": path}
    if action in {"shutdown", "reboot"}:
        if request.get("confirm") is not True:
            return {"ok": False, "error": "explicit confirmation required"}
        cmd = "poweroff" if action == "shutdown" else "reboot"
        r = _run(["sh", "-lc", f"command -v {cmd}"])
        return {"ok": r.returncode == 0, "action": action}
    return {"ok": False, "error": "action not allowlisted"}


if __name__ == "__main__":
    print(json.dumps(handle(json.loads(sys.stdin.read())), ensure_ascii=False))
