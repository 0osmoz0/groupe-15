import math
import pygame
from .attacks_data import get_attack_hitboxes
from .attack import (
    resolve_hit,
    get_active_hitboxes,
    check_hitbox_vs_circle,
    ActiveAttack,
    VictimStats,
    HitResult,
)
from .knockback import KnockbackResult

HURTBOX_RADIUS = 25
COUNTER_DAMAGE = 6
COUNTER_HITSTUN = 18
COUNTER_LAUNCH_SPEED = 4


class HitboxSprite(pygame.sprite.Sprite):

    def __init__(self, owner, attack_id: str, charge_mult: float = 1.0):
        super().__init__()
        self.owner = owner
        self.attack_id = attack_id
        self.hitboxes = get_attack_hitboxes(attack_id, charge_mult)
        if not self.hitboxes:
            self.total_frames = 1
        else:
            self.total_frames = max(h.frame_end for h in self.hitboxes) + 15
        self.current_frame = 0
        self.hit_this_attack = set()

        self.image = pygame.Surface((1, 1))
        self.image.set_alpha(0)
        self.rect = self.image.get_rect(center=getattr(owner, "rect", pygame.Rect(0, 0, 50, 50)).center)
        self.debug_draw = True

    def _owner_center(self):
        r = getattr(self.owner, "rect", None)
        if r is None:
            return 0, 0
        return r.centerx, r.centery

    def _owner_facing_right(self) -> bool:
        return getattr(self.owner, "facing_right", True)

    def update(self, potential_victims=None):
        potential_victims = potential_victims or []
        ox, oy = self._owner_center()
        facing_right = self._owner_facing_right()

        active = get_active_hitboxes(
            ActiveAttack(
                attack_id=self.attack_id,
                current_frame=self.current_frame,
                total_frames=self.total_frames,
                hitboxes=self.hitboxes,
                hit_this_attack=self.hit_this_attack,
            )
        )

        for victim in potential_victims:
            if victim is self.owner:
                continue
            if not getattr(victim, "rect", None):
                continue
            if getattr(victim, "respawn_invuln", 0) > 0:
                continue
            vx, vy = victim.rect.centerx, victim.rect.centery

            for hb in active:
                if (id(victim), id(hb)) in self.hit_this_attack:
                    continue
                sign = 1 if facing_right else -1
                hb_wx = ox + hb.offset_x * sign
                hb_wy = oy + hb.offset_y
                if not check_hitbox_vs_circle(
                    hb, hb_wx, hb_wy, vx, vy, HURTBOX_RADIUS, facing_right
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
                stale_mult = self.owner.get_stale_damage_mult(self.attack_id) if hasattr(self.owner, "get_stale_damage_mult") else 1.0
                di_angle = victim.get_di_angle_rad() if hasattr(victim, "get_di_angle_rad") else None
                result = resolve_hit(
                    hb,
                    victim_stats,
                    facing_right,
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
                            self.owner.push_stale(self.attack_id)
                    self.hit_this_attack.add((id(victim), id(hb)))
                break

        self.current_frame += 1
        if self.current_frame >= self.total_frames:
            self.kill()
        else:
            self.rect.center = self._owner_center()

    def draw_hitboxes_debug(self, surface):
        if not getattr(self, "debug_draw", False):
            return
        ox, oy = self._owner_center()
        sign = 1 if self._owner_facing_right() else -1
        active = get_active_hitboxes(
            ActiveAttack(
                attack_id=self.attack_id,
                current_frame=self.current_frame,
                total_frames=self.total_frames,
                hitboxes=self.hitboxes,
                hit_this_attack=self.hit_this_attack,
            )
        )
        for hb in active:
            hx = ox + hb.offset_x * sign
            hy = oy + hb.offset_y
            rect = pygame.Rect(
                hx - hb.width / 2, hy - hb.height / 2,
                hb.width, hb.height
            )
            s = pygame.Surface((rect.width, rect.height))
            s.set_alpha(80)
            s.fill((0, 255, 0))
            surface.blit(s, rect.topleft)
            pygame.draw.rect(surface, (0, 255, 0), rect, 1)
