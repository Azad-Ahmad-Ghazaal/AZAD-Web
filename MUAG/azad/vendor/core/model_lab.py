"""AZAD Model Lab: privacy-first experience collection and dataset preparation.

This module does not train a foundation model by itself. It creates a clean,
versionable stream of AZAD experiences that a future trainer can use.
Raw credentials and common secret-shaped values are redacted before persistence.
Only explicitly verified successful experiences enter the training dataset.
"""
from __future__ import annotations

import json
import os
import time
from dataclasses import asdict, dataclass
from typing import Any

from core.privacy import redact_sensitive


@dataclass
class Experience:
    request: str
    response: str
    success: bool
    verified: bool
    source: str = "azad"
    tool: str | None = None
    category: str = "general"
    feedback: str | None = None
    created_at: float = 0.0

    def normalized(self) -> dict[str, Any]:
        data = asdict(self)
        data["request"] = redact_sensitive(data["request"])
        data["response"] = redact_sensitive(data["response"])
        data["source"] = redact_sensitive(str(data["source"]))
        if data["tool"]:
            data["tool"] = redact_sensitive(str(data["tool"]))
        if data["feedback"]:
            data["feedback"] = redact_sensitive(str(data["feedback"]))
        return data


class AZADModelLab:
    """Collect candidate experiences and build a verified training dataset."""

    def __init__(self, root: str | None = None) -> None:
        self.root = root or os.getenv("AZAD_MODEL_LAB_DIR", "data/model_lab")
        os.makedirs(self.root, exist_ok=True)
        self.experiences_file = os.path.join(self.root, "experiences.jsonl")
        self.dataset_file = os.path.join(self.root, "verified_dataset.jsonl")
        self.state_file = os.path.join(self.root, "state.json")

    def record_experience(
        self,
        request: str,
        response: str,
        *,
        success: bool,
        verified: bool = False,
        source: str = "azad",
        tool: str | None = None,
        category: str = "general",
        feedback: str | None = None,
    ) -> bool:
        if not str(request).strip() or not str(response).strip():
            return False
        item = Experience(
            request=str(request).strip(),
            response=str(response).strip(),
            success=bool(success),
            verified=bool(verified),
            source=str(source or "azad"),
            tool=tool,
            category=str(category or "general"),
            feedback=feedback,
            created_at=time.time(),
        ).normalized()
        with open(self.experiences_file, "a", encoding="utf-8") as handle:
            handle.write(json.dumps(item, ensure_ascii=False) + "\n")
        return True

    def _read_experiences(self) -> list[dict[str, Any]]:
        if not os.path.exists(self.experiences_file):
            return []
        rows: list[dict[str, Any]] = []
        with open(self.experiences_file, "r", encoding="utf-8") as handle:
            for line in handle:
                try:
                    row = json.loads(line)
                except json.JSONDecodeError:
                    continue
                if isinstance(row, dict):
                    rows.append(row)
        return rows

    def pending(self, limit: int = 20) -> list[dict[str, Any]]:
        """Return recent unverified candidates, already privacy-redacted."""
        limit = max(1, int(limit))
        rows = self._read_experiences()
        pending = [
            {"index": index, **row}
            for index, row in enumerate(rows)
            if not row.get("verified")
            and row.get("feedback") != "rejected"
        ]
        return pending[-limit:]

    def _update_experience(self, index: int, **changes: Any) -> bool:
        rows = self._read_experiences()
        if index < 0 or index >= len(rows):
            return False
        row = rows[index]
        row.update(changes)
        if "request" in row:
            row["request"] = redact_sensitive(str(row["request"]))
        if "response" in row:
            row["response"] = redact_sensitive(str(row["response"]))
        if row.get("tool"):
            row["tool"] = redact_sensitive(str(row["tool"]))
        if row.get("feedback"):
            row["feedback"] = redact_sensitive(str(row["feedback"]))
        with open(self.experiences_file, "w", encoding="utf-8") as handle:
            for item in rows:
                handle.write(json.dumps(item, ensure_ascii=False) + "\n")
        return True

    def approve_experience(self, index: int) -> bool:
        """Explicitly approve one candidate for the training dataset."""
        return self._update_experience(
            int(index),
            success=True,
            verified=True,
            feedback="approved",
        )

    def reject_experience(self, index: int) -> bool:
        """Reject one candidate without deleting the audit record."""
        return self._update_experience(
            int(index),
            verified=False,
            feedback="rejected",
        )

    def correct_experience(self, index: int, corrected_response: str) -> bool:
        """Replace a candidate response with a human-provided correction."""
        if not str(corrected_response).strip():
            return False
        return self._update_experience(
            int(index),
            response=str(corrected_response).strip(),
            success=True,
            verified=True,
            feedback="corrected",
            category="correction",
        )

    def prepare_verified_dataset(self) -> dict[str, Any]:
        candidates = self._read_experiences()
        approved: list[dict[str, Any]] = []
        seen: set[tuple[str, str]] = set()
        for row in candidates:
            if not row.get("success") or not row.get("verified"):
                continue
            request = redact_sensitive(str(row.get("request", "")).strip())
            response = redact_sensitive(str(row.get("response", "")).strip())
            if not request or not response:
                continue
            key = (request, response)
            if key in seen:
                continue
            seen.add(key)
            approved.append(
                {
                    "instruction": request,
                    "output": response,
                    "category": str(row.get("category", "general")),
                    "source": str(row.get("source", "azad")),
                    "feedback": str(row.get("feedback", "verified")),
                }
            )
        with open(self.dataset_file, "w", encoding="utf-8") as handle:
            for row in approved:
                handle.write(json.dumps(row, ensure_ascii=False) + "\n")
        state = {
            "dataset_examples": len(approved),
            "candidate_experiences": len(candidates),
            "pending_experiences": len(self.pending(limit=max(20, len(candidates)))),
            "updated_at": time.time(),
        }
        with open(self.state_file, "w", encoding="utf-8") as handle:
            json.dump(state, handle, indent=2)
        return state

    def status(self) -> dict[str, Any]:
        state: dict[str, Any] = {}
        if os.path.exists(self.state_file):
            try:
                with open(self.state_file, encoding="utf-8") as handle:
                    loaded = json.load(handle)
                if isinstance(loaded, dict):
                    state = loaded
            except (OSError, json.JSONDecodeError):
                pass
        return {
            "root": self.root,
            "experiences_file": self.experiences_file,
            "dataset_file": self.dataset_file,
            "dataset_examples": int(state.get("dataset_examples", 0)),
            "candidate_experiences": int(
                state.get("candidate_experiences", len(self._read_experiences()))
            ),
            "pending_experiences": len(self.pending()),
        }


__all__ = ["AZADModelLab", "Experience"]
