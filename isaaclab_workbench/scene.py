"""Declarative Isaac Lab workbench scene, visible to scene-based visualizers."""

import isaaclab.sim as sim_utils
from isaaclab.assets import AssetBaseCfg, RigidObjectCfg
from isaaclab.scene import InteractiveSceneCfg
from isaaclab.utils import configclass

from .geometry import WorkbenchSpec


def _static_box(path: str, color: tuple[float, float, float]) -> AssetBaseCfg:
    return AssetBaseCfg(
        prim_path=path,
        spawn=sim_utils.CuboidCfg(
            size=(0.1, 0.1, 0.1),
            collision_props=sim_utils.UsdPhysicsCollisionCfg(),
            visual_material=sim_utils.PreviewSurfaceCfg(diffuse_color=color),
        ),
    )


@configclass
class WorkbenchSceneCfg(InteractiveSceneCfg):
    """Single-env scene whose assets participate in Isaac Lab's clone plan."""

    ground = AssetBaseCfg(prim_path="/World/Ground", spawn=sim_utils.GroundPlaneCfg())

    top = _static_box("{ENV_REGEX_NS}/Top", (0.35, 0.40, 0.45))
    leg_l_back = _static_box("{ENV_REGEX_NS}/Leg_L_Back", (0.20, 0.22, 0.25))
    leg_l_front = _static_box("{ENV_REGEX_NS}/Leg_L_Front", (0.20, 0.22, 0.25))
    leg_r_back = _static_box("{ENV_REGEX_NS}/Leg_R_Back", (0.20, 0.22, 0.25))
    leg_r_front = _static_box("{ENV_REGEX_NS}/Leg_R_Front", (0.20, 0.22, 0.25))

    test_cube: RigidObjectCfg | None = RigidObjectCfg(
        prim_path="{ENV_REGEX_NS}/TestCube",
        spawn=sim_utils.CuboidCfg(
            size=(0.08, 0.08, 0.08),
            collision_props=sim_utils.UsdPhysicsCollisionCfg(),
            rigid_props=sim_utils.UsdPhysicsRigidBodyCfg(),
            mass_props=sim_utils.MassCfg(mass=0.5),
            visual_material=sim_utils.PreviewSurfaceCfg(diffuse_color=(0.90, 0.20, 0.10)),
        ),
    )

    light = AssetBaseCfg(prim_path="/World/Light", spawn=sim_utils.DomeLightCfg(intensity=3000.0))


def make_scene_cfg(spec: WorkbenchSpec, *, test_cube: bool = True) -> WorkbenchSceneCfg:
    """Set component geometry and poses; the tabletop surface is at ``height``."""
    cfg = WorkbenchSceneCfg(num_envs=1, env_spacing=2.0)
    cfg.top.spawn.size = (spec.width, spec.depth, spec.top_thickness)
    cfg.top.init_state.pos = (0.0, 0.0, spec.top_center_z)

    for name, x, y in (
        ("leg_l_back", -spec.leg_x, -spec.leg_y),
        ("leg_l_front", -spec.leg_x, spec.leg_y),
        ("leg_r_back", spec.leg_x, -spec.leg_y),
        ("leg_r_front", spec.leg_x, spec.leg_y),
    ):
        leg = getattr(cfg, name)
        leg.spawn.size = (spec.leg_size, spec.leg_size, spec.leg_height)
        leg.init_state.pos = (x, y, spec.leg_height / 2)

    if test_cube:
        cfg.test_cube.init_state.pos = (0.0, 0.0, spec.height + 0.35)
    else:
        cfg.test_cube = None
    return cfg
