from __future__ import annotations

from collections import deque
from dataclasses import dataclass
from time import time
from typing import Optional
import re


@dataclass(frozen=True)
class TranscriptSegment:
    text: str
    started_at: float
    ended_at: float
    from_assistant: bool = False


class TranscriptBuffer:
    """Rolling short-term speech context used by AZAD's conversation layer."""

    def __init__(self, duration_seconds: float = 120.0) -> None:
        self.duration_seconds = max(10.0, float(duration_seconds))
        self._items: deque[TranscriptSegment] = deque()

    def add(self, text: str, *, from_assistant: bool = False) -> None:
        text = (text or "").strip()
        if not text:
            return
        now = time()
        self._items.append(TranscriptSegment(text, now, now, from_assistant))
        self.prune(now)

    def prune(self, now: Optional[float] = None) -> None:
        now = time() if now is None else now
        cutoff = now - self.duration_seconds
        while self._items and self._items[0].ended_at < cutoff:
            self._items.popleft()

    def recent(self, seconds: Optional[float] = None) -> list[TranscriptSegment]:
        self.prune()
        if seconds is None:
            return list(self._items)
        cutoff = time() - max(0.0, seconds)
        return [item for item in self._items if item.ended_at >= cutoff]

    def text(self, seconds: Optional[float] = None) -> str:
        return "\n".join(item.text for item in self.recent(seconds))

    def clear(self) -> None:
        self._items.clear()


class WakeWordDetector:
    """AZAD wake-word detector; user-facing identity is always AZAD."""

    def __init__(self, wake_words: tuple[str, ...] = ("azad", "آزاد")) -> None:
        self.wake_words = tuple(
            word.lower().strip() for word in wake_words if word.strip()
        )

    def detect(self, text: str) -> bool:
        value = (text or "").lower()
        return any(
            re.search(rf"(?<!\w){re.escape(word)}(?!\w)", value)
            for word in self.wake_words
        )

    def strip_wake_word(self, text: str) -> str:
        value = (text or "").strip()
        for word in self.wake_words:
            value = re.sub(
                rf"(?i)\b{re.escape(word)}\b[,،:\s-]*",
                "",
                value,
                count=1,
            ).strip()
        return value


class AZADListeningRuntime:
    """Transcript-first voice context for the AZAD core.

    This layer intentionally owns only short-term listening state. Long-term
    memory remains in AZAD Memory, while execution remains in AZAD agents,
    bots, desktop tools and MCP runtime.
    """

    def __init__(self, duration_seconds: float = 120.0) -> None:
        self.buffer = TranscriptBuffer(duration_seconds)
        self.wake = WakeWordDetector()

    def add_user_text(self, text: str) -> None:
        self.buffer.add(text)

    def add_assistant_text(self, text: str) -> None:
        self.buffer.add(text, from_assistant=True)

    def resolve_request(self, text: str) -> str:
        text = (text or "").strip()
        if not text:
            return ""
        cleaned = self.wake.strip_wake_word(text) if self.wake.detect(text) else text
        return cleaned.strip() or text

    def should_respond(self, text: str) -> bool:
        return bool((text or "").strip())

    def build_context(self, current_text: str) -> str:
        current_text = (current_text or "").strip()
        previous = self.buffer.text(seconds=self.buffer.duration_seconds)
        if previous == current_text:
            previous = ""
        if not previous:
            return current_text
        return f"Recent conversation:\n{previous}\n\nCurrent request:\n{current_text}"

    def record_turn(self, user_text: str, assistant_text: str = "") -> None:
        self.add_user_text(user_text)
        if assistant_text:
            self.add_assistant_text(assistant_text)


__all__ = [
    "TranscriptSegment",
    "TranscriptBuffer",
    "WakeWordDetector",
    "AZADListeningRuntime",
]
