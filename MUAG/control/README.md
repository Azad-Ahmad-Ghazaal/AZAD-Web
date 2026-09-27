# MUAG Control Bridge

This directory defines the control boundary between the external development agent (for example, ChatGPT through the connected GitHub integration) and the MUAG Project.

## Purpose

The bridge gives the development agent a stable, explicit contract for maintaining MUAG without requiring direct privileged access to the Chromebook runtime.

### Development control

The connected GitHub integration can:
- inspect MUAG source and build configuration;
- create/update files on the MUAG development branch;
- inspect GitHub Actions build/test results;
- diagnose build failures from workflow logs;
- prepare and verify changes before they are merged to `main`.

The bridge does **not** expose arbitrary shell execution on the user's computer to the external development agent.

### Runtime control

Inside MUAG, AZAD talks to MUAG through the local action boundary:

`voice/text -> AZAD -> permission/router -> local MUAG action bridge -> MUAG service/hardware -> result -> AZAD`

The runtime bridge must remain allowlisted. New actions must be deliberately added and documented.

## Branch policy

- Development work: `feat/muag-os-v0.1`
- Stable branch: `main`
- Do not modify `main) as part of automated development.
- Hardware/destructive actions require explicit user confirmation.

## Privacy boundary

Never place these in the bridge:
- API keys or passwords
- cookies/session tokens
- machine identifiers
- automatic location data
- unrelated personal data
- hidden telemetry
- undocumented network listeners

## Future maintenance

When MUAG changes, the external development agent should first inspect this contract and the current repository state, then make the smallest safe change, run/inspect CI, and report exactly what was verified.
