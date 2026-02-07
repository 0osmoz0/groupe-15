"""
Projectile (carotte / munition Nick) : déplacement, collision avec joueurs, dégâts/knockback.
Respecte cheat_invincible_until et cheat_super_damage_until.
"""
import math
import os
import pygame
from .attacks_data import get_projectile_hitbox
from .attack import (
    resolve_hit,
    check_hitbox_vs_circle,
    VictimStats,
    HitResult,
)
from .knockback import KnockbackResult

HURTBOX_RADIUS = 25
COUNTER_DAMAGE = 6
COUNTER_HITSTUN = 18
COUNTER_LAUNCH_SPEED = 4
PROJECTILE_SPEED = 14
PROJECTILE_LIFETIME = 90
PROJECTILE_SIZE = 20
PROJECTILE_CARROT_SIZE = 90

_base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
_judy_projectile_path = os.path.join(_base_dir, "assets", "JUDY_HOPPS", "munition", "munition.png")
_nick_projectile_path = os.path.join(_base_dir, "assets", "Nick", "munition_nick", "munition.png")
_distance_attack_sound = None

def _get_distance_attack_sound():
    global _distance_attack_sound
    if _distance_attack_sound is None:
        path = os.path.join(_base_dir, "assets", "song", "combat", "distance_attack", "tilt-attack.wav")
        try:
            _distance_attack_sound = pygame.mixer.Sound(path)
        except Exception:
            _distance_attack_sound = False
    return _distance_attack_sound if _distance_attack_sound else None

_counter_sound = None

def _get_counter_sound():
    global _counter_sound
    if _counter_sound is None:
        path = os.path.join(_base_dir, "assets", "song", "combat", "counter", "dash-attack.wav")
        try:
            _counter_sound = pygame.mixer.Sound(path)
        except Exception:
            _counter_sound = False
    return _counter_sound if _counter_sound else None

_judy_projectile_image = None
_nick_projectile_image = None


def _get_judy_projectile_image():
    global _judy_projectile_image
    if _judy_projectile_image is None:
        try:
            img = pygame.image.load(_judy_projectile_path).convert_alpha()
            img = pygame.transform.smoothscale(img, (PROJECTILE_CARROT_SIZE, PROJECTILE_CARROT_SIZE))
            _judy_projectile_image = pygame.transform.flip(img, True, False)
        except Exception:
            _judy_projectile_image = False
    return _judy_projectile_image if _judy_projectile_image else None


def _get_nick_projectile_image():
    global _nick_projectile_image
    if _nick_projectile_image is None:
        try:
            img = pygame.image.load(_nick_projectile_path).convert_alpha()
            img = pygame.transform.smoothscale(img, (PROJECTILE_CARROT_SIZE, PROJECTILE_CARROT_SIZE))
            _nick_projectile_image = pygame.transform.flip(img, True, False)
        except Exception:
            _nick_projectile_image = False
    return _nick_projectile_image if _nick_projectile_image else None


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

        character = getattr(owner, "character", None)
        if character == "judy":
            judy_img = _get_judy_projectile_image()
            if judy_img is not None:
                self.image = pygame.transform.flip(judy_img, not facing_right, False).copy()
            else:
                self.image = pygame.Surface((PROJECTILE_SIZE, PROJECTILE_SIZE))
                self.image.fill(owner.color if hasattr(owner, "color") else (200, 200, 0))
        elif character == "nick":
            nick_img = _get_nick_projectile_image()
            if nick_img is not None:
                self.image = pygame.transform.flip(nick_img, not facing_right, False).copy()
            else:
                self.image = pygame.Surface((PROJECTILE_SIZE, PROJECTILE_SIZE))
                self.image.fill(owner.color if hasattr(owner, "color") else (200, 200, 0))
        else:
            self.image = pygame.Surface((PROJECTILE_SIZE, PROJECTILE_SIZE))
            self.image.fill(owner.color if hasattr(owner, "color") else (200, 200, 0))

        self.rect = self.image.get_rect(center=(start_x, start_y))
        hitboxes_group.add(self)
        snd = _get_distance_attack_sound()
        if snd is not None:
            try:
                snd.set_volume(0.35)
                snd.play()
            except Exception:
                pass

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
            if getattr(victim, "cheat_invincible_until", 0) > pygame.time.get_ticks():
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
            if getattr(self.owner, "cheat_super_damage_until", 0) > pygame.time.get_ticks():
                stale_mult *= 5
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
                counter_remaining = getattr(victim, "_counter_remaining", 0)
                if counter_remaining > 0:
                    victim._counter_remaining = 0
                    snd = _get_counter_sound()
                    if snd is not None:
                        try:
                            snd.set_volume(0.4)
                            snd.play()
                        except Exception:
                            pass
                    ax, ay = self.owner.rect.centerx, self.owner.rect.centery
                    dx = ax - vx
                    dy = ay - vy
                    dist = math.sqrt(dx * dx + dy * dy) or 1.0
                    vx_out = (dx / dist) * COUNTER_LAUNCH_SPEED
                    vy_out = (dy / dist) * COUNTER_LAUNCH_SPEED
                    dummy_kb = KnockbackResult(0, 0, 0, vx_out, vy_out)
                    counter_result = HitResult(
                        COUNTER_DAMAGE,
                        dummy_kb,
                        COUNTER_HITSTUN,
                        True,
                        vx_out,
                        vy_out,
                    )
                    self.owner.receive_hit(counter_result)
                else:
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
