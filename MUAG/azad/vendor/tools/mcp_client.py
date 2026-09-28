from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Any, Optional
import json
import subprocess


@dataclass(frozen=True)
class MCPServerConfig:
    name: str
    command: str
    args: tuple[str, ...] = ()
    cwd: Optional[str] = None
    env: Optional[dict[str, str]] = None


class MCPClientManager:
    """Minimal JSON-RPC stdio MCP manager with lazy server sessions.

    The transport is deliberately isolated from AZAD's tool runtime. A server
    is started only when first used; no process is spawned during import.
    """

    def __init__(self, configs: Optional[dict[str, MCPServerConfig]] = None) -> None:
        self.server_configs = configs or {}
        self._sessions: dict[str, Any] = {}

    @classmethod
    def from_file(cls, path: str | Path) -> "MCPClientManager":
        raw = json.loads(Path(path).read_text(encoding="utf-8"))
        configs: dict[str, MCPServerConfig] = {}
        for name, item in raw.get("mcpServers", raw.get("servers", {})).items():
            if not item.get("command"):
                continue
            configs[name] = MCPServerConfig(
                name=name,
                command=str(item["command"]),
                args=tuple(str(x) for x in item.get("args", [])),
                cwd=item.get("cwd"),
                env={str(k): str(v) for k, v in item.get("env", {}).items()} or None,
            )
        return cls(configs)

    def _start(self, server_name: str):
        if server_name in self._sessions:
            return self._sessions[server_name]
        config = self.server_configs.get(server_name)
        if config is None:
            raise KeyError(f"Unknown MCP server: {server_name}")
        import os
        env = os.environ.copy()
        if config.env:
            env.update(config.env)
        process = subprocess.Popen(
            [config.command, *config.args],
            cwd=config.cwd,
            env=env,
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            stderr=subprocess.DEVNULL,
            text=True,
            bufsize=1,
        )
        self._sessions[server_name] = process
        self._request(server_name, "initialize", {
            "protocolVersion": "2025-06-18",
            "capabilities": {},
            "clientInfo": {"name": "AZAD", "version": "1.0"},
        })
        self._notify(server_name, "notifications/initialized", {})
        return process

    def _request(self, server_name: str, method: str, params: dict[str, Any]) -> Any:
        process = self._sessions.get(server_name)
        if process is None:
            process = self._start(server_name)
        if process.stdin is None or process.stdout is None:
            raise RuntimeError("MCP stdio session is unavailable")
        request_id = getattr(process, "_azad_request_id", 0) + 1
        setattr(process, "_azad_request_id", request_id)
        payload = {"jsonrpc": "2.0", "id": request_id, "method": method, "params": params}
        process.stdin.write(json.dumps(payload) + "\n")
        process.stdin.flush()
        while True:
            line = process.stdout.readline()
            if not line:
                raise RuntimeError(f"MCP server {server_name} closed stdout")
            message = json.loads(line)
            if message.get("id") != request_id:
                continue
            if "error" in message:
                raise RuntimeError(str(message["error"]))
            return message.get("result", {})

    def _notify(self, server_name: str, method: str, params: dict[str, Any]) -> None:
        process = self._sessions[server_name]
        process.stdin.write(json.dumps({"jsonrpc": "2.0", "method": method, "params": params}) + "\n")
        process.stdin.flush()

    def list_tools(self, server_name: str) -> list[dict[str, Any]]:
        result = self._request(server_name, "tools/list", {})
        return list(result.get("tools", []))

    def invoke_tool(self, server_name: str, tool_name: str, arguments: dict[str, Any]) -> dict[str, Any]:
        result = self._request(server_name, "tools/call", {"name": tool_name, "arguments": arguments})
        content = result.get("content", [])
        text = "\n".join(item.get("text", "") for item in content if isinstance(item, dict))
        return {"isError": bool(result.get("isError", False)), "text": text, "result": result}

    def close(self) -> None:
        for process in self._sessions.values():
            try:
                process.terminate()
            except Exception:
                pass
        self._sessions.clear()
