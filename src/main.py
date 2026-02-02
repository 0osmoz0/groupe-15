import pygame
from player.player import Player
from player.player2 import Player2

pygame.init()
screen = pygame.display.set_mode((1920,1080), pygame.FULLSCREEN)
clock = pygame.time.Clock()

player = Player()
player2 = Player2()


running = True
while running :
    for event in pygame.event.get() :
        if event.type == pygame.QUIT :
            running = False
            
    screen.fill((0, 0, 0))

    player.move(screen)
    player.draw(screen)

    player2.move(screen)
    player2.draw(screen)

    pygame.display.flip()
    # pygame.display.update()
    clock.tick(60)

pygame.quit()