# AZAD inside MUAG

AZAD is the assistant layer of MUAG Project.

Flow:
Voice -> speech recognition -> AZAD brain -> MUAG permission/action bridge -> OS action -> AZAD response -> speech.

The AZAD source is vendored under `MUAG/azad/vendor/` from the integration branch of the separate AZAD-AI repository. The source repository itself is not modified.

## Privacy boundary
Do not vendor secrets, .env files, credentials, machine identifiers, location reporting, telemetry, or unrelated personal data.

## Training
Website/task learning is represented as verified task traces. A trace contains intent, page/action observations, expected result, and approval state. It is not automatically trusted or executed as privileged code.

## Resource target
MUAG remains x86_64-only. The final image ceiling is 4 GB; runtime should remain lightweight enough for a 4 GB RAM Chromebook.
