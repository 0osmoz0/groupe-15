"""
Définition des attaques (hitboxes par frame) : jab, tilts, smash, aériennes, specials, projectile.
"""
from enum import Enum
from .hitbox import Hitbox, HitboxType


class AttackType(Enum):
    JAB = "jab"
    TILT = "tilt"
    SMASH = "smash"
    AERIAL = "aerial"
    DASH_ATTACK = "dash_attack"
    SPECIAL = "special"


ANGLE_SAKURAI = 361
ANGLE_HORIZONTAL = 0
ANGLE_UP = 90
ANGLE_DOWN = 270
ANGLE_DIAG_UP = 45
ANGLE_DIAG_DOWN = 315


def _jab_hitboxes() -> list[Hitbox]:
    return [
        Hitbox(
            frame_start=0, frame_end=14,
            offset_x=58, offset_y=0, width=100, height=90,
            angle_deg=ANGLE_SAKURAI,
            base_knockback=20, knockback_scaling=0.0,
            damage=2.0,
            hitbox_type=HitboxType.SET_KNOCKBACK,
            set_knockback_val=10.0,
            hitstun_modifier=2,
        ),
        Hitbox(
            frame_start=6, frame_end=22,
            offset_x=62, offset_y=0, width=100, height=90,
            angle_deg=ANGLE_SAKURAI,
            base_knockback=25, knockback_scaling=0.0,
            damage=2.0,
            hitbox_type=HitboxType.SET_KNOCKBACK,
            set_knockback_val=10.0,
            hitstun_modifier=2,
        ),
        Hitbox(
            frame_start=12, frame_end=32,
            offset_x=66, offset_y=0, width=105, height=95,
            angle_deg=ANGLE_SAKURAI,
            base_knockback=30, knockback_scaling=0.8,
            damage=4.0,
            hitbox_type=HitboxType.NORMAL,
            hitstun_modifier=3,
        ),
    ]


def _forward_tilt_hitbox() -> list[Hitbox]:
    return [
        Hitbox(
            frame_start=4, frame_end=14,
            offset_x=32, offset_y=0, width=36, height=32,
            angle_deg=ANGLE_SAKURAI,
            base_knockback=26, knockback_scaling=0.9,
            damage=9.0,
            hitbox_type=HitboxType.NORMAL,
        ),
    ]


def _up_tilt_hitbox() -> list[Hitbox]:
    return [
        Hitbox(
            frame_start=3, frame_end=14,
            offset_x=0, offset_y=18, width=32, height=28,
            angle_deg=ANGLE_UP,
            base_knockback=30, knockback_scaling=0.85,
            damage=8.0,
            hitbox_type=HitboxType.NORMAL,
        ),
    ]


def _down_tilt_hitbox() -> list[Hitbox]:
    return [
        Hitbox(
            frame_start=3, frame_end=12,
            offset_x=18, offset_y=-8, width=32, height=22,
            angle_deg=ANGLE_DIAG_DOWN,
            base_knockback=25, knockback_scaling=0.7,
            damage=7.0,
            hitbox_type=HitboxType.NORMAL,
            hitstun_modifier=3,
        ),
    ]


def _forward_smash_hitbox(charge_mult: float = 1.0) -> list[Hitbox]:
    return [
        Hitbox(
            frame_start=12, frame_end=20,
            offset_x=36, offset_y=0, width=40, height=36,
            angle_deg=ANGLE_SAKURAI,
            base_knockback=25 * charge_mult,
            knockback_scaling=1.1 * charge_mult,
            damage=15.0 * charge_mult,
            hitbox_type=HitboxType.NORMAL,
        ),
    ]


def _up_smash_hitbox(charge_mult: float = 1.0) -> list[Hitbox]:
    return [
        Hitbox(
            frame_start=10, frame_end=20,
            offset_x=0, offset_y=24, width=38, height=32,
            angle_deg=ANGLE_UP,
            base_knockback=35 * charge_mult,
            knockback_scaling=1.05 * charge_mult,
            damage=14.0 * charge_mult,
            hitbox_type=HitboxType.NORMAL,
        ),
    ]


def _down_smash_hitbox(charge_mult: float = 1.0) -> list[Hitbox]:
    return [
        Hitbox(
            frame_start=8, frame_end=16,
            offset_x=20, offset_y=-6, width=36, height=24,
            angle_deg=ANGLE_HORIZONTAL,
            base_knockback=28 * charge_mult,
            knockback_scaling=1.0 * charge_mult,
            damage=12.0 * charge_mult,
            hitbox_type=HitboxType.NORMAL,
        ),
    ]


def _neutral_aerial_hitbox() -> list[Hitbox]:
    return [
        Hitbox(
            frame_start=3, frame_end=22,
            offset_x=0, offset_y=0, width=36, height=36,
            angle_deg=ANGLE_SAKURAI,
            base_knockback=30, knockback_scaling=0.75,
            damage=10.0,
            hitbox_type=HitboxType.NORMAL,
        ),
    ]


def _forward_aerial_hitbox() -> list[Hitbox]:
    return [
        Hitbox(
            frame_start=6, frame_end=16,
            offset_x=28, offset_y=0, width=32, height=28,
            angle_deg=ANGLE_SAKURAI,
            base_knockback=35, knockback_scaling=0.9,
            damage=12.0,
            hitbox_type=HitboxType.NORMAL,
        ),
    ]


def _back_aerial_hitbox() -> list[Hitbox]:
    return [
        Hitbox(
            frame_start=5, frame_end=14,
            offset_x=-28, offset_y=0, width=32, height=28,
            angle_deg=180,
            base_knockback=40, knockback_scaling=0.95,
            damage=13.0,
            hitbox_type=HitboxType.NORMAL,
        ),
    ]


def _up_aerial_hitbox() -> list[Hitbox]:
    return [
        Hitbox(
            frame_start=4, frame_end=14,
            offset_x=0, offset_y=24, width=32, height=26,
            angle_deg=ANGLE_UP,
            base_knockback=32, knockback_scaling=0.85,
            damage=11.0,
            hitbox_type=HitboxType.NORMAL,
        ),
    ]


def _down_aerial_hitbox() -> list[Hitbox]:
    return [
        Hitbox(
            frame_start=10, frame_end=18,
            offset_x=0, offset_y=-22, width=28, height=24,
            angle_deg=ANGLE_DOWN,
            base_knockback=30, knockback_scaling=0.8,
            damage=14.0,
            hitbox_type=HitboxType.NORMAL,
        ),
    ]


def _neutral_special_hitbox() -> list[Hitbox]:
    return []


def _side_special_hitbox() -> list[Hitbox]:
    return [
        Hitbox(
            frame_start=8, frame_end=16,
            offset_x=45, offset_y=0, width=40, height=35,
            angle_deg=ANGLE_SAKURAI,
            base_knockback=35, knockback_scaling=0.9,
            damage=12.0,
            hitbox_type=HitboxType.NORMAL,
        ),
    ]


def _up_special_hitbox() -> list[Hitbox]:
    return [
        Hitbox(
            frame_start=6, frame_end=14,
            offset_x=0, offset_y=-30, width=30, height=40,
            angle_deg=ANGLE_UP,
            base_knockback=25, knockback_scaling=0.7,
            damage=8.0,
            hitbox_type=HitboxType.NORMAL,
        ),
    ]


def _down_special_hitbox() -> list[Hitbox]:
    return [
        Hitbox(
            frame_start=10, frame_end=18,
            offset_x=0, offset_y=20, width=35, height=25,
            angle_deg=ANGLE_DOWN,
            base_knockback=30, knockback_scaling=0.85,
            damage=10.0,
            hitbox_type=HitboxType.NORMAL,
        ),
    ]


def _grab_hitbox() -> list[Hitbox]:
    return [
        Hitbox(
            frame_start=0, frame_end=22,
            offset_x=55, offset_y=0, width=95, height=100,
            angle_deg=ANGLE_HORIZONTAL,
            base_knockback=0, knockback_scaling=0,
            damage=3.0,
            hitbox_type=HitboxType.SET_KNOCKBACK,
            set_knockback_val=18.0,
        ),
    ]


def _fthrow_hitbox() -> list[Hitbox]:
    return [
        Hitbox(
            frame_start=2, frame_end=8,
            offset_x=35, offset_y=0, width=30, height=40,
            angle_deg=ANGLE_HORIZONTAL,
            base_knockback=25, knockback_scaling=0.6,
            damage=6.0,
            hitbox_type=HitboxType.NORMAL,
        ),
    ]


def _bthrow_hitbox() -> list[Hitbox]:
    return [
        Hitbox(
            frame_start=2, frame_end=8,
            offset_x=-35, offset_y=0, width=30, height=40,
            angle_deg=180,
            base_knockback=28, knockback_scaling=0.65,
            damage=7.0,
            hitbox_type=HitboxType.NORMAL,
        ),
    ]


def _uthrow_hitbox() -> list[Hitbox]:
    return [
        Hitbox(
            frame_start=2, frame_end=8,
            offset_x=0, offset_y=-25, width=35, height=30,
            angle_deg=ANGLE_UP,
            base_knockback=30, knockback_scaling=0.7,
            damage=8.0,
            hitbox_type=HitboxType.NORMAL,
        ),
    ]


def _dthrow_hitbox() -> list[Hitbox]:
    return [
        Hitbox(
            frame_start=2, frame_end=8,
            offset_x=0, offset_y=25, width=35, height=25,
            angle_deg=ANGLE_DIAG_DOWN,
            base_knockback=22, knockback_scaling=0.55,
            damage=5.0,
            hitbox_type=HitboxType.NORMAL,
        ),
    ]


ATTACKS: dict[str, list[Hitbox]] = {
    "jab": _jab_hitboxes(),
    "ftilt": _forward_tilt_hitbox(),
    "utilt": _up_tilt_hitbox(),
    "dtilt": _down_tilt_hitbox(),
    "fsmash": _forward_smash_hitbox(),
    "usmash": _up_smash_hitbox(),
    "dsmash": _down_smash_hitbox(),
    "nair": _neutral_aerial_hitbox(),
    "fair": _forward_aerial_hitbox(),
    "bair": _back_aerial_hitbox(),
    "uair": _up_aerial_hitbox(),
    "dair": _down_aerial_hitbox(),
    "neutral_special": _neutral_special_hitbox(),
    "side_special": _side_special_hitbox(),
    "up_special": _up_special_hitbox(),
    "down_special": _down_special_hitbox(),
    "grab": _grab_hitbox(),
    "fthrow": _fthrow_hitbox(),
    "bthrow": _bthrow_hitbox(),
    "uthrow": _uthrow_hitbox(),
    "dthrow": _dthrow_hitbox(),
}

ATTACK_IDS_PROJECTILE = frozenset({"neutral_special"})


def _projectile_hitbox() -> Hitbox:
    return Hitbox(
        frame_start=0, frame_end=999,
        offset_x=0, offset_y=0, width=24, height=24,
        angle_deg=ANGLE_SAKURAI,
        base_knockback=20, knockback_scaling=0.7,
        damage=8.0,
        hitbox_type=HitboxType.NORMAL,
    )


def get_projectile_hitbox() -> Hitbox:
    return _projectile_hitbox()


def get_attack_hitboxes(attack_id: str, charge_mult: float = 1.0) -> list[Hitbox]:
    if attack_id in ("fsmash", "usmash", "dsmash"):
        builders = {
            "fsmash": _forward_smash_hitbox,
            "usmash": _up_smash_hitbox,
            "dsmash": _down_smash_hitbox,
        }
        return builders[attack_id](charge_mult)
    return list(ATTACKS.get(attack_id, []))
