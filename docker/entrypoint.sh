#!/bin/bash
set -e

# If HOST_UID/HOST_GID are set, ensure /output is owned by the host user
# then drop privileges and run the command as that user.
# This avoids output files being owned by root without requiring the user
# to pre-create the output directory.
if [ -n "${HOST_UID}" ] && [ -n "${HOST_GID}" ]; then
    mkdir -p /output
    chown "${HOST_UID}:${HOST_GID}" /output
    exec gosu "${HOST_UID}:${HOST_GID}" "$@"
else
    exec "$@"
fi
