from combat.attack import Attack

JAB = Attack(
    name="Jab",
    damage=3,
    angle=45,
    base_kb=3,
    scaling=1.2,
    hitstun=10,
    startup=3,
    active=4,
    endlag=10,
    hitbox_size=(30, 20),
    hitbox_offset=(35, 0)
)
