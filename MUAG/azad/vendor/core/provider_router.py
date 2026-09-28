"""Optional AI provider routing for AZAD.

Local callers can use this router without depending on a specific provider.
"""

from __future__ import annotations

import os
from typing import Any


class ProviderRouter:
    """Try configured providers in a safe order and return a normalized result."""

    def __init__(self, ollama_model: str | None = None) -> None:
        self.ollama_model = ollama_model or os.getenv("OLLAMA_MODEL", "qwen2.5:3b")
        self.last_provider: str | None = None

    def ask(self, prompt: str, system: str = "") -> str | None:
        self.last_provider = None

        # Ollama is optional and deliberately imported lazily.
        try:
            import ollama  # type: ignore

            messages: list[dict[str, str]] = []
            if system:
                messages.append({"role": "system", "content": system})
            messages.append({"role": "user", "content": prompt})
            result: Any = ollama.chat(model=self.ollama_model, messages=messages)
            message = result.get("message", {}) if isinstance(result, dict) else getattr(result, "message", {})
            content = message.get("content") if isinstance(message, dict) else getattr(message, "content", None)
            if content:
                self.last_provider = "ollama"
                return str(content).strip()
        except Exception:
            pass

        # Groq is optional and only used when explicitly configured.
        api_key = os.getenv("GROQ_API_KEY")
        if api_key:
            try:
                from groq import Groq  # type: ignore

                client = Groq(api_key=api_key)
                response = client.chat.completions.create(
                    model=os.getenv("GROQ_MODEL", "llama-3.1-8b-instant"),
                    messages=([{"role": "system", "content": system}] if system else [])
                    + [{"role": "user", "content": prompt}],
                    temperature=0.2,
                )
                content = response.choices[0].message.content
                if content:
                    self.last_provider = "groq"
                    return str(content).strip()
            except Exception:
                pass

        return None
