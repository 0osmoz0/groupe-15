import math

def compute_knockback(damage, percent, base, scaling, angle, weight):
    force = (base + scaling * percent) / weight
    rad = math.radians(angle)
    return (
        math.cos(rad) * force,
        -math.sin(rad) * force
    )