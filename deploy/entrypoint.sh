#!/usr/bin/env bash
set -euo pipefail

if [[ "${ACCEPT_EULA:-N}" != Y ]]; then
    printf '%s\n' 'Accept the NVIDIA Isaac Sim EULA, then set ACCEPT_EULA=Y in deploy/.env.' >&2
    exit 2
fi
export OMNI_KIT_ACCEPT_EULA=YES
ldconfig
arena_dir=/workspaces/isaaclab_arena
cd "$arena_dir"
mode="${1:-idle}"
if (( $# )); then shift; fi
case "$mode" in
    idle)
        printf '%s\n' 'Isaac Sim + Isaac Lab + Arena environment ready. Use check, smoke, teleop, or shell.'
        exec sleep infinity
        ;;
    check)
        exec /isaac-sim/python.sh -c "import importlib.metadata as m; [print(n, m.version(n)) for n in ('isaacsim', 'isaaclab', 'isaaclab_arena', 'isaacteleop')]"
        ;;
    smoke)
        exec /isaac-sim/python.sh isaaclab_arena/evaluation/policy_runner.py \
            --policy_type zero_action --num_steps 20 "$@" cube_goal_pose
        ;;
    teleop)
        exec /isaac-sim/python.sh submodules/IsaacLab/scripts/environments/teleoperation/teleop_se3_agent.py \
            --device cpu --num_envs 1 --xr \
            --external_callback isaaclab_arena.environments.isaaclab_interop.environment_registration_callback \
            --task galileo_g1_locomanip_pick_and_place \
            --arena_teleop_device openxr "$@"
        ;;
    shell)
        exec /bin/bash "$@"
        ;;
    *)
        printf 'Unknown mode: %s. Use idle, check, smoke, teleop, or shell.\n' "$mode" >&2
        exit 2
        ;;
esac
