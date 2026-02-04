import pygame
from player.player import Player
from smash_platform.game_platform import Platform
from combat.hitbox_sprite import HitboxSprite

pygame.init()
pygame.font.init()

WIDTH, HEIGHT = 1920, 1080
screen = pygame.display.set_mode((WIDTH, HEIGHT), pygame.FULLSCREEN)
clock = pygame.time.Clock()

try:
    FONT_PERCENT = pygame.font.SysFont("arial", 72, bold=True)
except Exception:
    FONT_PERCENT = pygame.font.Font(None, 120)

player1 = Player(
    start_pos=(WIDTH//2 - 200, HEIGHT//2),
    color=(255, 0, 0),
    controls={
        "left": pygame.K_q,
        "right": pygame.K_d,
        "jump": pygame.K_SPACE,
        "down": pygame.K_s,
        "attacking": pygame.K_f
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
        "down": pygame.K_DOWN,
        "attacking": pygame.K_m
    },
    screen_size=(WIDTH, HEIGHT)
)

players = pygame.sprite.Group(player1, player2)
platforms = pygame.sprite.Group()
hitboxes = pygame.sprite.Group()


def draw_grid(screen, spacing=100):
    for x in range(0, WIDTH, spacing):
        pygame.draw.line(screen, (40, 40, 40), (x, 0), (x, HEIGHT))
    for y in range(0, HEIGHT, spacing):
        pygame.draw.line(screen, (40, 40, 40), (0, y), (WIDTH, y))


def draw_percent_hud(surface, player, x: int, y: int, align_left: bool = True):
    percent = int(player.stats.percent)
    text = f"{percent}%"
    img = FONT_PERCENT.render(text, True, player.color)
    r = img.get_rect(midleft=(x, y) if align_left else (x, y))
    if not align_left:
        r.midright = (x, y)
    surface.blit(img, r)

MAIN_W, MAIN_H = 1000, 25
SMALL_W, SMALL_H = 220, 18

center_x = WIDTH // 2
center_y = HEIGHT // 2

platforms.add(
    Platform(
        (MAIN_W, MAIN_H),
        (center_x - MAIN_W // 2, center_y + 200)
    ),
    Platform(
        (SMALL_W, SMALL_H),
        (center_x - 350 - SMALL_W // 2, center_y),
        one_way=True
    ),
    Platform(
        (SMALL_W, SMALL_H),
        (center_x + 350 - SMALL_W // 2, center_y),
        one_way=True
    ),
)

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

            if event.key == player1.controls["attacking"]:
                player1.start_attack("jab", hitboxes)

            if event.key == player2.controls["attacking"]:
                player2.start_attack("jab", hitboxes)

    player1.handle_input()
    player2.handle_input()

    player1.update([player2] + list(platforms))
    player2.update([player1] + list(platforms))

    hitboxes.update(list(players))

    screen.fill((0, 0, 0))
    hitboxes.draw(screen)
    for hb in hitboxes:
        hb.draw_hitboxes_debug(screen)

    platforms.draw(screen)
    players.draw(screen)
    draw_grid(screen)

    draw_percent_hud(screen, player1, 80, 60, align_left=True)
    draw_percent_hud(screen, player2, WIDTH - 80, 60, align_left=False)

    pygame.display.flip()
    clock.tick(60)

pygame.quit()
