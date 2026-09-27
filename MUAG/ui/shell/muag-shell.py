#!/usr/bin/env python3
"""MUAG desktop shell prototype.

Runs the local HTML shell in the first available lightweight browser.
The final image can replace this launcher with a native shell without
changing the shell UI contract.
"""
import os
import shutil
import subprocess
import sys

HTML = "/usr/share/muag/shell/index.html"

BROWSERS = [
    "chromium",
    "chromium-browser",
    "google-chrome",
    "firefox",
]

def main():
    browser = next((shutil.which(x) for x in BROWSERS), None)
    if not browser:
        print("MUAG shell: no graphical browser runtime installed.")
        print("Install Chromium for the current prototype.")
        return 1

    env = os.environ.copy()
    env.setdefault("XDG_RUNTIME_DIR", "/tmp/muag-runtime")
    os.makedirs(env["XDG_RUNTIME_DIR"], mode=0o700, exist_ok=True)

    args = [
        browser,
        "--kiosk",
        "--no-first-run",
        "--disable-session-crashed-bubble",
        "--disable-infobars",
        f"file://{HTML}",
    ]

    try:
        return subprocess.call(args, env=env)
    except KeyboardInterrupt:
        return 0

if __name__ == "__main__":
    sys.exit(main())
