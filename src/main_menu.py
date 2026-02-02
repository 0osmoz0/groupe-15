import pygame
from menu.settings import *
from menu.button import Button



pygame.init()
screen = pygame.display.set_mode((WIDTH, HEIGHT), pygame.FULLSCREEN)
background = pygame.image.load(BG_MENU_PATH).convert()
background = pygame.transform.scale(background, (WIDTH, HEIGHT))
pygame.display.set_caption("Mon Menu Pygame")
clock = pygame.time.Clock()

buttons = [  
    Button("Play", 860, 400, 200, 80, (255,255,255), (200,200,200)),
    Button("Quit", 860, 520, 200, 80, (255,255,255), (200,200,200)) 
    ]

running = True
while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

        for button in buttons:
            button.is_clicked(event)
        
        screen.blit(background, (0, 0))
           
        for button in buttons:
            button.draw(screen)

        pygame.display.flip()
        clock.tick(FPS)

pygame.quit()
