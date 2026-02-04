import pygame

class Platform(pygame.sprite.Sprite):
    def __init__(self, size, pos, one_way=False, image=None, surface_offset=0):
        super().__init__()
        if image is not None:
            self.image = image
        else:
            self.image = pygame.Surface(size)
            self.image.fill((180, 180, 180))
        self.rect = self.image.get_rect(topleft=pos)
        self.one_way = one_way
        self.surface_offset = surface_offset

    def surface_top(self):
        """Y du haut de la surface marchable (pour collision alignée sur l'image)."""
        return self.rect.top + self.surface_offset
