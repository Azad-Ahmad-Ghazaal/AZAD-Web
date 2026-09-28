# MUAG AZAD Voice

The voice stack is deliberately local-first:

1. `arecord` captures 16 kHz mono PCM WAV from `/dev/snd`.
2. `whisper-cli`/`whisper-cpp` performs offline transcription.
3. `continuous_voice.py` emits `AZAD_INPUT=<text>` for the AZAD command router.
4. AZAD may call `/run/muag/azad.sock` through `runtime_client.py` for allowlisted OS actions.
5. TTS is provided by `espeak-ng`/`espeak`.

The default model path is `/usr/share/muag/models/ggml-tiny.bin`. The model is intentionally kept outside the base source tree so the OS image can remain small and the model can be replaced independently.

For multilingual speech, use the multilingual `tiny` model rather than `tiny.en`; the upstream whisper.cpp model table lists tiny at about 75 MiB and base at about 142 MiB. citeturn0search0
