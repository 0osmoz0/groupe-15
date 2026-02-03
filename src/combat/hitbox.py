import pygame

class Hitbox(pygame.sprite.Sprite):
    def __init__(self, owner, size, offset, attack):
        super().__init__()
        self.owner = owner
        self.attack = attack
        self.image = pygame.Surface(size)
        self.image.fill((255, 255, 0))
        self.rect = self.image.get_rect()
        self.offset = offset

        self.timer = 0
        self.state = "startup"
        self.active = False

    def update(self):
        self.rect.topleft = (self.owner.rect.x + self.offset[0],
                             self.owner.rect.y + self.offset[1])

        self.timer += 1
        if self.state == "startup" and self.timer >= self.attack.startup:
            self.state = "active"
            self.active = True
            self.timer = 0
        elif self.state == "active" and self.timer >= self.attack.active:
            self.state = "endlag"
            self.active = False
            self.timer = 0
        elif self.state == "endlag" and self.timer >= self.attack.endlag:
            self.kill()

    def check_collision(self, target):
        return self.active and self.rect.colliderect(target.rect)

