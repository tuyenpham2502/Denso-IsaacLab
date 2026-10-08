# Denso-IsaacLab

Isaac Lab workbench scene for the DENSO VR workspace project. This repository
contains only the Isaac Lab workbench prototype and its tests; it does not
include the earlier Unity, TeleVision, or Mac runtime projects.

## Current milestone

The scene spawns a static tabletop with four legs and a dynamic red cube. The
cube is a collision smoke test: it should fall and come to rest on the table.
The default 1.20 × 0.60 × 0.75 m dimensions are placeholders, **not** an
approved DENSO workbench standard. No robot, Quest XR, or teleoperation is
included in this milestone.

See [workbench setup](isaaclab_workbench/README.md) for VM commands and
custom dimensions.

## Local geometry tests

The geometry tests do not require Isaac Sim:

```bash
python3 -m unittest discover -s tests/isaaclab_workbench -v
```

Runtime simulation and Viser must be verified on the Ubuntu GPU VM.
