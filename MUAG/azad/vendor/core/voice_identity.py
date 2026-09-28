from __future__ import annotations

import json
import os
from pathlib import Path
from typing import Dict, Optional


class VoiceIdentity:
    """Optional speaker-verification gate for AZAD's voice interface.

    Voice embeddings are stored locally under data/ and are intentionally not
    committed to Git. A voice match is an access signal, not cryptographic
    authentication; a separate mobile token can be required for network access.
    """

    def __init__(self, profile_path: str | Path = "data/voice_profiles/uzair.json", threshold: Optional[float] = None):
        self.profile_path = Path(profile_path)
        self.threshold = float(threshold or os.getenv("AZAD_VOICE_THRESHOLD", "0.55"))

    @property
    def available(self) -> bool:
        try:
            import resemblyzer  # noqa: F401
            import numpy  # noqa: F401
            return True
        except ImportError:
            return False

    def enroll(self, audio_path: str | Path) -> Dict:
        if not self.available:
            return {"success": False, "error": "Voice verification requires resemblyzer and numpy."}
        from resemblyzer import VoiceEncoder, preprocess_wav

        wav = preprocess_wav(Path(audio_path))
        if len(wav) < 16000 * 3:
            return {"success": False, "error": "Please provide at least 3 seconds of clear speech."}
        encoder = VoiceEncoder("cpu")
        embedding = encoder.embed_utterance(wav)
        self.profile_path.parent.mkdir(parents=True, exist_ok=True)
        self.profile_path.write_text(
            json.dumps({"owner": "Uzair", "embedding": embedding.tolist(), "version": 1}, indent=2),
            encoding="utf-8",
        )
        return {"success": True, "owner": "Uzair", "profile": str(self.profile_path)}

    def verify(self, audio_path: str | Path) -> Dict:
        if not self.profile_path.exists():
            return {"success": False, "verified": False, "error": "Uzair voice profile is not enrolled."}
        if not self.available:
            return {"success": False, "verified": False, "error": "Voice verification dependency is unavailable."}

        import numpy as np
        from resemblyzer import VoiceEncoder, preprocess_wav

        profile = json.loads(self.profile_path.read_text(encoding="utf-8"))
        reference = np.asarray(profile["embedding"], dtype=np.float32)
        wav = preprocess_wav(Path(audio_path))
        if len(wav) < 16000 * 1:
            return {"success": False, "verified": False, "error": "Voice sample is too short."}
        encoder = VoiceEncoder("cpu")
        candidate = encoder.embed_utterance(wav)
        similarity = float(np.inner(reference, candidate))
        return {
            "success": True,
            "verified": similarity >= self.threshold,
            "owner": "Uzair" if similarity >= self.threshold else "unknown",
            "similarity": round(similarity, 4),
            "threshold": self.threshold,
        }
