import pygame

class Player(object):
    def __init__(self):

        self.w = 50
        self.h = 50
        self.x = 960
        self.y = 540
        self.color = (255, 255, 255)
    
    def draw(self, screen):
        player_rect = pygame.draw.rect(screen, self.color, (self.x, self.y, self.w, self.h))
