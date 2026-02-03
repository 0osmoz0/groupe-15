from dataclasses import dataclass
from enum import Enum
from typing import Optional


class HitboxType(Enum):
    NORMAL = "normal"
    SET_KNOCKBACK = "set"
    NO_KNOCKBACK = "none"


@dataclass
class Hitbox:
    frame_start: int
    frame_end: int
    offset_x: float
    offset_y: float
    width: float
    height: float
    angle_deg: float
    base_knockback: float
    knockback_scaling: float
    damage: float
    hitbox_type: HitboxType = HitboxType.NORMAL
    set_knockback_val: Optional[float] = None
    weight_independent: bool = False
    hitstun_modifier: int = 0

    def is_active(self, frame: int) -> bool:
        return self.frame_start <= frame <= self.frame_end

    def get_angle_rad(self) -> float:
        import math
        return math.radians(self.angle_deg)
