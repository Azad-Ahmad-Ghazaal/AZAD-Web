#!/bin/sh
set -eu
install -d "$TARGET_DIR/etc"
printf '%s\n' 'MUAG Project' > "$TARGET_DIR/etc/muag-release"
if [ -f "$TARGET_DIR/etc/inittab" ]; then
  :
fi
# Bundle the MUAG-native AZAD runtime snapshot and task-training interfaces.
mkdir -p "$TARGET_DIR/usr/share/muag/azad"
if [ -d "$BR2_EXTERNAL_MUAG_PATH/../azad" ]; then
    cp -a "$BR2_EXTERNAL_MUAG_PATH/../azad/." "$TARGET_DIR/usr/share/muag/azad/"
fi
chmod +x "$TARGET_DIR/usr/share/muag/azad/muag_action_bridge.py" 2>/dev/null || true
chmod +x "$TARGET_DIR/usr/share/muag/azad/training/trace.py" 2>/dev/null || true

# Make the boot-time MUAG installer menu executable in the final rootfs.
chmod +x "$TARGET_DIR/etc/init.d/S99muag-installer" 2>/dev/null || true
chmod +x "$TARGET_DIR/usr/bin/muag-installer-menu" 2>/dev/null || true
