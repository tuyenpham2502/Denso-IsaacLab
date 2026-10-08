"""Unit tests for the workbench geometry, without requiring Isaac Sim."""

import unittest

from isaaclab_workbench.geometry import WorkbenchSpec


class WorkbenchSpecTests(unittest.TestCase):
    def test_default_poses(self) -> None:
        spec = WorkbenchSpec()
        self.assertAlmostEqual(spec.top_center_z + spec.top_thickness / 2, spec.height)
        self.assertAlmostEqual(spec.leg_height, 0.71)
        self.assertGreater(spec.leg_x, 0)
        self.assertGreater(spec.leg_y, 0)

    def test_invalid_dimensions(self) -> None:
        for dimensions in (
            {"height": 0.0},
            {"height": float("nan")},
            {"height": 0.03},
            {"width": 0.10},
            {"depth": 0.10},
        ):
            with self.subTest(dimensions=dimensions), self.assertRaises(ValueError):
                WorkbenchSpec(**dimensions)


if __name__ == "__main__":
    unittest.main()
