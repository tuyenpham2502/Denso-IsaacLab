# DENSO workbench for Isaac Lab

This is a standalone, robot-free smoke test. It creates a static workbench with
colliders and drops a dynamic cube onto its top. Dimensions are placeholders,
not a DENSO standard. The scene is constructed from code on every run; no USD
asset or IsaacLab-Arena installation is needed.

## Run on the Ubuntu GPU VM

Prerequisites: the existing `/root/IsaacLab` installation with its `isaacsim`
and `viser` extras, and this repository cloned to `/root/Denso-IsaacLab`.

```bash
cd /root/Denso-IsaacLab
/root/IsaacLab/.venv/bin/python -m isaaclab_workbench.run --visualizer viser
```

From the Mac, keep the existing SSH tunnel to VM port 8080 open and visit
`http://localhost:8080/`. Stop the simulation with Ctrl+C. Do not run the G1
teleoperation scene simultaneously on the same port.

Change the sample dimensions (meters):

```bash
/root/IsaacLab/.venv/bin/python -m isaaclab_workbench.run \
  --visualizer viser --width 1.50 --depth 0.75 --height 0.85
```

Pass `--no-test-cube` to hide the collision test cube. A successful first run
shows the tabletop, four legs and the red cube coming to rest on the tabletop.
This does **not** verify Quest XR, a robot, or fidelity to the real DENSO
workbench. Those are separate milestones. If the cube falls through the top,
capture the VM log and the Viser view before changing the scene.

The geometry and poses are defined in `geometry.py`; the reusable spawn
configuration is in `scene.py`. The scene uses `InteractiveSceneCfg` so
visualizers can discover its assets through Isaac Lab's scene/clone plan.
Source patterns follow Isaac Lab's official
[empty scene](https://isaac-sim.github.io/IsaacLab/develop/source/how-to/create_empty.html)
and [interactive scene](https://isaac-sim.github.io/IsaacLab/develop/source/how-to/create_scene.html)
guides.
