import pygame

class Player(object):
    def __init__(self):

        self.speed = [0, 0]
        self.gravity = 0.5

        self.w = 50
        self.h = 50
        self.x = 960
        self.y = 540
        self.color = (255, 255, 255)
        
    def move(self):
        self.speed[1] += self.gravity
        self.x += self.speed[0]
        self.y += self.speed[1]
    
    
    def draw(self, screen):
        player_rect = pygame.draw.rect(screen, self.color, (self.x, self.y, self.w, self.h))
