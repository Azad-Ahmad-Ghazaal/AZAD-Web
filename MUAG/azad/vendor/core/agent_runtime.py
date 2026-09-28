from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Iterable, Optional
import re

from bots.base import BotContext
from bots.orchestrator import BotOrchestrator
from bots.registry import BotRegistry
from bots.auto_router import AutoBotRouter
from tools.desktop_runtime import DesktopToolRuntime


@dataclass
class AgentPlan:
    """Small, inspectable plan produced before AZAD executes a request."""
    intent: str
    steps: list[str] = field(default_factory=list)
    requires_bot: bool = True
    confidence: float = 0.0

    def to_dict(self) -> dict[str, Any]:
        return {
            "intent": self.intent,
            "steps": list(self.steps),
            "requires_bot": self.requires_bot,
            "confidence": self.confidence,
        }


class AZADAgentRuntime:
    """Autonomous execution layer for Bots, Desktop tools and optional MCP tools."""

    def __init__(
        self,
        registry: Optional[BotRegistry] = None,
        orchestrator: Optional[BotOrchestrator] = None,
        router: Optional[AutoBotRouter] = None,
        desktop_runtime: Optional[DesktopToolRuntime] = None,
        mcp_runtime: Any = None,
    ) -> None:
        self.registry = registry or BotRegistry()
        self.orchestrator = orchestrator or BotOrchestrator(self.registry)
        self.router = router or AutoBotRouter(self.registry)
        self.desktop_runtime = desktop_runtime
        self.mcp_runtime = mcp_runtime

    def _desktop_tools(self, request: str) -> list[dict[str, Any]]:
        if self.desktop_runtime is None:
            return []
        try:
            return self.desktop_runtime.select(request)
        except Exception:
            return []

    def _mcp_tools(self, request: str) -> list[dict[str, Any]]:
        if self.mcp_runtime is None:
            return []
        try:
            text = (request or "").lower()
            matches = []
            for tool in self.mcp_runtime.discover():
                haystack = " ".join(str(tool.get(k, "")) for k in ("name", "description", "tool")).lower()
                score = sum(1 for token in re.findall(r"[a-z0-9_]+", text) if token in haystack)
                if score:
                    matches.append((score, tool))
            matches.sort(key=lambda item: (-item[0], item[1].get("name", "")))
            return [item[1] for item in matches[:5]]
        except Exception:
            return []

    def _select_tool(self, request: str) -> Optional[dict[str, Any]]:
        desktop = self._desktop_tools(request)
        if desktop:
            return {**desktop[0], "source": "desktop"}
        mcp = self._mcp_tools(request)
        if mcp:
            return {**mcp[0], "source": "mcp"}
        return None

    def inspect(self, request: str) -> AgentPlan:
        text = (request or "").strip().lower()
        if not text:
            return AgentPlan("empty_request", [], False, 1.0)

        selected_tool = self._select_tool(request)
        if selected_tool:
            return AgentPlan(
                f"{selected_tool['source']}_tool",
                [f"execute_tool:{selected_tool['name']}", "verify"],
                False,
                0.95,
            )

        intent_rules = (
            ("research", ("research", "find sources", "investigate", "researcher")),
            ("code", ("code", "python", "program", "debug", "fix bug", "build")),
            ("file", ("file", "folder", "read file", "write file", "document")),
            ("note", ("note", "remember this", "save this")),
            ("calculator", ("calculate", "calculator", "compute", "how much is")),
        )
        for intent, keywords in intent_rules:
            if any(keyword in text for keyword in keywords):
                return AgentPlan(intent, [f"route_to_{intent}"], True, 0.85)
        if re.search(r"\b(then|after that|next|and then)\b", text):
            return AgentPlan("multi_step", ["split_steps", "execute_in_order", "verify"], True, 0.65)
        return AgentPlan("general", ["inspect_available_bots", "execute_best_match", "verify"], True, 0.35)

    @staticmethod
    def _split_steps(request: str) -> list[str]:
        parts = re.split(r"\s+(?:then|after that|next|and then)\s+", request, flags=re.I)
        return [part.strip(" .") for part in parts if part.strip(" .")]

    def plan(self, request: str) -> AgentPlan:
        plan = self.inspect(request)
        if plan.intent == "multi_step":
            return AgentPlan(plan.intent, self._split_steps(request) or plan.steps, True, plan.confidence)
        return plan

    def _execute_tool(self, request: str, context: BotContext) -> Optional[dict[str, Any]]:
        selected = self._select_tool(request)
        if not selected:
            return None
        try:
            if selected.get("source") == "desktop" and self.desktop_runtime is not None:
                result = self.desktop_runtime.execute(selected["name"])
            elif selected.get("source") == "mcp" and self.mcp_runtime is not None:
                result = self.mcp_runtime.execute_request(request, selected)
            else:
                return None
            payload = result.to_dict()
            payload["tool_name"] = selected["name"]
            payload["tool_source"] = selected["source"]
            payload["context_task_id"] = context.task_id
            context.history.append(payload)
            if result.data is not None:
                context.data[selected["name"]] = result.data
            return payload
        except Exception as exc:
            return {
                "success": False,
                "tool": selected["name"],
                "tool_name": selected["name"],
                "tool_source": selected["source"],
                "error": str(exc),
                "context_task_id": context.task_id,
            }

    def execute(self, request: str, context: Optional[BotContext] = None) -> dict[str, Any]:
        request = (request or "").strip()
        context = context or BotContext(user_request=request)
        plan = self.plan(request)
        if not request:
            return self._response(False, plan, context, error="empty_request")

        if plan.intent in {"desktop_tool", "mcp_tool"}:
            tool_result = self._execute_tool(request, context)
            if tool_result is None:
                return self._response(False, plan, context, error="tool_not_available")
            return self._response(
                bool(tool_result.get("success")),
                plan,
                context,
                results=[tool_result],
                data=tool_result.get("data"),
                error=tool_result.get("error"),
            )

        if plan.intent == "multi_step":
            results = []
            for step in plan.steps:
                tool_result = self._execute_tool(step, context)
                if tool_result is not None:
                    results.append(tool_result)
                    if not tool_result.get("success"):
                        return self._response(False, plan, context, error=tool_result.get("error") or "step_failed", results=results, failed_step=step)
                    continue
                result = self.router.route(step, context=context)
                results.append(result.to_dict())
                if not result.success:
                    return self._response(False, plan, context, error=result.error or "step_failed", results=results, failed_step=step)
            return self._response(True, plan, context, results=results, data=context.data)

        result = self.router.route(request, context=context)
        return self._response(result.success, plan, context, results=[result.to_dict()], data=result.data, error=result.error)

    def execute_chain(self, bot_ids: Iterable[str], request: str, context: Optional[BotContext] = None) -> dict[str, Any]:
        context = context or BotContext(user_request=request)
        plan = self.plan(request)
        result = self.orchestrator.execute_chain(bot_ids, request, context)
        result["plan"] = plan.to_dict()
        result["verified"] = self.verify(result)
        return result

    def verify(self, response: dict[str, Any]) -> bool:
        if not isinstance(response, dict) or not response.get("success") or not response.get("plan"):
            return False
        results = response.get("results", [])
        if not results or not isinstance(results, list):
            return False
        return all(isinstance(item, dict) and item.get("success") is True for item in results)

    @staticmethod
    def _response(success: bool, plan: AgentPlan, context: BotContext, **extra: Any) -> dict[str, Any]:
        payload = {
            "success": success,
            "task_id": context.task_id,
            "plan": plan.to_dict(),
            "history": list(context.history),
        }
        payload.update(extra)
        payload["verified"] = AZADAgentRuntime._verified_payload(payload)
        return payload

    @staticmethod
    def _verified_payload(payload: dict[str, Any]) -> bool:
        if not payload.get("success") or not payload.get("results"):
            return False
        return all(isinstance(item, dict) and item.get("success") is True for item in payload["results"])
