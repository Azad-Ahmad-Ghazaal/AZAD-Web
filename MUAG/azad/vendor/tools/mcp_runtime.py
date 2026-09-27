from __future__ import annotations

from typing import Any, Optional
import re

from tools.desktop_runtime import DesktopToolRuntime
from tools.runtime import ToolResult


class MCPToolRuntime:
    """Optional runtime for configured MCP servers.

    MCP SDK loading remains lazy through the existing adapter, so importing
    this module does not make MCP a hard dependency of AZAD.
    """

    def __init__(self, client: Any, servers: Optional[list[str]] = None) -> None:
        self.client = client
        self.servers = servers

    def discover(self) -> list[dict[str, Any]]:
        specs = []
        for server in self.servers or list(getattr(self.client, "server_configs", {})):
            for item in self.client.list_tools(server):
                if item.get("name"):
                    specs.append({
                        "name": f"{server}__{item['name']}",
                        "server": server,
                        "tool": item["name"],
                        "description": item.get("description") or "",
                        "inputSchema": item.get("inputSchema"),
                    })
        return specs

    @staticmethod
    def build_arguments(request: str, spec: dict[str, Any]) -> dict[str, Any]:
        """Extract safe arguments from natural-language requests using the tool schema."""
        schema = spec.get("inputSchema") or {}
        properties = schema.get("properties") or {}
        required = set(schema.get("required") or [])
        text = (request or "").strip()
        args: dict[str, Any] = {}
        url_match = re.search(r"https?://[^\\s<>\"']+", text)
        for name, definition in properties.items():
            kind = str(definition.get("type", ""))
            lowered = name.lower()
            if lowered == "url" and url_match:
                args[name] = url_match.group(0).rstrip(".,);")
            elif lowered in {"text", "value"}:
                quoted = re.search(r"[\"']([^\"']+)[\"']", text)
                if quoted:
                    args[name] = quoted.group(1)
            elif lowered in {"target", "element", "ref"}:
                ref = re.search(r"\\b(?:e|f|ref)[-_]?\\d+\\b", text, re.I)
                if ref:
                    args[name] = ref.group(0)
            elif kind == "boolean" and re.search(r"\\b(?:submit|confirm|yes)\\b", text, re.I):
                args[name] = True
            elif kind in {"integer", "number"}:
                number = re.search(r"\\b\\d+(?:\\.\\d+)?\\b", text)
                if number:
                    args[name] = int(number.group(0)) if kind == "integer" else float(number.group(0))
        missing = [name for name in required if name not in args]
        if missing:
            raise ValueError(f"MCP tool requires arguments: {', '.join(sorted(missing))}")
        return args

    def execute_request(self, request: str, tool: dict[str, Any]) -> ToolResult:
        args = self.build_arguments(request, tool)
        return self.execute(tool["name"], args)

    def execute(self, qualified_name: str, args: Optional[dict[str, Any]] = None) -> ToolResult:
        if "__" not in qualified_name:
            return ToolResult(False, qualified_name, error="MCP tool must use server__tool naming")
        server, tool = qualified_name.split("__", 1)
        result = self.client.invoke_tool(server_name=server, tool_name=tool, arguments=args or {})
        failed = bool(result.get("isError", False))
        return ToolResult(
            success=not failed,
            tool=qualified_name,
            message=result.get("text") or "",
            data=result,
            error=result.get("text") if failed else None,
            metadata={"source": "mcp", "server": server},
        )
