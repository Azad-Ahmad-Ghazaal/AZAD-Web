# MUAG OS v0.1 build baseline

This branch contains the MUAG x86_64 UEFI boot baseline and automated GitHub Actions build/test flow.

CI scans the repository, attempts an existing OS build, falls back to a minimal MUAG UEFI boot image when no usable ISO is present, creates the ISO, runs a QEMU/OVMF smoke boot test, and uploads the ISO plus diagnostics.

VirtualBox is not available on standard GitHub-hosted Linux runners, so QEMU/OVMF is used for automated firmware/boot verification. The generated ISO is directly usable in VirtualBox with UEFI enabled.
