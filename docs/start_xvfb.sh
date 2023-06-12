#!/bin/bash
set -ueo pipefail

# replicate the --auto-servernum functionality from xvfb-run
# https://unix.stackexchange.com/questions/291804/howto-terminate-xvfb-run-properly
# Copyright (C) 2005 The T2 SDE Project
# Copyright (C) XXXX - 2005 Debian
# GNU GPLv2
SERVERNUM=0
find_free_servernum() {
    # Sadly, the "local" keyword is not POSIX.  Leave the next line commented in
    # the hope Debian Policy eventually changes to allow it in /bin/sh scripts
    # anyway.
    local i

    i=$SERVERNUM
    while [ -f /tmp/.X$i-lock ]; do
        i=$(($i + 1))
    done
    echo $i
}

SERVERNUM=$(find_free_servernum)

# TODO: allow configuration of screen
Xvfb :$SERVERNUM -screen 0, 1024x768x16 > /tmp/xvfb-output 2>&1 &

echo "$!"
echo "$SERVERNUM"
