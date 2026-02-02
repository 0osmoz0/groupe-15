import pygame
from player.player import Player

pygame.init()
screen = pygame.display.set_mode((800,400))
clock = pygame.time.Clock()

player1 = Player(start_pos=(100, 500), color=(255, 0, 0), controls={"left":pygame.K_a,"right":pygame.K_d,"jump":pygame.K_SPACE})
player2 = Player(start_pos=(300, 500), color=(0, 0, 255), controls={"left":pygame.K_LEFT,"right":pygame.K_RIGHT,"jump":pygame.K_UP})



running = True
while running :
    for event in pygame.event.get() :
        if event.type == pygame.QUIT :
            running = False
        if event.type == pygame.KEYDOWN:
            if event.key == player1.controls["jump"]:
                player1.jump()
            if event.key == player2.controls["jump"]:
                player2.jump()
            
    screen.fill((0, 0, 0))

    keys = pygame.key.get_pressed()
    player1.handle_input(keys)
    player1.move(screen, others=[player2])
    player1.move(screen)
    player1.draw(screen)


    player2.handle_input(keys)
    player2.move(screen, others=[player1])
    player2.move(screen)
    player2.draw(screen)

    pygame.display.flip()
    # pygame.display.update()
    clock.tick(60)

pygame.quit()