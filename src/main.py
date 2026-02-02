import pygame
from settings import *
from menu import menu_loop

def main():
    pygame.init()
    screen = pygame.display.set_mode((WIDTH, HEIGHT))
    pygame.display.set_caption("Mon Menu Pygame")
    
    menu_loop(screen)

if __name__ == "__main__":
    main()