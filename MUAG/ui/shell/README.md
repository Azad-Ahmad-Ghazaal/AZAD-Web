# MUAG Shell

The shell prototype is the user-facing desktop layer for MUAG Project.

## Current prototype

- Windows-11-inspired centered taskbar
- Start menu
- App search
- Pinned applications
- Recommended items
- Clock/status area
- Touch-friendly controls
- Responsive layout

## Runtime

- `index.html` contains the UI.
- `muag-shell.py` launches the UI in the first available Chromium/Chrome/Firefox runtime.
- The launcher is replaceable; hardware services must remain independent from the UI.

## Integration roadmap

1. Package the shell into the Buildroot root filesystem.
2. Add a Chromium-based runtime.
3. Connect Files, Settings, Terminal and Hardware Check to real MUAG services.
4. Add touchscreen gesture handling.
5. Add Wi-Fi, Bluetooth, battery, audio and notification status providers.
6. Replace the prototype launcher with a lighter native shell if image/RAM targets require it.

The shell must not own hardware drivers. Hardware state comes from Linux services and system interfaces, ALSA, BlueZ and networking interfaces.
