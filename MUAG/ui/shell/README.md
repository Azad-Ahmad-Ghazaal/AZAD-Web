# MUAG Shell Prototype

This directory defines the first desktop-shell contract.

## Required shell surfaces

1. Bottom taskbar with centered launcher
2. Start menu with search
3. Pinned applications
4. Recent files/applications
5. Quick settings
6. Notifications
7. Clock/calendar
8. Battery/network/audio indicators
9. Touch-friendly context menus
10. Virtual desktop hooks

## Input contract

- Pointer/touch primary activation: left click / tap
- Context activation: right click / long press
- Scroll: wheel / touch scroll
- Future gesture hooks: swipe and pinch

The shell must not own hardware drivers. Hardware state comes from Linux services and system interfaces, ALSA, BlueZ and networking interfaces.
