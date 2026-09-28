from __future__ import annotations

from typing import Any, Optional

from agent.desktop_agent import DesktopAgent
from tools.runtime import ToolResult, ToolRuntime


class DesktopToolRuntime:
    """Expose safe, existing DesktopAgent capabilities as structured tools."""

    def __init__(self, desktop_agent: Optional[DesktopAgent] = None) -> None:
        self.agent = desktop_agent or DesktopAgent()
        self.runtime = ToolRuntime()
        self.runtime.register(
            "open_notepad",
            "Open Windows Notepad.",
            lambda args: self._dispatch("open notepad"),
            keywords=("open notepad", "notepad"),
            risk="medium",
        )
        self.runtime.register(
            "list_files",
            "List files in the current working directory.",
            lambda args: self._dispatch("list files"),
            keywords=("list files", "files", "folder"),
            risk="low",
        )

    def _dispatch(self, request: str) -> ToolResult:
        response = self.agent.handle(request)
        if response is None:
            return ToolResult(False, "desktop", error="DesktopAgent did not handle request")
        text = str(response)
        failed = text.lower().startswith(("failed", "error"))
        return ToolResult(
            success=not failed,
            tool="desktop",
            message=text,
            data=response,
            error=text if failed else None,
            metadata={"source": "DesktopAgent"},
        )

    def select(self, request: str) -> list[dict[str, Any]]:
        return [
            {
                "name": spec.name,
                "description": spec.description,
                "keywords": list(spec.keywords),
                "risk": spec.risk,
            }
            for spec in self.runtime.select(request)
        ]

    def execute(self, tool_name: str, args: Optional[dict[str, Any]] = None) -> ToolResult:
        return self.runtime.execute(tool_name, args)
