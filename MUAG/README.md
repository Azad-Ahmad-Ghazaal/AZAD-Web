# MUAG Project

Lightweight x86_64 operating system project targeting touchscreen Chromebooks with 4 GB RAM and 16 GB storage.

## Goals
- x86_64 only
- Target final system image <= 2 GB
- Touchscreen, touchpad and keyboard support
- Wi-Fi, Bluetooth, audio, webcam and USB support
- Windows 11-inspired lightweight desktop
- Built-in Chromium-based browser
- Live USB boot and disk installation
- Rufus-friendly x86_64 ISO/image
- Hardware detection and graceful fallback across Chromebook variants

## Development stages
1. Bootable x86_64 base
2. Hardware detection/input validation
3. Lightweight graphical desktop
4. Chromium integration
5. Installer and persistence
6. Hardware compatibility testing

**Safety:** early builds must be tested from USB before touching internal storage.
