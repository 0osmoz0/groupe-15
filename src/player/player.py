import pygame

class Player(object):
    def __init__(self):

        self.speed = [0, 0] 
        self.gravity = 0.45
        self.move_speed = 5
        self.jump_count = 0
        self.jump_max = 2
        self.jump_force = -12

        self.rect = pygame.Rect(960, 540, 50, 50)
        self.color = (255, 255, 255)

    def handle_input(self, keys):
        self.speed[0] = 0

        if keys[pygame.K_LEFT]:
            self.speed[0] = -self.move_speed
        if keys[pygame.K_RIGHT]:
            self.speed[0] = self.move_speed
    
    def jump(self):
        if self.jump_count < self.jump_max:
            if self.jump_count == 0:
                self.speed[1] = self.jump_force
            else:
                self.speed[1] = self.jump_force * 1.1
            self.jump_count += 1

        
    def move(self, screen):
        self.speed[1] += self.gravity

        self.rect.x += self.speed[0]
        self.rect.y += self.speed[1]


        self.rect.clamp_ip(screen.get_rect())

        if self.rect.bottom >= screen.get_height():
            self.rect.bottom = screen.get_height()
            self.speed[1] = 0
            self.jump_count = 0
    
    
    def draw(self, screen):
        pygame.draw.rect(screen, self.color, self.rect)
