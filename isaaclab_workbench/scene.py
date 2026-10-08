"""Spawn a static, collidable workbench and an optional falling test cube."""

import isaaclab.sim as sim_utils

from .geometry import WorkbenchSpec


def _cuboid(path: str, size: tuple[float, float, float], position: tuple[float, float, float],
            color: tuple[float, float, float], *, dynamic: bool = False) -> None:
    cfg = sim_utils.CuboidCfg(
        size=size,
        collision_props=sim_utils.UsdPhysicsCollisionCfg(),
        rigid_props=sim_utils.UsdPhysicsRigidBodyCfg() if dynamic else None,
        mass_props=sim_utils.MassCfg(mass=0.5) if dynamic else None,
        visual_material=sim_utils.PreviewSurfaceCfg(diffuse_color=color),
    )
    cfg.func(path, cfg, translation=position)


def spawn_workbench(spec: WorkbenchSpec, *, test_cube: bool = True) -> None:
    """Create a bench whose top surface is at ``spec.height`` above the ground."""
    sim_utils.create_prim("/World/Workbench", "Xform")

    _cuboid(
        "/World/Workbench/Top",
        (spec.width, spec.depth, spec.top_thickness),
        (0.0, 0.0, spec.top_center_z),
        (0.35, 0.40, 0.45),
    )
    for x_label, x in (("L", -spec.leg_x), ("R", spec.leg_x)):
        for y_label, y in (("Back", -spec.leg_y), ("Front", spec.leg_y)):
            _cuboid(
                f"/World/Workbench/Leg_{x_label}_{y_label}",
                (spec.leg_size, spec.leg_size, spec.leg_height),
                (x, y, spec.leg_height / 2),
                (0.20, 0.22, 0.25),
            )

    if test_cube:
        _cuboid(
            "/World/Workbench/TestCube",
            (0.08, 0.08, 0.08),
            (0.0, 0.0, spec.height + 0.35),
            (0.90, 0.20, 0.10),
            dynamic=True,
        )
