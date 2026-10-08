"""Run the standalone workbench scene using the installed Isaac Lab runtime."""

import argparse

from isaaclab.app import add_launcher_args, launch_simulation

from .geometry import WorkbenchSpec


def main() -> None:
    parser = argparse.ArgumentParser(description="DENSO workbench collision smoke test")
    parser.add_argument("--width", type=float, default=1.20, help="Bench width in meters")
    parser.add_argument("--depth", type=float, default=0.60, help="Bench depth in meters")
    parser.add_argument("--height", type=float, default=0.75, help="Top surface height in meters")
    parser.add_argument("--no-test-cube", action="store_true", help="Do not spawn the falling cube")
    add_launcher_args(parser)
    args = parser.parse_args()

    try:
        spec = WorkbenchSpec(width=args.width, depth=args.depth, height=args.height)
    except ValueError as exc:
        parser.error(str(exc))

    import isaaclab.sim as sim_utils

    from .scene import spawn_workbench

    sim_cfg = sim_utils.SimulationCfg(dt=0.01, device=args.device)
    with launch_simulation(sim_cfg, args):
        context = sim_utils.SimulationContext(sim_cfg)
        context.set_camera_view([2.0, 1.7, 1.5], [0.0, 0.0, spec.height / 2])

        ground = sim_utils.GroundPlaneCfg()
        ground.func("/World/Ground", ground)
        light = sim_utils.DomeLightCfg(intensity=3000.0)
        light.func("/World/Light", light)
        spawn_workbench(spec, test_cube=not args.no_test_cube)

        context.reset()
        print(f"Workbench ready: {spec.width:.2f} x {spec.depth:.2f} x {spec.height:.2f} m")
        print("Expected: the red test cube falls and stays on the tabletop.")
        while context.is_running():
            context.step()


if __name__ == "__main__":
    main()
