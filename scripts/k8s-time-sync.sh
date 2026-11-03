#!/bin/bash
# Run on each CentOS 7 guest as root. Chronyd remains the clock owner.
set -euo pipefail
export PATH=/usr/sbin:/usr/bin:/sbin:/bin
export LC_ALL=C
if [ "$EUID" -ne 0 ]; then
    echo "Run as root." >&2
    exit 1
fi
systemctl is-active --quiet chronyd.service
chronyc online
# DNS can still be resolving just after chronyd starts (503 No such source).
# iburst will begin when resolution completes; waitsync remains authoritative.
if ! chronyc burst 4/4; then
    echo "Initial burst unavailable; waiting for chronyd to acquire its sources." >&2
fi
# Do not step using an old cached offset. Wait for chronyd's NTP updates.
# Bounded wait: about 40 seconds; chronyd keeps retrying if this fails.
chronyc waitsync 20 0.5 0 2
hwclock --systohc --utc
date --iso-8601=seconds
chronyc tracking
