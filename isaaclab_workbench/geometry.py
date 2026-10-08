"""Workbench dimensions and component poses, in meters."""

from dataclasses import dataclass
from math import isfinite


@dataclass(frozen=True)
class WorkbenchSpec:
    width: float = 1.20
    depth: float = 0.60
    height: float = 0.75
    top_thickness: float = 0.04
    leg_size: float = 0.06
    leg_inset: float = 0.02

    def __post_init__(self) -> None:
        values = vars(self)
        if any(not isfinite(value) or value <= 0 for value in values.values()):
            raise ValueError("All workbench dimensions must be finite and positive")
        if self.top_thickness >= self.height:
            raise ValueError("top_thickness must be smaller than height")
        if self.width <= 2 * (self.leg_inset + self.leg_size):
            raise ValueError("width is too small for four inset legs")
        if self.depth <= 2 * (self.leg_inset + self.leg_size):
            raise ValueError("depth is too small for four inset legs")

    @property
    def top_center_z(self) -> float:
        return self.height - self.top_thickness / 2

    @property
    def leg_height(self) -> float:
        return self.height - self.top_thickness

    @property
    def leg_x(self) -> float:
        return self.width / 2 - self.leg_inset - self.leg_size / 2

    @property
    def leg_y(self) -> float:
        return self.depth / 2 - self.leg_inset - self.leg_size / 2
