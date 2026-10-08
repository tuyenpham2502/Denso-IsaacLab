# Container image audit — 2026-10-08

| Component | Distribution confirmed | Compose decision |
| --- | --- | --- |
| Isaac Sim | Official `nvcr.io/nvidia/isaac-sim:6.1.0`; manifest read successfully | Base of the combined image |
| Isaac Lab | Official `nvcr.io/nvidia/isaac-lab:3.0.0-rc1`; manifest and metadata read successfully | Not used by the combined build; install Arena's pinned Lab submodule instead |
| IsaacLab-Arena | Official docs describe source builds; no supported public image verified | Built directly by Compose into the single `arena` service image |
| IsaacTeleop / CloudXR | Arena pins `isaacteleop[retargeters,ui,cloudxr]`; its teleop script auto-launches the runtime | Installed in the Arena environment; no arbitrary standalone image |
| Quest web client | NVIDIA hosts a prebuilt web client | Browser on headset, no VM container required |
| Viser / Mac observer | Visualizer coupled to Isaac Lab | Not configured in this basic setup |
| NVIDIA driver / Container Toolkit | Host prerequisites | Configure on the VM |

Checks performed without downloading image layers:

```bash
docker manifest inspect nvcr.io/nvidia/isaac-sim:6.1.0
docker manifest inspect nvcr.io/nvidia/isaac-lab:3.0.0-rc1
docker buildx imagetools inspect nvcr.io/nvidia/isaac-lab:3.0.0-rc1 --format '{{json .Image}}'
```

Verified amd64 manifest digests:

- Sim: `sha256:0c16dd67d09a70ea474f2c809a13c4d09bd23c738184cf1bf28af487ecd39080`
- Lab: `sha256:1e795d3f10b50e97f93141a8eb1fa4d2c90a192c226a1bceecc5338ca87652f3`

Historical prebuilt Lab inspection (not the current combined image): user `isaaclab`, `HOME=/root`, working directory
`/workspace/isaaclab`, inherited entrypoint `/isaac-sim/runheadless.sh`.
Build history creates uid/gid 1000 and runs `isaaclab.sh --install`.
Rolling develop docs describe newer interpreter layouts. The current combined
image follows Arena's pinned installation scripts and uses `/isaac-sim/python.sh`.

Manifest access confirms registry availability, not successful layer download,
GPU simulation, complete teleop dependencies in the Lab image, or Quest
streaming. Runtime verification is pending. Arena pins its own Lab submodule;
its custom image is not interchangeable with the prebuilt Lab release.

Sources:

- [Isaac Sim NGC](https://catalog.ngc.nvidia.com/orgs/nvidia/-/containers/isaac-sim/6.1.0/tags)
- [Official Isaac Lab images](https://isaac-sim.github.io/IsaacLab/develop/source/workflows/docker/images.html)
- [Arena installation](https://isaac-sim.github.io/IsaacLab-Arena/main/pages/quickstart/installation.html)
- [Pinned Arena dependencies](https://github.com/isaac-sim/IsaacLab-Arena/blob/1cfc849b2172d040e2e5fce52322678f4f199387/pyproject.toml)
- [Pinned teleop workflow](https://github.com/isaac-sim/IsaacLab-Arena/blob/1cfc849b2172d040e2e5fce52322678f4f199387/docs/pages/example_workflows/locomanipulation/step_2_teleoperation.rst)
- [Hosted Quest client](https://nvidia.github.io/IsaacTeleop/main/getting_started/build_from_source/webxr.html)
