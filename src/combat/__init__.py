from .hitbox import Hitbox, HitboxType
from .knockback import (
    compute_knockback,
    apply_directional_influence,
    apply_gravity_modifier_tumble,
    decay_launch_speed,
    causes_tumble,
    compute_rage_mult,
    KnockbackResult,
    LAUNCH_SPEED_FACTOR,
    KNOCKBACK_DECAY,
)
from .hitstun import compute_hitstun_frames
from .attack import resolve_hit, HitResult, VictimStats, ActiveAttack, get_active_hitboxes
from .attacks_data import ATTACKS, get_attack_hitboxes, AttackType, ATTACK_IDS_PROJECTILE
from .projectile_sprite import ProjectileSprite

__all__ = [
    "Hitbox",
    "HitboxType",
    "compute_knockback",
    "apply_directional_influence",
    "apply_gravity_modifier_tumble",
    "decay_launch_speed",
    "causes_tumble",
    "compute_rage_mult",
    "KnockbackResult",
    "LAUNCH_SPEED_FACTOR",
    "KNOCKBACK_DECAY",
    "compute_hitstun_frames",
    "resolve_hit",
    "HitResult",
    "VictimStats",
    "ActiveAttack",
    "get_active_hitboxes",
    "ATTACKS",
    "get_attack_hitboxes",
    "AttackType",
    "ATTACK_IDS_PROJECTILE",
    "ProjectileSprite",
]
