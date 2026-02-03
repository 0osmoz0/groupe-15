import pygame 

class Platform(pygame.sprite.Sprite):
    def __init__(self, size, pos, one_way=False):
        super().__init__()
        self.image = pygame.Surface(size)
        self.image.fill((180, 180, 180))
        self.rect = self.image.get_rect(topleft=pos)
        self.one_way = one_way
