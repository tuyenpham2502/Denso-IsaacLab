# Isaac Sim + Isaac Lab + Arena: one Docker Compose environment

`compose.yaml` now has **one service, `arena`**, with a complete Docker build.
It installs Isaac Sim, Isaac Lab, IsaacLab-Arena and Arena's pinned
IsaacTeleop/CloudXR dependencies into the same image/Python environment.
No custom base image, host Python installation, or manual Arena checkout is
required. No DENSO workbench is included.

## First setup on a Linux GPU VM / Docker host

The host needs Docker Engine, the Compose plugin, BuildKit, a compatible
NVIDIA driver, and NVIDIA Container Toolkit configured for Docker. This is a
Linux/amd64 deployment. The driver stays on the host.

```bash
nvidia-smi
docker version
docker compose version
cd /root/Denso-IsaacLab
git pull --ff-only
cd deploy
cp -n .env.example .env
nano .env
```

Set `ACCEPT_EULA=Y` after accepting NVIDIA's Isaac Sim EULA. Use a persistent
disk for `DENSO_DATA_DIR`; leave `ARENA_MODE=idle` for basic setup. Existing
`.env` files are preserved. An old `ISAACLAB_IMAGE` entry is now unused.
If you ran an earlier version's `lab`/`lab-init`, stop those old containers
with `docker compose down --remove-orphans` before starting the new layout.
This removes project containers, not their bind-mounted data. The old
`/srv/denso/lab` directory is not deleted or automatically migrated.

Build and start:

```bash
docker compose build arena
docker compose up -d --no-build --pull never
docker compose logs --tail=50
```

Or combine build/start: `docker compose up -d --build --pull never`.
`--pull never` applies to the final service image; BuildKit still downloads
the official base image, source and installation dependencies on first build.
First build is large and may take substantial time/disk; inspect `df -h` and
Docker storage capacity first. Subsequent builds reuse Docker's layer cache.

## Verify the environment

```bash
docker compose exec arena nvidia-smi
docker compose exec arena /opt/denso/entrypoint.sh check
docker compose run --rm --no-deps arena smoke
```

`check` reports package versions. `smoke` runs Arena's headless cube task for
20 steps. Successful package checks are not proof that GPU simulation works;
the smoke task must finish without a traceback. Enter the installed environment:

```bash
docker compose exec arena /opt/denso/entrypoint.sh shell
```

Within it, `/isaac-sim/python.sh` is the interpreter for all three components.
Default startup (`idle`) keeps the environment ready; it does not launch a
scene, desktop, viewer, or VR session automatically.

## Optional G1 / Quest VR

```bash
docker compose run --rm --no-deps arena teleop
```

Complete the CloudXR EULA prompt yourself. Verify G1 appears on Quest and
tracked input controls it. Stop the foreground container with Ctrl+C, then
test another launch to confirm consent persists. The temporary container is
removed when it exits. Once confirmed, set `ARENA_MODE=teleop` in `.env` and
run `docker compose up -d --no-build --pull never` to start VR automatically.
Do not run foreground and background teleop simultaneously on the same ports.

The upstream integration auto-launches CloudXR inside the environment, so a
separate CloudXR service is not configured. Host/provider routing needs the
runtime's TCP 49100, TCP 48322 (HTTPS proxy), and UDP 47998. HTTPS clients need
WSS and a trusted certificate matching the server address. Runtime/Quest
verification remains necessary; containerization does not fix NAT/UDP limits.
The Mac observer at 8080 is not part of this basic environment.

## Save and reuse

On the same VM/disk, `docker compose up -d --no-build --pull never` reuses the
existing image. The restart policy restarts it when Docker starts unless you
explicitly stopped it. No rebuild/pull is required on each boot.

For another VM, publish the tested image:

```bash
docker tag denso-arena:local ghcr.io/tuyenpham2502/denso-isaaclab:0.1.0
docker login ghcr.io -u tuyenpham2502
docker push ghcr.io/tuyenpham2502/denso-isaaclab:0.1.0
```

These commands assume `DENSO_IMAGE=denso-arena:local` during build. Replace
that source tag if you used a different one. On the new VM, copy the deployment
files, set `DENSO_IMAGE` to the published tag in `.env`, then:

```bash
docker compose pull arena
docker compose up -d --no-build
```

Datasets, models, output, configuration and caches stay under `DENSO_DATA_DIR`
outside the image. Restore or attach that disk separately on a new VM. Container
removal preserves bind mounts; deleting the VM disk does not. Remote robot/scene
assets can still download at first launch. Keep secrets outside Git/images.

## EzyCloudX Docker GPU versus a VM

Compose needs access to a Docker daemon. Root inside a rented container alone
does not provide that access. If EzyCloudX only accepts an image/template,
build/publish on another Docker host and provide the final image to EzyCloudX,
subject to their custom-image support. The image is self-contained: entrypoint
`/opt/denso/entrypoint.sh`, default argument `idle`, alternative `teleop`.
It does not include an SSH server; provider console/access, persistent mounts,
environment variables, GPU capabilities and UDP routing must be configured
by their platform. That provider workflow has not been verified.

## Versions and verification boundary

- Isaac Sim: official `6.1.0`, pinned Linux/amd64 digest in `Dockerfile`.
- Arena: `1cfc849b2172d040e2e5fce52322678f4f199387` (release/0.3.1 snapshot).
- Isaac Lab: the commit recorded by that Arena submodule.
- Installation: the pinned upstream system, Lab, policy-client and Arena
  dependency scripts, followed by editable Arena installation.
- No cuRobo build or separate GR00T inference/training server is included.

The Dockerfile verifies the four package distributions at build time. The
repository changes have static validation; the complete image build, GPU smoke
test and Quest connection are not yet verified here. See [image audit](IMAGE_AUDIT.md).

Sources: [Arena installation](https://isaac-sim.github.io/IsaacLab-Arena/main/pages/quickstart/installation.html),
[pinned upstream Dockerfile](https://github.com/isaac-sim/IsaacLab-Arena/blob/1cfc849b2172d040e2e5fce52322678f4f199387/docker/Dockerfile.isaaclab_arena).
