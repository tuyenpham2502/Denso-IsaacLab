# Basic Isaac Lab setup with one Compose file

The default services pull the **official prebuilt Isaac Lab image**, including
Isaac Sim. No custom image or workbench is needed for this basic setup.
The optional `arena` profile retains the separate Arena build.

Registry manifests and image metadata were checked on 2026-10-08. GPU
simulation and Quest streaming still require a Linux GPU VM test.
See [the image audit](IMAGE_AUDIT.md) for evidence and limitations.

## Host prerequisites

Use a Linux x86_64 GPU VM with Docker Engine, Compose, a compatible NVIDIA
driver and [NVIDIA Container Toolkit](https://docs.nvidia.com/datacenter/cloud-native/container-toolkit/latest/install-guide.html).
The driver is installed on the host, not by Compose.

```bash
nvidia-smi
docker version
docker compose version
```

## Pull and start the basic environment

```bash
cd /root/Denso-IsaacLab
git pull --ff-only
cd deploy
cp -n .env.example .env
nano .env
```

After accepting NVIDIA's Isaac Sim EULA, set `ACCEPT_EULA=Y`. Set
`DENSO_DATA_DIR` to a persistent disk (default `/srv/denso`). Existing `.env`
files are preserved; absent `ISAACLAB_IMAGE` uses the verified default in
Compose. The default image is pinned to its Linux/amd64 manifest digest.

```bash
docker compose config --quiet
docker compose pull
docker compose up -d
docker compose ps -a
docker compose logs --tail=50 lab
```

Only `lab-init` and `lab` start by default:

- `lab-init` uses the same image once to create writable cache/data directories
  under `DENSO_DATA_DIR/lab` for uid/gid 1000. Its successful exit is expected.
- `lab` keeps the installed environment available. It does **not** automatically
  launch a simulation, browser viewer or VR session.

Isaac Lab loads Isaac Sim in its own process, so no separate Sim service is
needed. The unpublished Arena image is excluded from the default pull/start.

## Verify GPU and installed versions

```bash
docker compose exec lab nvidia-smi
docker compose exec lab bash ./isaaclab.sh -p -c \
  "import importlib.metadata as m; print('Isaac Sim:', m.version('isaacsim')); print('Isaac Lab:', m.version('isaaclab'))"
docker compose exec lab bash
```

Use `./isaaclab.sh --help` inside the container to inspect its launcher. The
image is a release, not the VM's current `develop` checkout: its CLI and
teleop dependencies may differ. These checks confirm GPU/package access,
not successful simulation or VR.

The inspected image uses uid/gid 1000, home `/root`, and working directory
`/workspace/isaaclab`. Compose overrides its inherited streaming entrypoint.
Data is mounted at `/data`; caches/configuration persist separately from Arena.

## Stop, restart, update

```bash
docker compose stop lab
docker compose up -d lab
```

If Docker starts at boot, the existing lab container restarts unless explicitly
stopped. No pull is needed on each reboot. To update, select a verified image
in `.env`, then run `pull` and `up -d`. Bind mounts survive container deletion,
but not deletion of the VM disk: use persistent storage or backups.

## Optional Arena + G1/CloudXR

Arena documents a source-build Docker workflow; a supported public prebuilt
Arena image has not been verified. Build the pinned image once:

```bash
cd /root/Denso-IsaacLab
bash deploy/build.sh denso-arena:local
cd deploy
```

Set `DENSO_IMAGE=denso-arena:local` in `.env` (or your own built image tag).
Target the Arena service explicitly:

```bash
docker compose --profile arena run --rm --no-deps arena smoke
docker compose --profile arena run --rm --no-deps arena teleop
```

The first VR session is interactive for the CloudXR EULA. Verify G1 loads,
Quest displays video, and tracked input controls the robot. Stop with Ctrl+C
and verify consent persists on another interactive launch before using:

```bash
docker compose --profile arena up -d arena
docker compose --profile arena logs -f --tail=100 arena
```

The pinned Arena teleop integration auto-launches CloudXR. A separate CloudXR
sidecar is not configured. This integration still needs a VM test. Configure
host/provider routing for TCP 49100, TCP 48322 (HTTPS proxy) and UDP 47998 as
required by the runtime. HTTPS clients need WSS and a matching trusted
certificate. Avoid running native and container teleop on the same ports.

The Mac observer at 8080 is not configured. Viser is coupled to the simulation
process, not a separate service that can read arbitrary simulation state.
NVIDIA's hosted Quest client needs no web-server container on this VM.

Publish the tested Arena image for future pull-only VMs:

```bash
docker tag denso-arena:local ghcr.io/tuyenpham2502/denso-isaaclab:0.1.0
docker login ghcr.io -u tuyenpham2502
docker push ghcr.io/tuyenpham2502/denso-isaaclab:0.1.0
```

Set `DENSO_IMAGE` to the published tag on other VMs, then use
`docker compose --profile arena pull arena` and
`docker compose --profile arena up -d arena`. No combined Arena image has
been published by this change. Keep credentials outside Git and images.
