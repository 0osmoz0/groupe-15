HITSTUN_MULTIPLIER_MELEE = 0.4
HITSTUN_MULTIPLIER_64 = 0.533
HITSTUN_FRAME_SUBTRACT = 1
MIN_HITSTUN_FLINCH = 4


def compute_hitstun_frames(
    knockback_units: float,
    *,
    style: str = "melee",
    hitstun_modifier: int = 0,
    sent_tumbling: bool = False,
    electric_attack: bool = False,
) -> int:
    if knockback_units <= 0:
        return max(MIN_HITSTUN_FLINCH, hitstun_modifier)

    if style == "64":
        frames = knockback_units * HITSTUN_MULTIPLIER_64
    else:
        frames = knockback_units * HITSTUN_MULTIPLIER_MELEE

    if style == "smash4" or style == "ultimate":
        frames -= HITSTUN_FRAME_SUBTRACT
        if sent_tumbling and electric_attack:
            frames += 1
        elif sent_tumbling or electric_attack:
            frames += 1

    frames = int(max(0, frames))
    frames += hitstun_modifier
    return max(MIN_HITSTUN_FLINCH, frames)


def get_hitstun_style_options() -> list[str]:
    return ["melee", "64", "smash4", "ultimate"]
