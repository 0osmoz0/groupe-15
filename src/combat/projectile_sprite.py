import pygame
from .attacks_data import get_projectile_hitbox
from .attack import (
    resolve_hit,
    check_hitbox_vs_circle,
    VictimStats,
)

HURTBOX_RADIUS = 25
PROJECTILE_SPEED = 14
PROJECTILE_LIFETIME = 90
PROJECTILE_SIZE = 20


class ProjectileSprite(pygame.sprite.Sprite):
    def __init__(self, owner, hitboxes_group):
        super().__init__()
        self.owner = owner
        self.hitbox = get_projectile_hitbox()
        self.hit_players = set()
        facing_right = getattr(owner, "facing_right", True)
        self.velocity_x = PROJECTILE_SPEED if facing_right else -PROJECTILE_SPEED
        self.velocity_y = 0
        self.lifetime = PROJECTILE_LIFETIME
        self.facing_right = facing_right

        r = getattr(owner, "rect", pygame.Rect(0, 0, 50, 50))
        start_x = r.centerx + (45 if facing_right else -45)
        start_y = r.centery
        self.image = pygame.Surface((PROJECTILE_SIZE, PROJECTILE_SIZE))
        self.image.fill(owner.color if hasattr(owner, "color") else (200, 200, 0))
        self.rect = self.image.get_rect(center=(start_x, start_y))
        hitboxes_group.add(self)

    def update(self, potential_victims=None):
        potential_victims = potential_victims or []
        self.rect.x += int(self.velocity_x)
        self.rect.y += int(self.velocity_y)
        self.lifetime -= 1

        if self.lifetime <= 0:
            self.kill()
            return

        hx, hy = self.rect.centerx, self.rect.centery
        for victim in potential_victims:
            if victim is self.owner:
                continue
            if not getattr(victim, "rect", None):
                continue
            if getattr(victim, "respawn_invuln", 0) > 0:
                continue
            if getattr(victim, "lives", 1) <= 0:
                continue
            if id(victim) in self.hit_players:
                continue
            vx, vy = victim.rect.centerx, victim.rect.centery
            if not check_hitbox_vs_circle(
                self.hitbox, hx, hy, vx, vy, HURTBOX_RADIUS, self.facing_right
            ):
                continue
            w = getattr(victim.stats, "weight", 1.0)
            crouch_cancel = victim.CROUCH_CANCEL_MULT if getattr(victim, "crouching", False) else 1.0
            victim_stats = VictimStats(
                current_percent=getattr(victim.stats, "percent", 0),
                weight=w * 100.0 if w < 50 else w,
                crouch_cancel=crouch_cancel,
            )
            attacker_percent = getattr(self.owner.stats, "percent", 0)
            victim_gravity = getattr(victim, "gravity_for_kb", 0.05)
            stale_mult = self.owner.get_stale_damage_mult("neutral_special") if hasattr(self.owner, "get_stale_damage_mult") else 1.0
            di_angle = victim.get_di_angle_rad() if hasattr(victim, "get_di_angle_rad") else None
            result = resolve_hit(
                self.hitbox,
                victim_stats,
                self.facing_right,
                di_angle_rad=di_angle,
                di_strength=0.18,
                hitstun_style="ultimate",
                attacker_percent=attacker_percent,
                victim_gravity=victim_gravity,
                stale_damage_mult=stale_mult,
            )
            if result is not None:
                victim.receive_hit(result)
                if hasattr(self.owner, "push_stale"):
                    self.owner.push_stale("neutral_special")
                self.hit_players.add(id(victim))
            self.kill()
            return

    def draw_debug(self, surface):
        pygame.draw.rect(surface, (255, 255, 0), self.rect, 1)

    def draw_hitboxes_debug(self, surface):
        self.draw_debug(surface)
