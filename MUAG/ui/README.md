# MUAG Desktop UI

The MUAG desktop shell is designed for x86_64 Chromebooks with touchscreens and low memory.

## UI goals

- Windows-11-inspired centered launcher
- Touch-friendly controls
- Start/search/pinned/recent sections
- Settings and quick controls
- Status area for network, audio, battery and clock
- Dark/light theme support
- Keyboard and pointer navigation
- No proprietary Windows assets

## Implementation

The first UI milestone uses a small native shell rather than a full desktop environment. The shell should remain replaceable while the kernel, input, networking and hardware services stay independent.

The initial prototype is intentionally dependency-light. Browser, file manager and settings applications will be integrated as separate launchable components.
