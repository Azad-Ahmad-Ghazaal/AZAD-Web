from __future__ import annotations

from pathlib import Path
from typing import Optional
import tempfile
import wave


class LocalVoiceTranscriber:
    """Optional local transcription adapter.

    Uses faster-whisper when installed. AZAD continues to work without it.
    """

    def __init__(self, model_size: str = "tiny", language: Optional[str] = None) -> None:
        self.model_size = model_size
        self.language = language
        self._model = None

    @property
    def available(self) -> bool:
        try:
            import faster_whisper  # noqa: F401
            return True
        except Exception:
            return False

    def _load(self):
        if self._model is None:
            from faster_whisper import WhisperModel
            self._model = WhisperModel(
                self.model_size,
                device="cpu",
                compute_type="int8",
            )
        return self._model

    def transcribe(self, audio_path: str | Path) -> dict:
        path = Path(audio_path)
        if not path.exists():
            return {"success": False, "text": "", "error": f"Audio not found: {path}"}
        if not self.available:
            return {
                "success": False,
                "text": "",
                "error": "faster-whisper is not installed. Install requirements-voice-local.txt.",
            }

        try:
            model = self._load()
            segments, info = model.transcribe(
                str(path),
                language=self.language,
                vad_filter=True,
                beam_size=1,
            )
            text = " ".join(segment.text.strip() for segment in segments).strip()
            return {
                "success": bool(text),
                "text": text,
                "language": getattr(info, "language", None),
                "duration": getattr(info, "duration", None),
            }
        except Exception as exc:
            return {"success": False, "text": "", "error": str(exc)}
