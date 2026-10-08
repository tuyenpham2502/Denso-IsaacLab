#!/usr/bin/env bash
set -euo pipefail
if [[ "${ACCEPT_EULA:-N}" != Y ]]; then
    printf '%s\n' 'Accept the NVIDIA Isaac Sim EULA, then set ACCEPT_EULA=Y in deploy/.env.' >&2
    exit 2
fi
export OMNI_KIT_ACCEPT_EULA=YES
printf '%s\n' 'Isaac Lab container ready. No simulation or VR session is running yet.'
printf '%s\n' 'Use docker compose exec lab bash to enter the environment.'
exec sleep infinity
