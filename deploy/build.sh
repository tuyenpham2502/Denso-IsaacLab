#!/usr/bin/env bash
set -euo pipefail
deploy_dir="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd)"
repo_dir="$(cd "$deploy_dir/.." && pwd)"
source "$deploy_dir/arena.env"
image="${1:?Usage: bash deploy/build.sh REGISTRY/IMAGE:VERSION}"
if [[ "$(uname -s)" != Linux || "$(uname -m)" != x86_64 ]]; then
    printf '%s\n' 'Build on an x86_64 Linux machine; validate runtime on an NVIDIA GPU VM.' >&2
    exit 2
fi
docker info >/dev/null
build_dir="$deploy_dir/.build"
upstream_dir="$build_dir/IsaacLab-Arena"
mkdir -p "$build_dir"
if [[ ! -d "$upstream_dir" ]]; then
    git clone --no-checkout https://github.com/isaac-sim/IsaacLab-Arena.git "$upstream_dir"
fi
if [[ -n "$(git -C "$upstream_dir" status --porcelain --untracked-files=no)" ]]; then
    # A fresh --no-checkout clone has no populated index/worktree yet.
    if [[ -f "$upstream_dir/pyproject.toml" ]]; then
        printf '%s\n' 'Arena build checkout has changes; inspect them before rebuilding.' >&2
        exit 2
    fi
fi
git -C "$upstream_dir" fetch origin "$ARENA_COMMIT"
git -C "$upstream_dir" checkout --detach "$ARENA_COMMIT"
git -C "$upstream_dir" -c 'url.https://github.com/.insteadOf=git@github.com:' \
    submodule update --init --recursive
docker build --platform linux/amd64 --target dev \
    -f "$upstream_dir/docker/Dockerfile.isaaclab_arena" \
    -t "$ARENA_BASE_IMAGE" "$upstream_dir"

# Package committed application source; never silently publish a dirty XR prototype.
denso_commit="$(git -C "$repo_dir" rev-parse HEAD)"
context_dir="$(mktemp -d "$build_dir/app.XXXXXX")"
git -C "$repo_dir" archive "$denso_commit" isaaclab_workbench | tar -x -C "$context_dir"
cp "$deploy_dir/Dockerfile" "$deploy_dir/entrypoint.sh" "$context_dir/"
docker build --platform linux/amd64 \
    --build-arg "ARENA_BASE_IMAGE=$ARENA_BASE_IMAGE" \
    --build-arg "ARENA_COMMIT=$ARENA_COMMIT" \
    --build-arg "DENSO_COMMIT=$denso_commit" \
    -t "$image" "$context_dir"
printf '\nBuilt %s. Run the smoke and Quest checks before docker push.\n' "$image"
