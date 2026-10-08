# DENSO Arena Docker deployment

This packages the official Arena Docker environment and the committed DENSO
workbench source. Build once on Linux x86_64, test on an NVIDIA GPU VM, push
the image to a registry, and pull it on subsequent VMs.

Status: deployment files only. The image has not yet been built, published,
or validated with a GPU/Quest. This checkout was prepared on a Mac without a
running Docker engine. A successful Compose validation is not a runtime test.

## Contents and version pin

- Arena: `1cfc849b2172d040e2e5fce52322678f4f199387` from `release/0.3.1`.
- Isaac Lab: the submodule revision recorded by that Arena commit.
- Isaac Sim: `6.1.0`, selected by the upstream Dockerfile.
- DENSO source: `isaaclab_workbench` from the repository's committed HEAD.
  Uncommitted workbench changes are deliberately not included by `build.sh`.
- `smoke`: a short headless Arena cube task, exits after 20 steps.
- `teleop`: Arena's G1 Galileo pick-and-place task with OpenXR/CloudXR, one
  environment, CPU physics as in the upstream teleoperation example.
- `workbench`: the existing standalone DENSO workbench prototype. It is not
  yet converted into an Arena environment or combined with the G1 task.

The build uses the upstream `dev` Docker target and replaces its interactive
user-creation entrypoint with a mode-selecting entrypoint. It does not mount
the Docker socket or require a privileged container. CloudXR is expected to
auto-launch from the installed IsaacTeleop package; this must be verified in
the image. No separately managed CloudXR service is configured here.

## 1. Prepare the Linux build/GPU VM once

The host needs Docker Engine, the Compose plugin, a compatible NVIDIA driver,
and NVIDIA Container Toolkit configured for Docker. Isaac Sim/Lab, Python,
and conda do not need to be installed on the host for this deployment.

Follow the [NVIDIA toolkit installation guide](https://docs.nvidia.com/datacenter/cloud-native/container-toolkit/latest/install-guide.html).
Check the host:

```bash
nvidia-smi
docker version
docker compose version
df -h / /var/lib/docker
```

The upstream image and build cache are large; check available storage before
building. This deployment does not improve the RTX 3090's encoding throughput
or the older Xeon's single-thread performance. VR frame rate remains a VM test.

## 2. Build an image

Run from the repository on the Linux build machine:

```bash
cd /root/Denso-IsaacLab
git pull --ff-only
bash deploy/build.sh ghcr.io/tuyenpham2502/denso-isaaclab:0.1.0
cd deploy
cp -n .env.example .env
```

Edit `.env`. Set `DENSO_IMAGE` to the tag just built, `DENSO_DATA_DIR` to a
persistent host disk, and `ACCEPT_EULA=Y` only after accepting the NVIDIA
Isaac Sim EULA. The file is ignored by Git. The build script creates an ignored
`.build/` directory, pins Arena and initializes its submodules using HTTPS
(no GitHub SSH key required). It builds a reusable base image, then the app
image. It never pushes automatically.

## 3. Validate before publishing

From `/root/Denso-IsaacLab/deploy`:

```bash
docker compose config --quiet
docker compose run --rm --no-deps --entrypoint nvidia-smi arena
docker compose run --rm --no-deps arena smoke
docker compose run --rm --no-deps arena teleop
```

The last command runs interactively for the initial CloudXR EULA prompt.
Accept that EULA yourself when prompted, then connect the Quest through the
CloudXR client as in your working VM setup. Stop the foreground session with
Ctrl+C before starting the background service. Check a second interactive
launch to verify that consent/configuration persists. Do not deploy unattended
if it still waits for input.

Acceptance checks:

1. GPU is visible and the short Arena task exits successfully.
2. G1 loads, the Quest displays the scene, and tracked input controls the robot.
3. CloudXR stops with the container and can reconnect after restart.
4. Recordings written under `/datasets` remain after container recreation.

The service uses Linux host networking. The host/provider firewall and routing
must allow the CloudXR client to reach TCP 49100, TCP 48322 for HTTPS proxy,
and UDP 47998 for media, as required by the configured runtime. An HTTPS client
needs the appropriate WSS endpoint and a trusted certificate matching its
address. A TCP listener alone does not prove VR media or tracking works.
Do not run a native CloudXR session on the same ports at the same time.

The separate Mac observer at port 8080 from the earlier prototype is not
configured in this image. The smoke task is headless. Add and validate the
observer explicitly before considering the full Mac+Quest workflow complete.

## 4. Publish after validation

Use a registry credential with package-write permission. `docker login` prompts
for it; do not put tokens in Git, `.env.example`, Dockerfiles, or image layers.

```bash
docker login ghcr.io -u tuyenpham2502
docker push ghcr.io/tuyenpham2502/denso-isaaclab:0.1.0
```

Keep the package private initially. The public source repository does not
require publishing the binary image, company models, or datasets publicly.
Use a new image version for each release and retain previous tested tags for
rollback. These commands describe a future package; none has been published
by this change.

## 5. Pull and run on a deployment VM

Set up the host prerequisites from step 1 once per new VM. Copy/clone this
repository to obtain `deploy/compose.yaml`, then configure `deploy/.env`.
The deployment VM does not need the Arena source or a build toolchain.
Log in to GHCR using package-read credentials if the image is private.

```bash
cd /root/Denso-IsaacLab/deploy
docker compose pull
# First launch on a new VM: complete the interactive EULA/connection test above.
docker compose up -d
docker compose logs -f --tail=100
```

`up -d` starts G1 teleoperation. The restart policy restarts the service after
Docker/VM reboot unless it was explicitly stopped. Configure Docker to start
at boot on the host. A retained VM disk keeps its image layers, so a reboot
does not require downloading them again.

To update: change `DENSO_IMAGE` in `.env` to a tested release, run `pull`, then
`up -d`. To roll back, select the previous image tag and run the same commands.
To stop:

```bash
docker compose down
```

Datasets, models, evaluation output, configuration, CloudXR state and caches
are bind-mounted under `DENSO_DATA_DIR`. Container recreation preserves them.
Deleting the VM's disk does not: use a persistent disk or external backup when
moving between rental VMs. Assets may still download on first launch; the
image does not bundle every remote NVIDIA asset.

To run the standalone workbench instead, stop teleop and run:

```bash
docker compose down
docker compose run --rm --no-deps arena workbench
```

This runs the committed prototype with its default visualizer. Do not assume
it opens a remote UI; follow the workbench documentation for the exact source
version packaged by the image.

## References

- [Arena installation](https://isaac-sim.github.io/IsaacLab-Arena/main/pages/quickstart/installation.html)
- [Pinned upstream Dockerfile](https://github.com/isaac-sim/IsaacLab-Arena/blob/1cfc849b2172d040e2e5fce52322678f4f199387/docker/Dockerfile.isaaclab_arena)
- [G1 teleoperation workflow](https://isaac-sim.github.io/IsaacLab-Arena/main/pages/example_workflows/locomanipulation/step_2_teleoperation.html)
