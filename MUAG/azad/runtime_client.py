#!/usr/bin/env python3
"""AZAD-side client for the MUAG local action bridge."""

from __future__ import annotations

import json
import socket

SOCKET_PATH = "/run/muag/azad.sock"


def call(action: str, **params) -> dict:
    request = {"action": action, **params}
    payload = (json.dumps(request, ensure_ascii=False) + "\n").encode("utf-8")
    with socket.socket(socket.AF_UNIX, socket.SOCK_STREAM) as sock:
        sock.settimeout(10)
        sock.connect(SOCKET_PATH)
        sock.sendall(payload)
        data = sock.recv(1024 * 1024)
    return json.loads(data.decode("utf-8"))


if __name__ == "__main__":
    import sys
    action = sys.argv[1] if len(sys.argv) > 1 else "system_status"
    print(json.dumps(call(action), ensure_ascii=False, indent=2))
