#!/usr/bin/env python3
"""Local Unix-socket service for the AZAD -> MUAG allowlisted action bridge."""

from __future__ import annotations

import json
import os
import socket
import signal

from muag_action_bridge import handle

SOCKET_PATH = "/run/muag/azad.sock"
BUFFER = 1024 * 1024

def main() -> None:
    os.makedirs(os.path.dirname(SOCKET_PATH), exist_ok=True)
    try:
        os.unlink(SOCKET_PATH)
    except FileNotFoundError:
        pass

    server = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
    server.bind(SOCKET_PATH)
    os.chmod(SOCKET_PATH, 0o660)
    server.listen(8)

    def stop(_sig, _frame):
        try:
            server.close()
        finally:
            try:
                os.unlink(SOCKET_PATH)
            except FileNotFoundError:
                pass
        raise SystemExit(0)

    signal.signal(signal.SIGTERM, stop)
    signal.signal(signal.SIGINT, stop)

    while True:
        conn, _ = server.accept()
        with conn:
            try:
                raw = conn.recv(BUFFER)
                request = json.loads(raw.decode("utf-8"))
                response = handle(request)
            except Exception as exc:
                response = {"ok": False, "error": f"invalid request: {exc}"}
            conn.sendall((json.dumps(response, ensure_ascii=False) + "\n").encode("utf-8"))

if __name__ == "__main__":
    main()
