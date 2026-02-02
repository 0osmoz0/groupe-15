import pygame

class Player(object):
    def __init__(self, start_pos, color, controls):
        
        self.rect = pygame.Rect(*start_pos, 50, 50)
        self.color = color
        self.controls = controls
        self.speed = [0, 0] 
        self.gravity = 0.45
        self.move_speed = 5
        self.jump_count = 0
        self.jump_max = 2
        self.jump_force = -12

    def handle_input(self, keys):
        self.speed[0] = 0

        if keys[self.controls["left"]]:
            self.speed[0] = -self.move_speed
        if keys[self.controls["right"]]:
            self.speed[0] = self.move_speed
    
    def jump(self):
        if self.jump_count < self.jump_max:
            if self.jump_count == 0:
                self.speed[1] = self.jump_force
            else:
                self.speed[1] = self.jump_force * 1.1
            self.jump_count += 1
    
    def collide_with_other(self, other):
        if self.rect.colliderect(other.rect):

            if self.speed[0] > 0: 
                self.rect.right = other.rect.left
            elif self.speed[0] < 0: 
                self.rect.left = other.rect.right

            if self.speed[1] > 0 : 
                self.rect.bottom = other.rect.top
                self.speed[1] = 0

            elif self.speed [1] < 0: 
                self.rect.top = other.rect.bottom 
                self.speed[1] = 0

    def move(self, screen, others=[]):
        self.speed[1] += self.gravity

        self.rect.x += self.speed[0]
        self.rect.y += self.speed[1]


        self.rect.clamp_ip(screen.get_rect())

        for other in others:
            self.collide_with_other(other)

        if self.rect.bottom >= screen.get_height():
            self.rect.bottom = screen.get_height()
            self.speed[1] = 0
            self.jump_count = 0
    
    
    def draw(self, screen):
        pygame.draw.rect(screen, self.color, self.rect)
