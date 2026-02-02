import pygame

class Player(object):
    def __init__(self):

        self.speed = [0, 0]
        self.gravity = 0.5

        self.rect = pygame.Rect(960, 540, 50, 50)
        self.color = (255, 255, 255)
        
    def move(self, screen):
        self.speed[1] += self.gravity

        self.rect.x += self.speed[0]
        self.rect.y += self.speed[1]

        self.rect.clamp_ip(screen.get_rect())

        if self.rect.bottom >= screen.get_height():
            self.speed[1] = 0
    
    
    def draw(self, screen):
        pygame.draw.rect(screen, self.color, self.rect)
