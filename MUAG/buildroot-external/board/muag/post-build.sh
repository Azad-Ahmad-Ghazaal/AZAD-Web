#!/bin/sh
set -eu
install -d "$TARGET_DIR/etc"
printf '%s\n' 'MUAG Project' > "$TARGET_DIR/etc/muag-release"
if [ -f "$TARGET_DIR/etc/inittab" ]; then
  :
fi
