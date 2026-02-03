class Attack:
    def __init__( self, name, damage, angle, base_kb, scaling, hitstun, startup, active, endlag, hitbox_size, hitbox_offset):
        self.name = name
        self.damage = damage
        self.angle = angle
        self.base_kb = base_kb
        self.scaling = scaling
        self.hitstun = hitstun

        self.startup = startup
        self.active = active
        self.endlag = endlag

        self.hitbox_size = hitbox_size
        self.hitbox_offset = hitbox_offset
