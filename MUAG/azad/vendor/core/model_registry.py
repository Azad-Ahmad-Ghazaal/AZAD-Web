"""AZAD local model registry.

Only lightweight, privacy-safe manifests are stored here. Model weights are
never written to Git by this component and artifact paths are stored relative
to the registry root when possible.
"""
from __future__ import annotations
import json
import os
import time
from typing import Any

class AZADModelRegistry:
    STATUSES = {"candidate", "approved", "active", "rejected"}

    def __init__(self, root: str | None = None, benchmark_threshold: float = 0.67) -> None:
        self.root = root or os.getenv("AZAD_MODEL_REGISTRY_DIR", "data/model_registry")
        self.manifest_file = os.path.join(self.root, "models.json")
        self.benchmark_threshold = float(benchmark_threshold)
        os.makedirs(self.root, exist_ok=True)

    def _read(self) -> list[dict[str, Any]]:
        if not os.path.exists(self.manifest_file):
            return []
        try:
            with open(self.manifest_file, encoding="utf-8") as handle:
                data = json.load(handle)
            return data if isinstance(data, list) else []
        except (OSError, json.JSONDecodeError):
            return []

    def _write(self, models: list[dict[str, Any]]) -> None:
        temp = self.manifest_file + ".tmp"
        with open(temp, "w", encoding="utf-8") as handle:
            json.dump(models, handle, ensure_ascii=False, indent=2)
        os.replace(temp, self.manifest_file)

    def register_candidate(self, model_id: str, version: str, *, base_model: str,
                           backend: str, dataset_examples: int,
                           benchmark_score: float | None = None,
                           benchmark_status: str = "backend_required",
                           artifact_path: str | None = None) -> dict[str, Any]:
        model_id, version = str(model_id).strip(), str(version).strip()
        if not model_id or not version:
            raise ValueError("model_id and version are required")
        models = self._read()
        if any(m.get("model_id") == model_id and m.get("version") == version for m in models):
            raise ValueError("model version already registered")
        score = None if benchmark_score is None else float(benchmark_score)
        if score is not None and not 0.0 <= score <= 1.0:
            raise ValueError("benchmark_score must be between 0 and 1")
        artifact = None
        if artifact_path:
            try:
                artifact = os.path.relpath(os.path.abspath(artifact_path), os.path.abspath(self.root))
            except (OSError, ValueError):
                artifact = os.path.basename(str(artifact_path))
        record = {
            "model_id": model_id, "version": version,
            "base_model": str(base_model).strip(), "backend": str(backend).strip(),
            "dataset_examples": max(0, int(dataset_examples)),
            "benchmark_score": score, "benchmark_status": str(benchmark_status),
            "artifact_path": artifact, "status": "candidate", "created_at": time.time(),
        }
        models.append(record)
        self._write(models)
        return record.copy()

    def _find(self, model_id: str, version: str | None = None) -> tuple[list[dict[str, Any]], dict[str, Any]]:
        models = self._read()
        for model in models:
            if model.get("model_id") == model_id and (version is None or model.get("version") == version):
                return models, model
        raise KeyError(f"model not found: {model_id}" + (f":{version}" if version else ""))

    def approve(self, model_id: str, version: str | None = None) -> dict[str, Any]:
        models, model = self._find(model_id, version)
        if model.get("dataset_examples", 0) <= 0:
            raise ValueError("model cannot be approved without dataset examples")
        if model.get("benchmark_status") != "passed":
            raise ValueError("model benchmark has not passed")
        if model.get("benchmark_score") is None or float(model["benchmark_score"]) < self.benchmark_threshold:
            raise ValueError("model benchmark score is below the approval threshold")
        model["status"] = "approved"
        self._write(models)
        return model.copy()

    def reject(self, model_id: str, version: str | None = None) -> dict[str, Any]:
        models, model = self._find(model_id, version)
        model["status"] = "rejected"
        self._write(models)
        return model.copy()

    def set_active(self, model_id: str, version: str | None = None) -> dict[str, Any]:
        models, model = self._find(model_id, version)
        if model.get("status") != "approved":
            raise ValueError("only an approved model can become active")
        for item in models:
            if item is not model and item.get("status") == "active":
                item["status"] = "approved"
        model["status"] = "active"
        self._write(models)
        return model.copy()

    def get_active(self) -> dict[str, Any] | None:
        return next((m.copy() for m in self._read() if m.get("status") == "active"), None)

    def list_models(self) -> list[dict[str, Any]]:
        return [m.copy() for m in self._read()]
