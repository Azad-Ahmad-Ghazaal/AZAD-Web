# AZAD inside MUAG

AZAD is the personal voice/task assistant layer inside MUAG Project.

## Design

MUAG owns:
- kernel and hardware access
- desktop shell
- display/input
- networking, audio and power services

AZAD owns:
- voice input/output
- natural-language task understanding
- task planning
- safe action execution
- user-facing assistant responses
- optional AI providers and local fallback

## Control flow

Voice -> speech-to-text -> AZAD brain -> task/permission router -> MUAG service -> result -> AZAD response -> text-to-speech.

AZAD must never bypass the MUAG safety/permission boundary to execute arbitrary privileged operations.

## Privacy

No hidden telemetry, machine identifiers, location reporting, secrets, API keys, or unrelated personal data are copied from the existing AZAD project into MUAG.

External AI is optional. The local path must remain usable when network AI is unavailable.

## Initial commands

The first integration milestone should support:
- open an application
- open a file/folder
- launch terminal
- system status
- volume controls
- brightness controls
- Wi-Fi/Bluetooth status
- time/date
- search/open browser
- shutdown/restart with explicit confirmation

More powerful automation comes only after the permission model is implemented.
