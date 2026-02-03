import pygame
from player.player import Player
from smash_platform.game_platform import Platform

pygame.init()

# ------------------ CONFIG ------------------
WIDTH, HEIGHT = 1920, 1080
screen = pygame.display.set_mode((WIDTH, HEIGHT), pygame.FULLSCREEN)
clock = pygame.time.Clock()

# ------------------ JOUEURS ------------------
player1 = Player(
    start_pos=(WIDTH//2 - 200, HEIGHT//2),
    color=(255, 0, 0),
    controls={
        "left": pygame.K_q,
        "right": pygame.K_d,
        "jump": pygame.K_SPACE,
        "down": pygame.K_s
    },
    screen_size=(WIDTH, HEIGHT)
)

player2 = Player(
    start_pos=(WIDTH//2 + 200, HEIGHT//2),
    color=(0, 0, 255),
    controls={
        "left": pygame.K_LEFT,
        "right": pygame.K_RIGHT,
        "jump": pygame.K_UP,
        "down": pygame.K_DOWN
    },
    screen_size=(WIDTH, HEIGHT)
)

players = pygame.sprite.Group(player1, player2)
platforms = pygame.sprite.Group()

# ------------------ GRILLE ------------------
def draw_grid(screen, spacing=100):
    for x in range(0, WIDTH, spacing):
        pygame.draw.line(screen, (40, 40, 40), (x, 0), (x, HEIGHT))
    for y in range(0, HEIGHT, spacing):
        pygame.draw.line(screen, (40, 40, 40), (0, y), (WIDTH, y))

# ------------------ PLATEFORMES ------------------
MAIN_W, MAIN_H = 1000, 25
SMALL_W, SMALL_H = 220, 18

center_x = WIDTH // 2
center_y = HEIGHT // 2

platforms.add(
    # Plateforme principale
    Platform(
        (MAIN_W, MAIN_H),
        (center_x - MAIN_W // 2, center_y + 200)
    ),

    # Plateforme gauche (one-way)
    Platform(
        (SMALL_W, SMALL_H),
        (center_x - 350 - SMALL_W // 2, center_y),
        one_way=True
    ),

    # Plateforme droite (one-way)
    Platform(
        (SMALL_W, SMALL_H),
        (center_x + 350 - SMALL_W // 2, center_y),
        one_way=True
    ),
)

# ------------------ BOUCLE JEU ------------------
running = True
while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

        if event.type == pygame.KEYDOWN:
            if event.key == player1.controls["jump"]:
                player1.jump()
            if event.key == player2.controls["jump"]:
                player2.jump()

    screen.fill((0, 0, 0))

    player1.handle_input()
    player2.handle_input()

    player1.update([player2] + list(platforms))
    player2.update([player1] + list(platforms))

    platforms.draw(screen)
    players.draw(screen)
    draw_grid(screen)

    pygame.display.flip()
    clock.tick(60)

pygame.quit()
