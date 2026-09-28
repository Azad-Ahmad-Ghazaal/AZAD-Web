from __future__ import annotations

from typing import Any, Optional

from bots.base import BotContext
from bots.native_ai import NativeAIBot
from bots.registry import BotRegistry
from core.agent_runtime import AZADAgentRuntime
from tools.desktop_runtime import DesktopToolRuntime
from tools.mcp_client import MCPClientManager
from tools.mcp_runtime import MCPToolRuntime


class AZADAgentGateway:
    """Stable integration point for Brain/API/UI layers with tool + memory execution."""

    def __init__(
        self,
        runtime: Optional[AZADAgentRuntime] = None,
        registry: Optional[BotRegistry] = None,
        memory: Any = None,
        ai_engine: Any = None,
        desktop_runtime: Optional[DesktopToolRuntime] = None,
        mcp_runtime: Any = None,
        mcp_config: Optional[str] = None,
    ) -> None:
        if runtime is not None:
            self.runtime = runtime
        else:
            active_registry = registry or BotRegistry()
            if ai_engine is not None and active_registry.get("native_ai") is None:
                active_registry.register(NativeAIBot(ai_engine))
            if mcp_runtime is None and mcp_config:
                mcp_runtime = MCPToolRuntime(MCPClientManager.from_file(mcp_config))
            self.runtime = AZADAgentRuntime(
                registry=active_registry,
                desktop_runtime=desktop_runtime or DesktopToolRuntime(),
                mcp_runtime=mcp_runtime,
            )
        self.memory = memory

    def handle(self, request: str, context: Optional[BotContext] = None) -> dict[str, Any]:
        request = (request or "").strip()
        if not request:
            return {"success": False, "message": "Request is empty.", "results": [], "plan": {}}
        context = context or BotContext(user_request=request)
        if self.memory is not None:
            try:
                context.data["memory"] = self._memory_snapshot(request)
            except Exception as exc:
                context.data["memory_error"] = str(exc)
        result = self.runtime.execute(request, context=context)
        if self.memory is not None and result.get("success"):
            try:
                self.memory.save(f"agent_task:{context.task_id}", {
                    "request": request,
                    "intent": result.get("plan", {}).get("intent"),
                    "success": True,
                    "bot_results": [
                        {"bot_id": item.get("bot_id"), "message": item.get("message")}
                        for item in result.get("results", []) if isinstance(item, dict)
                    ],
                })
            except Exception as exc:
                result.setdefault("warnings", []).append(f"memory_save_failed: {exc}")
        return result

    def inspect(self, request: str) -> dict[str, Any]:
        return self.runtime.plan(request).to_dict()

    def available_bots(self) -> list[dict[str, Any]]:
        return self.runtime.registry.list()

    def _memory_snapshot(self, request: str) -> dict[str, Any]:
        if not self.memory:
            return {}
        data = {}
        for key in ("user_name", "user", "preferences", "current_project", "azad_mode"):
            value = self.memory.remember(key)
            if value != "I don't remember this.":
                data[key] = value
        data["request"] = request
        return data
