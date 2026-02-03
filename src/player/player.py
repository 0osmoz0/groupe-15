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
        self.drop_through = False

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
        
        self.drop_through = keys[self.controls.get("down", pygame.K_s)] and keys[self.controls["jump"]]

    def jump(self):
        if self.jump_count < self.jump_max:
            self.speed_y = self.jump_force * (1.1 if self.jump_count > 0 else 1)
            self.jump_count += 1
            self.drop_through = False

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
                print(f"Collision with {other} | one_way={getattr(other, 'one_way', False)}")
                print(f"prev_y={self.prev_y}, rect.top={self.rect.top}, rect.bottom={self.rect.bottom}, speed_y={self.speed_y}, drop_through={self.drop_through}")

                if getattr(other, "one_way", False):
                    if self.speed_y > 0 and self.prev_y + self.rect.height <= other.rect.top + 5 and not self.drop_through:
                        print("Landing on one_way platform")
                        self.rect.bottom = other.rect.top
                        self.speed_y = 0
                        self.jump_count = 0
                    else:
                        print("Ignoring one_way platform (from below or drop-through)")
                else:
                    if self.speed_y > 0:
                        print("Landing on normal platform")
                        self.rect.bottom = other.rect.top
                        self.speed_y = 0
                        self.jump_count = 0
                    elif self.speed_y < 0:
                        print("Hitting head on normal platform")
                        self.rect.top = other.rect.bottom
                        self.speed_y = 0

        # Limites écran
        if self.rect.top < 0:
            self.rect.top = 0
            self.speed_y = 0
        if self.rect.bottom >= self.screen_height:
            self.rect.bottom = self.screen_height
            self.speed_y = 0
            self.jump_count = 0
