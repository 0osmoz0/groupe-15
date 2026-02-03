import pygame

class Player(pygame.sprite.Sprite):
    def __init__(self, start_pos, color, controls, screen_size):
        super().__init__()
        self.screen_width, self.screen_height = screen_size
        self.color = color

        self.image = pygame.Surface((50, 50))
        self.image.fill(color)
        self.rect = self.image.get_rect(topleft=start_pos)
        self.prevy = self.rect.y

        self.controls = controls
        self.speed_x = 0
        self.speed_y = 0
        self.gravity = 0.5
        self.move_speed = 5
        self.jump_count = 0
        self.jump_max = 2
        self.jump_force = -12

    def handle_input(self):
        keys = pygame.key.get_pressed()
        self.speed_x = 0
        if keys[self.controls["left"]]:
            self.speed_x = -self.move_speed
        if keys[self.controls["right"]]:
            self.speed_x = self.move_speed

    def jump(self):
        if self.jump_count < self.jump_max:
            self.speed_y = self.jump_force * (1.1 if self.jump_count > 0 else 1)
            self.jump_count += 1

    def update(self, others=[]):
        self.prev_y = self.rect.y
        self.rect.x += self.speed_x

        for other in others:
            if self.rect.colliderect(other.rect):
                if self.speed_x > 0:
                    self.rect.right = other.rect.left
                elif self.speed_x < 0:
                    self.rect.left = other.rect.right


        self.rect.left = max(self.rect.left, 0)
        self.rect.right = min(self.rect.right, self.screen_width)


        self.speed_y += self.gravity
        self.rect.y += self.speed_y

        for other in others:
            if self.rect.colliderect(other.rect):
                if (
                    self.speed_y > 0 and
                    self.prev_y + self.rect.height <= other.rect.top
                ):
                    self.rect.bottom = self.rect.top
                    self.speed_y = 0
                    self.jump_count = 0

        if self.rect.top < 0:
            self.rect.top = 0
            self.speed_y = 0

        if self.rect.bottom >= self.screen_height:
            self.rect.bottom = self.screen_height
            self.speed_y = 0
            self.jump_count = 0
