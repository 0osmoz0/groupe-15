import pygame
from player.player import Player
from smash_platform.game_platform import Platform
from combat.hitbox_sprite import HitboxSprite
from combat.projectile_sprite import ProjectileSprite

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
        "attacking": pygame.K_f,
        "special": pygame.K_e,
        "grab": pygame.K_g,
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
        "attacking": pygame.K_m,
        "special": pygame.K_i,
        "grab": pygame.K_o,
    },
    screen_size=(WIDTH, HEIGHT)
)

players = pygame.sprite.Group(player1, player2)
platforms = pygame.sprite.Group()
hitboxes = pygame.sprite.Group()


def _start_attack_from_input(player, keys, hitboxes, jab, ftilt, utilt, dtilt, nair, fair, bair, uair, dair):
    left = keys[player.controls["left"]]
    right = keys[player.controls["right"]]
    up = keys[player.controls["jump"]]
    down = keys[player.controls["down"]]
    on_ground = getattr(player, "on_ground", True)
    facing_right = getattr(player, "facing_right", True)
    if on_ground:
        if up:
            player.start_attack(utilt, hitboxes)
        elif down:
            player.start_attack(dtilt, hitboxes)
        elif left or right:
            player.start_attack(ftilt, hitboxes)
        else:
            player.start_attack(jab, hitboxes)
    else:
        if up:
            player.start_attack(uair, hitboxes)
        elif down:
            player.start_attack(dair, hitboxes)
        elif (right and facing_right) or (left and not facing_right):
            player.start_attack(fair, hitboxes)
        elif (left and facing_right) or (right and not facing_right):
            player.start_attack(bair, hitboxes)
        else:
            player.start_attack(nair, hitboxes)


def draw_percent_hud(surface, player, x: int, y: int, align_left: bool = True):
    percent = int(player.stats.percent)
    lives = player.lives
    color = player.color if lives > 0 else (100, 100, 100)
    text_stocks = f"{lives}"
    text_percent = f"{percent}%"
    img_stocks = FONT_PERCENT.render(text_stocks, True, color)
    img_percent = FONT_PERCENT.render(text_percent, True, color)
    if align_left:
        r_stocks = img_stocks.get_rect(midleft=(x, y))
        surface.blit(img_stocks, r_stocks)
        r_percent = img_percent.get_rect(midleft=(r_stocks.right + 20, y))
        surface.blit(img_percent, r_percent)
    else:
        r_percent = img_percent.get_rect(midright=(x, y))
        surface.blit(img_percent, r_percent)
        r_stocks = img_stocks.get_rect(midright=(r_percent.left - 20, y))
        surface.blit(img_stocks, r_stocks)

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
            keys = pygame.key.get_pressed()
            if event.key == player1.controls["jump"]:
                player1.jump()
            if event.key == player2.controls["jump"]:
                player2.jump()

            if event.key == player1.controls["attacking"] and player1.lives > 0:
                _start_attack_from_input(player1, keys, hitboxes, "jab", "ftilt", "utilt", "dtilt", "nair", "fair", "bair", "uair", "dair")
            if event.key == player2.controls["attacking"] and player2.lives > 0:
                _start_attack_from_input(player2, keys, hitboxes, "jab", "ftilt", "utilt", "dtilt", "nair", "fair", "bair", "uair", "dair")

            if event.key == player1.controls.get("grab") and player1.lives > 0:
                player1.start_attack("grab", hitboxes)
            if event.key == player2.controls.get("grab") and player2.lives > 0:
                player2.start_attack("grab", hitboxes)

            if event.key == player1.controls.get("special") and player1.lives > 0:
                if keys[player1.controls["left"]] or keys[player1.controls["right"]]:
                    player1.start_attack("side_special", hitboxes)
                elif keys[player1.controls["jump"]]:
                    player1.start_attack("up_special", hitboxes)
                elif keys[player1.controls["down"]]:
                    player1.start_attack("down_special", hitboxes)
                else:
                    ProjectileSprite(player1, hitboxes)
            if event.key == player2.controls.get("special") and player2.lives > 0:
                if keys[player2.controls["left"]] or keys[player2.controls["right"]]:
                    player2.start_attack("side_special", hitboxes)
                elif keys[player2.controls["jump"]]:
                    player2.start_attack("up_special", hitboxes)
                elif keys[player2.controls["down"]]:
                    player2.start_attack("down_special", hitboxes)
                else:
                    ProjectileSprite(player2, hitboxes)

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

    draw_percent_hud(screen, player1, 80, 60, align_left=True)
    draw_percent_hud(screen, player2, WIDTH - 80, 60, align_left=False)

    pygame.display.flip()
    clock.tick(60)

pygame.quit()
