#!/usr/bin/env bash
# Compatibility helper; Compose owns the complete build now.
set -euo pipefail
deploy_dir="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd)"
repo_dir="$(cd "$deploy_dir/.." && pwd)"
export DENSO_IMAGE="${1:?Usage: bash deploy/build.sh REGISTRY/IMAGE:VERSION}"
export DENSO_COMMIT="$(git -C "$repo_dir" rev-parse HEAD)"
docker compose --project-directory "$deploy_dir" -f "$deploy_dir/compose.yaml" build arena
printf '\nBuilt %s. Test GPU, smoke, and Quest before publishing.\n' "$DENSO_IMAGE"
