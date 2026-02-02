import pygame
from pygame.locals import *

pygame.init()
screen = pygame.display.set_mode((1920,1080), pygame.FULLSCREEN)
clock = pygame.time.Clock()
red = (255, 0, 0)

running = True
while running :
    for event in pygame.event.get() :
        if event.type == pygame.QUIT :
            running = False
            
    screen.fill((0, 0, 0))
    pygame.draw.rect(screen, red, [100, 100, 100, 100], 2)

    pygame.display.flip()
    # pygame.display.update()
    clock.tick(60)

pygame.quit()