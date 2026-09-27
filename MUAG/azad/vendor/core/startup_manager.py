from __future__ import annotations

import importlib
import os
from typing import Any


class StartupManager:
    """Run safe AZAD startup checks without making optional services fatal."""

    def __init__(self, bot_factory: Any, voice_identity: Any, ai_engine: Any):
        self.bot_factory = bot_factory
        self.voice_identity = voice_identity
        self.ai_engine = ai_engine

    def _provider_available(self) -> bool:
        router = getattr(self.ai_engine, "router", None)
        if router is not None and getattr(router, "last_provider", None):
            return True
        try:
            import ollama  # type: ignore
            ollama.list()
            return True
        except Exception:
            return bool(os.getenv("GROQ_API_KEY", "").strip())

    def run(self) -> dict[str, Any]:
        report: dict[str, Any] = {"status": "ready", "checks": {}, "warnings": []}
        checks = report["checks"]

        try:
            importlib.import_module("bots")
            checks["bot_system"] = True
        except Exception as exc:
            checks["bot_system"] = False
            report["status"] = "degraded"
            report["warnings"].append(f"bot_system: {exc}")

        try:
            bots = self.bot_factory.list_bots()
            checks["registered_bots"] = len(bots) if hasattr(bots, "__len__") else 0
            if checks["registered_bots"] == 0:
                report["warnings"].append("No registered bots found at startup.")
        except Exception as exc:
            checks["registered_bots"] = 0
            report["status"] = "degraded"
            report["warnings"].append(f"bot_registry: {exc}")

        checks["voice_verification"] = bool(getattr(self.voice_identity, "available", False))
        checks["voice_enrolled"] = bool(
            getattr(getattr(self.voice_identity, "profile_path", None), "exists", lambda: False)()
        )
        checks["ai_provider"] = self._provider_available()
        if not checks["ai_provider"]:
            report["warnings"].append("No AI provider detected. Start Ollama or configure GROQ_API_KEY before AI chat.")

        if report["warnings"] and report["status"] == "ready":
            report["status"] = "ready_with_warnings"
        return report
