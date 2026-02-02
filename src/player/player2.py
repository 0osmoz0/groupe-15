import pygame

class Player2(object):
    def __init__(self):

        self.speed = [0, 0]
        self.gravity = 0.5
        self.move_speed = 5

        self.rect = pygame.Rect(660, 540, 50, 50)
        self.color = (255, 0, 0)

    def handle_input(self, keys):
        self.speed[0] = 0

        if keys[pygame.K_q]:
            self.speed[0] = -self.move_speed
        if keys[pygame.K_d]:
            self.speed[0] = self.move_speed
        if keys[pygame.K_z]:
            self.speed[1] = -self.move_speed
        if keys[pygame.K_s]:
            self.speed[1] = self.move_speed
        
    def move(self, screen):
        self.speed[1] += self.gravity

        self.rect.x += self.speed[0]
        self.rect.y += self.speed[1]

        self.rect.clamp_ip(screen.get_rect())

        if self.rect.bottom >= screen.get_height():
            self.speed[1] = 0
    
    
    def draw(self, screen):
        pygame.draw.rect(screen, self.color, self.rect)
