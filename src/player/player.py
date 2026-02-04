import math
import pygame
from player.stats import Stats
from combat.hitbox_sprite import HitboxSprite
from combat.knockback import decay_launch_speed

class Player(pygame.sprite.Sprite):
    STALE_QUEUE_MAX = 9
    STALE_DECAY_PER_USE = 0.09
    CROUCH_CANCEL_MULT = 0.67
    BLAST_MARGIN = 250
    RESPAWN_INVULN_FRAMES = 120

    def __init__(self, start_pos, color, controls, screen_size):
        super().__init__()
        self.screen_width, self.screen_height = screen_size
        self.color = color

        self.image = pygame.Surface((50, 50))
        self.image.fill(color)
        self.rect = self.image.get_rect(topleft=start_pos)
        self.spawn_pos = start_pos
        self.prev_y = self.rect.y
        self.drop_through = False

        self.controls = controls
        self.speed_x = 0
        self.speed_y = 0
        self.gravity = 0.5
        self.move_speed = 5
        self.jump_count = 0
        self.jump_max = 2
        self.jump_force = -12

        self.stats = Stats(weight=1.0)
        self.lives = 3
        self.state = "idle"
        self.hitstun = 0
        self.facing_right = True
        self.tumbling = False
        self.crouching = False
        self.di_angle_rad = None
        self.stale_queue = []
        self.gravity_for_kb = 0.05
        self.respawn_invuln = 0

    def respawn(self):
        self.rect.topleft = self.spawn_pos
        self.speed_x = 0
        self.speed_y = 0
        self.hitstun = 0
        self.tumbling = False
        self.crouching = False
        self.on_ground = False
        self.jump_count = 0
        self.stats.percent = 0
        self.state = "idle"
        self.respawn_invuln = self.RESPAWN_INVULN_FRAMES

    def update_di(self):
        keys = pygame.key.get_pressed()
        dx = 1 if keys[self.controls["right"]] else (-1 if keys[self.controls["left"]] else 0)
        dy = 1 if keys[self.controls["jump"]] else (-1 if keys[self.controls.get("down", pygame.K_s)] else 0)
        if dx != 0 or dy != 0:
            self.di_angle_rad = math.atan2(dy, dx)
        else:
            self.di_angle_rad = None

    def get_di_angle_rad(self):
        return self.di_angle_rad

    def get_stale_damage_mult(self, attack_id: str) -> float:
        n = self.stale_queue.count(attack_id)
        mult = 1.0 - self.STALE_DECAY_PER_USE * min(self.STALE_QUEUE_MAX, n)
        return max(0.1, mult)

    def push_stale(self, attack_id: str):
        self.stale_queue.append(attack_id)
        if len(self.stale_queue) > self.STALE_QUEUE_MAX:
            self.stale_queue.pop(0)

    def handle_input(self):
        if self.lives <= 0:
            return
        if self.hitstun > 0:
            return
        keys = pygame.key.get_pressed()
        self.speed_x = 0

        if keys[self.controls["left"]]:
            self.speed_x = -self.move_speed
            self.facing_right = False
        if keys[self.controls["right"]]:
            self.speed_x = self.move_speed
            self.facing_right = True

        self.drop_through = keys[self.controls.get("down", pygame.K_s)] and keys[self.controls["jump"]]

    def start_attack(self, attack_id: str, hitboxes_group, charge_mult: float = 1.0):
        hb = HitboxSprite(owner=self, attack_id=attack_id, charge_mult=charge_mult)
        hitboxes_group.add(hb)


    def jump(self):
        if self.jump_count < self.jump_max:
            self.speed_y = self.jump_force * (1.1 if self.jump_count > 0 else 1)
            self.jump_count += 1
            self.drop_through = False

    KNOCKBACK_SCALE = 5.0

    def receive_hit(self, hit_result):
        if self.respawn_invuln > 0:
            return
        self.stats.take_damage(hit_result.damage_dealt)
        self.speed_x = hit_result.velocity_x * self.KNOCKBACK_SCALE
        self.speed_y = hit_result.velocity_y * self.KNOCKBACK_SCALE
        self.hitstun = hit_result.hitstun_frames
        self.tumbling = hit_result.tumble
        self.state = "hitstun"



    def update(self, others=[]):
        if self.lives <= 0:
            return
        self.update_di()
        self.prev_y = self.rect.y
        self.on_ground = False
        if self.respawn_invuln > 0:
            self.respawn_invuln -= 1

        if self.hitstun > 0:
            self.hitstun -= 1
            self.speed_x, self.speed_y = decay_launch_speed(self.speed_x, self.speed_y)
        else:
            self.tumbling = False

        self.crouching = False
        self.speed_y += self.gravity

        self.rect.x += int(self.speed_x)
        self.rect.y += int(self.speed_y)

        for other in others:
            if not hasattr(other, "rect"):
                continue

            if not self.rect.colliderect(other.rect):
                continue

            one_way = getattr(other, "one_way", False)
            if one_way:
                if (
                    self.speed_y > 0 and
                    self.prev_y + self.rect.height <= other.rect.top and
                    not self.drop_through
                ):
                    self.rect.bottom = other.rect.top
                    self.speed_y = 0
                    self.jump_count = 0
                    self.on_ground = True
            else:
                if self.speed_y > 0:
                    self.rect.bottom = other.rect.top
                    self.speed_y = 0
                    self.jump_count = 0
                    self.on_ground = True
                elif self.speed_y < 0:
                    self.rect.top = other.rect.bottom
                    self.speed_y = 0
        down_key = self.controls.get("down", pygame.K_s)
        if self.on_ground and pygame.key.get_pressed()[down_key]:
            self.crouching = True

        if (
            self.rect.right < -self.BLAST_MARGIN
            or self.rect.left > self.screen_width + self.BLAST_MARGIN
            or self.rect.bottom < -self.BLAST_MARGIN
            or self.rect.top > self.screen_height + self.BLAST_MARGIN
        ):
            self.lives -= 1
            if self.lives > 0:
                self.respawn()
            else:
                self.rect.center = (-999, -999)
