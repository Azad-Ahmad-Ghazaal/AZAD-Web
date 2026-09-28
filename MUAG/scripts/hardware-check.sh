#!/bin/sh
set -eu

echo "=== MUAG hardware check ==="
echo "Kernel: $(uname -a)"
echo "Architecture: $(uname -m)"

if [ -r /proc/meminfo ]; then
  awk '/MemTotal/ {printf "RAM: %.0f MB\\n", $2/1024}' /proc/meminfo
fi

for d in /sys/class/input/*; do
  [ -e "$d" ] || continue
  name="$(cat "$d/name" 2>/dev/null || true)"
  [ -n "$name" ] && echo "Input: $name"
done

[ -d /sys/class/net ] && ls /sys/class/net | sed 's/^/Network: /'
[ -d /sys/class/video4linux ] && ls /sys/class/video4linux | sed 's/^/Camera: /'
[ -d /sys/class/drm ] && ls /sys/class/drm | sed 's/^/Display: /'
