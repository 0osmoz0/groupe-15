import pygame
from settings import *
from button import Button
import sys

def play_game():
    print("Play pressed!")

def open_settings():
    print("Settings pressed!")

def quit_game():
    pygame.quit()
    sys.exit()

def menu_loop(screen):
    clock = pygame.time.Clock()

    play_button = Button("Play", WIDTH//2 - 100, 200, 200, 50, BLUE, GRAY, play_game)
    settings_button = Button("Settings", WIDTH//2 - 100, 300, 200, 50, BLUE, GRAY, open_settings)
    quit_button = Button("Quit", WIDTH//2 - 100, 400, 200, 50, BLUE, GRAY, quit_game)

    buttons = [play_button, settings_button, quit_button]

    running = True
    while running:
        screen.fill(WHITE)
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
                pygame.quit()
                sys.exit()
            for button in buttons:
                button.is_clicked(event)

        for button in buttons:
            button.draw(screen)

        pygame.display.flip()
        clock.tick(FPS)
import pygame
from settings import *
from button import Button
import sys

def play_game():
    print("Play pressed!")

def open_settings():
    print("Settings pressed!")

def quit_game():
    pygame.quit()
    sys.exit()

def menu_loop(screen):
    clock = pygame.time.Clock()

    play_button = Button("Play", WIDTH//2 - 100, 200, 200, 50, BLUE, GRAY, play_game)
    settings_button = Button("Settings", WIDTH//2 - 100, 300, 200, 50, BLUE, GRAY, open_settings)
    quit_button = Button("Quit", WIDTH//2 - 100, 400, 200, 50, BLUE, GRAY, quit_game)

    buttons = [play_button, settings_button, quit_button]

    running = True
    while running:
        screen.fill(WHITE)
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
                pygame.quit()
                sys.exit()
            for button in buttons:
                button.is_clicked(event)

        for button in buttons:
            button.draw(screen)

        pygame.display.flip()
        clock.tick(FPS)