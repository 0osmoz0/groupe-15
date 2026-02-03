import math
from dataclasses import dataclass, field
from typing import Optional

from .hitbox import Hitbox, HitboxType
from .knockback import (
    compute_knockback,
    apply_directional_influence,
    causes_tumble,
    KnockbackResult,
)
from .hitstun import compute_hitstun_frames


@dataclass
class VictimStats:
    current_percent: float
    weight: float
    launch_rate: float = 1.0
    rage_mult: float = 1.0
    crouch_cancel: float = 1.0


@dataclass
class HitResult:
    damage_dealt: float
    knockback: KnockbackResult
    hitstun_frames: int
    tumble: bool
    velocity_x: float
    velocity_y: float


def resolve_hit(
    hitbox: Hitbox,
    victim: VictimStats,
    attacker_facing_right: bool,
    *,
    di_angle_rad: Optional[float] = None,
    di_strength: float = 0.18,
    hitstun_style: str = "melee",
) -> Optional[HitResult]:
    if hitbox.hitbox_type == HitboxType.NO_KNOCKBACK:
        return None

    set_kb = hitbox.hitbox_type == HitboxType.SET_KNOCKBACK
    set_p = hitbox.set_knockback_val if set_kb else None

    victim_percent_after = victim.current_percent + hitbox.damage

    res = compute_knockback(
        victim_percent_after,
        hitbox.damage,
        victim.weight,
        hitbox.base_knockback,
        hitbox.knockback_scaling,
        hitbox.angle_deg,
        set_knockback=set_kb,
        set_knockback_p=set_p or 10.0,
        weight_independent=hitbox.weight_independent,
        launch_rate=victim.launch_rate,
        rage_mult=victim.rage_mult,
        crouch_cancel=victim.crouch_cancel,
    )

    angle_rad = res.angle_rad
    vx, vy = res.velocity_x, res.velocity_y
    if not attacker_facing_right:
        vx = -vx
        angle_rad = math.pi - angle_rad

    if di_angle_rad is not None and (vx != 0 or vy != 0):
        vx, vy = apply_directional_influence(
            vx, vy, angle_rad, di_angle_rad, di_strength
        )

    tumble = causes_tumble(res.knockback_units)
    hitstun = compute_hitstun_frames(
        res.knockback_units,
        style=hitstun_style,
        hitstun_modifier=hitbox.hitstun_modifier,
        sent_tumbling=tumble,
        electric_attack=False,
    )

    return HitResult(
        damage_dealt=hitbox.damage,
        knockback=res,
        hitstun_frames=hitstun,
        tumble=tumble,
        velocity_x=vx,
        velocity_y=vy,
    )


@dataclass
class ActiveAttack:
    attack_id: str
    current_frame: int
    total_frames: int
    hitboxes: list[Hitbox]
    hit_this_attack: set[int] = field(default_factory=set)


def get_active_hitboxes(attack: ActiveAttack) -> list[Hitbox]:
    return [h for h in attack.hitboxes if h.is_active(attack.current_frame)]


def advance_attack(attack: ActiveAttack) -> bool:
    attack.current_frame += 1
    return attack.current_frame < attack.total_frames


def check_hitbox_vs_circle(
    hitbox: Hitbox,
    hitbox_world_x: float,
    hitbox_world_y: float,
    target_x: float,
    target_y: float,
    target_radius: float,
    facing_right: bool,
) -> bool:
    hw, hh = hitbox.width / 2, hitbox.height / 2
    dx = abs(target_x - hitbox_world_x)
    dy = abs(target_y - hitbox_world_y)
    if dx > hw + target_radius or dy > hh + target_radius:
        return False
    if dx <= hw or dy <= hh:
        return True
    cx = dx - hw
    cy = dy - hh
    return cx * cx + cy * cy <= target_radius * target_radius
