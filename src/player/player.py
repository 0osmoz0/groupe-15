import pygame
from player.stats import Stats
from combat.hitbox_sprite import HitboxSprite
from combat.knockback import decay_launch_speed

class Player(pygame.sprite.Sprite):
    def __init__(self, start_pos, color, controls, screen_size):
        super().__init__()
        self.screen_width, self.screen_height = screen_size
        self.color = color

        self.image = pygame.Surface((50, 50))
        self.image.fill(color)
        self.rect = self.image.get_rect(topleft=start_pos)
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
        self.state = "idle"
        self.hitstun = 0
        self.facing_right = True

    def handle_input(self):
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
        self.stats.take_damage(hit_result.damage_dealt)
        self.speed_x = hit_result.velocity_x * self.KNOCKBACK_SCALE
        self.speed_y = hit_result.velocity_y * self.KNOCKBACK_SCALE
        self.hitstun = hit_result.hitstun_frames
        self.state = "hitstun"



    def update(self, others=[]):
        self.prev_y = self.rect.y

        if self.hitstun > 0:
            self.hitstun -= 1
            self.speed_x, self.speed_y = decay_launch_speed(self.speed_x, self.speed_y)

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
            else:
                if self.speed_y > 0:
                    self.rect.bottom = other.rect.top
                    self.speed_y = 0
                    self.jump_count = 0
                elif self.speed_y < 0:
                    self.rect.top = other.rect.bottom
                    self.speed_y = 0
        if self.rect.left < 0:
            self.rect.left = 0
        if self.rect.right > self.screen_width:
            self.rect.right = self.screen_width

        if self.rect.top < 0:
            self.rect.top = 0
            self.speed_y = 0

        if self.rect.bottom > self.screen_height:
            self.rect.bottom = self.screen_height
            self.speed_y = 0
            self.jump_count = 0
