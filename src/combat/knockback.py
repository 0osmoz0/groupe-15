import math

LAUNCH_SPEED_FACTOR = 0.03
KNOCKBACK_DECAY = 0.051
TUMBLE_THRESHOLD = 80.0
WEIGHT_DEFAULT_KB = 100


class KnockbackResult:
    def __init__(
        self,
        knockback_units: float,
        launch_speed: float,
        angle_rad: float,
        velocity_x: float,
        velocity_y: float,
    ):
        self.knockback_units = knockback_units
        self.launch_speed = launch_speed
        self.angle_rad = angle_rad
        self.velocity_x = velocity_x
        self.velocity_y = velocity_y


def compute_knockback(
    victim_percent_after_hit: float,
    damage_dealt: float,
    victim_weight: float,
    base_knockback: float,
    knockback_scaling: float,
    angle_deg: float,
    *,
    set_knockback: bool = False,
    set_knockback_p: float = 10.0,
    weight_independent: bool = False,
    launch_rate: float = 1.0,
    rage_mult: float = 1.0,
    crouch_cancel: float = 1.0,
) -> KnockbackResult:
    if set_knockback:
        p = set_knockback_p
        d = set_knockback_p
    else:
        p = victim_percent_after_hit
        d = damage_dealt

    w = WEIGHT_DEFAULT_KB if weight_independent else victim_weight
    s = knockback_scaling
    b = base_knockback

    damage_term = (p / 10.0) + (p * d / 20.0)
    weight_factor = 200.0 / (w + 100.0)
    knockback_units = ((damage_term * weight_factor * 1.4 + 18.0) * s) + b
    r = launch_rate * rage_mult * crouch_cancel
    knockback_units = knockback_units * r

    knockback_units = max(0.0, knockback_units)

    launch_speed = knockback_units * LAUNCH_SPEED_FACTOR

    angle_rad = math.radians(angle_deg)
    velocity_x = launch_speed * math.cos(angle_rad)
    velocity_y = launch_speed * math.sin(angle_rad)

    return KnockbackResult(
        knockback_units=knockback_units,
        launch_speed=launch_speed,
        angle_rad=angle_rad,
        velocity_x=velocity_x,
        velocity_y=velocity_y,
    )


def apply_directional_influence(
    velocity_x: float,
    velocity_y: float,
    original_angle_rad: float,
    di_angle_rad: float,
    di_strength: float = 1.0,
) -> tuple[float, float]:
    speed = math.hypot(velocity_x, velocity_y)
    if speed <= 0:
        return velocity_x, velocity_y

    new_angle = original_angle_rad + (di_angle_rad - original_angle_rad) * di_strength
    return (
        speed * math.cos(new_angle),
        speed * math.sin(new_angle),
    )


def decay_launch_speed(current_vx: float, current_vy: float) -> tuple[float, float]:
    speed = math.hypot(current_vx, current_vy)
    if speed <= 0:
        return 0.0, 0.0
    new_speed = max(0.0, speed - KNOCKBACK_DECAY)
    if new_speed <= 0:
        return 0.0, 0.0
    scale = new_speed / speed
    return current_vx * scale, current_vy * scale


def causes_tumble(knockback_units: float) -> bool:
    return knockback_units >= TUMBLE_THRESHOLD


def apply_gravity_modifier_tumble(
    velocity_x: float,
    velocity_y: float,
    victim_gravity: float,
) -> tuple[float, float]:
    """
    Brawl onward: en tumble, la gravité de la cible modifie la vélocité verticale.
    (g - 0.075) * 5 → plus la gravité est haute, plus le lancement vertical est fort.
    """
    if victim_gravity <= 0:
        return velocity_x, velocity_y
    factor = 1.0 + (victim_gravity - 0.075) * 5.0
    factor = max(0.5, min(1.5, factor))
    return velocity_x, velocity_y * factor


def compute_rage_mult(attacker_percent: float, rage_start: float = 35.0, rage_cap: float = 150.0, rage_max_mult: float = 1.1) -> float:
    """
    Ultimate: rage entre 35% et 150% → mult 1.0 à 1.1.
    """
    if attacker_percent < rage_start:
        return 1.0
    t = (attacker_percent - rage_start) / (rage_cap - rage_start)
    t = min(1.0, max(0.0, t))
    return 1.0 + t * (rage_max_mult - 1.0)
