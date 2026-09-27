# MUAG Architecture

Boot flow: firmware/boot -> Linux kernel -> init/userspace -> hardware services -> desktop shell -> applications.

## Base
- Linux kernel
- BusyBox
- musl userspace
- lightweight init/service manager
- x86_64 boot path

## Hardware layer
- Linux input subsystem for keyboard/touchpad/touchscreen
- standard USB, PCI, I2C and ACPI interfaces where supported
- lightweight networking services for Wi-Fi/Bluetooth
- ALSA/PipeWire only where needed, with resource limits

## Desktop
The MUAG desktop will provide a Windows-11-inspired layout without copying proprietary code or assets. It will prioritize touch targets, low memory usage and keyboard navigation.

## Browser
Chromium-based browser integration will be added after the base desktop is stable. Distribution of Google Chrome itself will be handled separately from the open-source base where licensing/distribution requirements apply.
