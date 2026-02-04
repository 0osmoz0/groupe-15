from __future__ import annotations

from enum import Enum


class HitboxType(Enum):
    NORMAL = "normal"
    SET_KNOCKBACK = "set"
    NO_KNOCKBACK = "none"


class Hitbox:
    def __init__(
        self,
        frame_start: int,
        frame_end: int,
        offset_x: float,
        offset_y: float,
        width: float,
        height: float,
        angle_deg: float,
        base_knockback: float,
        knockback_scaling: float,
        damage: float,
        hitbox_type: HitboxType = HitboxType.NORMAL,
        set_knockback_val: float | None = None,
        weight_independent: bool = False,
        hitstun_modifier: int = 0,
    ):
        self.frame_start = frame_start
        self.frame_end = frame_end
        self.offset_x = offset_x
        self.offset_y = offset_y
        self.width = width
        self.height = height
        self.angle_deg = angle_deg
        self.base_knockback = base_knockback
        self.knockback_scaling = knockback_scaling
        self.damage = damage
        self.hitbox_type = hitbox_type
        self.set_knockback_val = set_knockback_val
        self.weight_independent = weight_independent
        self.hitstun_modifier = hitstun_modifier

    def is_active(self, frame: int) -> bool:
        return self.frame_start <= frame <= self.frame_end

    def get_angle_rad(self) -> float:
        import math
        return math.radians(self.angle_deg)
