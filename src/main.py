import pygame
from player.player import Player

pygame.init()
WIDTH, HEIGHT = 1920, 1080
screen = pygame.display.set_mode((WIDTH, HEIGHT), pygame.FULLSCREEN)
clock = pygame.time.Clock()

player1 = Player(start_pos=(100, 300), color=(255, 0, 0), controls={"left":pygame.K_q,"right":pygame.K_d,"jump":pygame.K_SPACE}, screen_size = (WIDTH, HEIGHT))
player2 = Player(start_pos=(300, 300), color=(0, 0, 255), controls={"left":pygame.K_LEFT,"right":pygame.K_RIGHT,"jump":pygame.K_UP}, screen_size = (WIDTH, HEIGHT))

players = pygame.sprite.Group(player1, player2)

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

    player1.handle_input()
    player2.handle_input()
    player1.update([player2])
    player2.update([player1])

    players.draw(screen)

    pygame.display.flip()

    clock.tick(60)

pygame.quit()