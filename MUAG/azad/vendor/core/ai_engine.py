"""AZAD AI engine with provider routing and broad, safety-aware knowledge mode."""

from __future__ import annotations

import ast
import operator
import os
import re

from core.provider_router import ProviderRouter


class AIEngine:
    def __init__(self, model: str = "qwen2.5:3b", *args, **kwargs):
        self.model = model
        self.router = ProviderRouter(ollama_model=model)
        self.last_provider_available = False
        self.last_provider = None
        # "full" means AZAD should understand difficult/sensitive subjects instead of
        # pretending they do not exist. It does not disable execution safeguards.
        self.knowledge_mode = os.getenv("AZAD_KNOWLEDGE_MODE", "full").strip().lower() or "full"

    def set_model(self, model: str) -> str:
        """Switch AZAD's active local Ollama model for future requests."""
        model = str(model).strip()
        if not model:
            raise ValueError("model name is required")
        self.model = model
        self.router.ollama_model = model
        return self.model

    @staticmethod
    def _safe_calculate(expression: str) -> float | int | None:
        """Evaluate only simple arithmetic; never execute arbitrary Python."""
        allowed = {
            ast.Add: operator.add, ast.Sub: operator.sub, ast.Mult: operator.mul,
            ast.Div: operator.truediv, ast.FloorDiv: operator.floordiv,
            ast.Mod: operator.mod, ast.Pow: operator.pow, ast.USub: operator.neg,
            ast.UAdd: operator.pos,
        }

        def evaluate(node):
            if isinstance(node, ast.Expression):
                return evaluate(node.body)
            if isinstance(node, ast.Constant) and isinstance(node.value, (int, float)):
                if abs(node.value) > 10**12:
                    raise ValueError
                return node.value
            if isinstance(node, ast.UnaryOp) and type(node.op) in allowed:
                return allowed[type(node.op)](evaluate(node.operand))
            if isinstance(node, ast.BinOp) and type(node.op) in allowed:
                left, right = evaluate(node.left), evaluate(node.right)
                if isinstance(node.op, ast.Pow) and abs(right) > 20:
                    raise ValueError
                return allowed[type(node.op)](left, right)
            raise ValueError

        try:
            tree = ast.parse(expression, mode="eval")
            return evaluate(tree)
        except (SyntaxError, ValueError, TypeError, ZeroDivisionError, OverflowError):
            return None

    @staticmethod
    def _offline_response(prompt: str) -> str | None:
        """Answer deterministic local requests without pretending to be an LLM."""
        text = re.sub(r"\s+", " ", str(prompt).strip().lower())
        if not text:
            return "Please enter a message."

        greetings = ("hi", "hello", "hey", "assalam-o-alaikum", "assalamualaikum", "salam", "aoa", "السلام علیکم", "سلام")
        if text in greetings or text.rstrip("!.") in greetings:
            return "Wa Alaikum Assalam, Uzair. Main AZAD hoon. Mera owner Uzair hai."

        identity_terms = ("your name", "who are you", "what is your name", "tumhara naam", "apna naam", "aap ka naam", "تمہارا نام", "آپ کا نام", "کون ہو")
        owner_terms = ("your owner", "owner", "mera owner", "mere liye owner", "تمہارا owner", "آپ کا مالک", "مالک کون")
        if any(term in text for term in identity_terms):
            return "Main AZAD hoon, Uzair ka personal AI assistant."
        if any(term in text for term in owner_terms):
            return "Mera owner Uzair hai."

        expression = text
        for phrase in ("kitna hota hai", "kitna hai", "kya hai", "calculate", "calculate karo", "what is", "what's", "equals", "=", "کا جواب", "کتنا ہے", "کتنا ہوگا"):
            expression = expression.replace(phrase, " ")
        expression = expression.replace("×", "*").replace("÷", "/")
        expression = re.sub(r"\bplus\b", "+", expression)
        expression = re.sub(r"\bminus\b", "-", expression)
        expression = re.sub(r"\btimes\b", "*", expression)
        expression = re.sub(r"\bdivided by\b", "/", expression)
        expression = re.sub(r"\s+", " ", expression).strip()
        if re.fullmatch(r"[0-9+\-*/%.() ]+", expression):
            result = AIEngine._safe_calculate(expression)
            if result is not None:
                return f"Uzair, jawab {result:g} hai."
        return None

    def _build_system_prompt(self, system_prompt: str | None = None) -> str:
        base = system_prompt or (
            "You are AZAD, Uzair's personal AI assistant. "
            "Reply naturally in Urdu, English, or Roman Urdu. "
            "You understand software, cybersecurity, networking, firewalls, privacy, "
            "system administration, research, poetry, writing and personal-assistant tasks. "
            "Treat sensitive or difficult subjects as legitimate topics to understand and explain. "
            "For cybersecurity, distinguish defensive education and authorized administration "
            "from unauthorized access or harmful real-world actions. "
            "Do not claim that a subject is unknown merely because it is sensitive. "
            "Never expose secrets or credentials and never take consequential system actions "
            "without the required authorization."
        )
        if self.knowledge_mode == "full":
            base += " Maintain broad subject-matter awareness, including sensitive topics, while preserving action and safety boundaries."
        return base

    def ask(self, prompt: str, system_prompt: str | None = None, **kwargs) -> str:
        system = self._build_system_prompt(system_prompt)
        result = self.router.ask(prompt, system=system)
        self.last_provider_available = result is not None
        self.last_provider = self.router.last_provider
        if result:
            return result
        offline = self._offline_response(prompt)
        if offline:
            return offline
        return (
            "Uzair, abhi koi external/local AI reasoning provider available nahi hai. "
            "AZAD Core, local skills aur bots phir bhi available hain. "
            "Complex AI reasoning ke liye Ollama ya Groq provider configure karna hoga."
        )

    def chat(self, prompt: str, system_prompt: str | None = None, **kwargs) -> str:
        return self.ask(prompt, system_prompt=system_prompt, **kwargs)
