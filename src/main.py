import os
import pygame
from player.player import Player
from smash_platform.game_platform import Platform
from combat.hitbox_sprite import HitboxSprite
from combat.projectile_sprite import ProjectileSprite

try:
    from PIL import Image, ImageSequence
    _HAS_PIL = True
except ImportError:
    _HAS_PIL = False


def load_gif_frames(path, scale_size=None):
    """Charge les frames d'un GIF animé. Retourne liste de (Surface, duration_ms)."""
    if not _HAS_PIL:
        try:
            surf = pygame.image.load(path).convert_alpha()
            if scale_size:
                surf = pygame.transform.smoothscale(surf, scale_size)
            return [(surf, 50)]
        except Exception:
            return []
    frames = []
    try:
        with Image.open(path) as gif:
            for frame in ImageSequence.Iterator(gif):
                f = frame.convert("RGBA")
                size = f.size
                data = f.tobytes()
                surf = pygame.image.frombytes(data, size, "RGBA")
                surf = surf.convert_alpha()
                if scale_size:
                    surf = pygame.transform.smoothscale(surf, scale_size)
                duration = 50
                if hasattr(frame, "info") and "duration" in frame.info:
                    duration = max(20, frame.info["duration"])
                frames.append((surf, duration))
    except Exception:
        try:
            surf = pygame.image.load(path).convert_alpha()
            if scale_size:
                surf = pygame.transform.smoothscale(surf, scale_size)
            return [(surf, 50)]
        except Exception:
            return []
    return frames if frames else []


pygame.init()
pygame.font.init()

WIDTH, HEIGHT = 1920, 1080
screen = pygame.display.set_mode((WIDTH, HEIGHT), pygame.FULLSCREEN)
clock = pygame.time.Clock()

_screen_w, _screen_h = screen.get_size()
WORLD_W, WORLD_H = _screen_w * 2, _screen_h * 2

_base_dir = os.path.dirname(os.path.abspath(__file__))
_bg_path = os.path.join(_base_dir, "assets", "background map", "BG.png")
_background_raw = pygame.image.load(_bg_path).convert()
BACKGROUND = pygame.transform.smoothscale(_background_raw, (WORLD_W, WORLD_H))
world_surface = pygame.Surface((WORLD_W, WORLD_H))

CAMERA_LERP = 0.08
camera_x = WORLD_W // 2 - _screen_w // 2
camera_y = WORLD_H // 2 - _screen_h // 2

try:
    FONT_PERCENT = pygame.font.SysFont("arial", 72, bold=True)
except Exception:
    FONT_PERCENT = pygame.font.Font(None, 120)

_nick_win_gif_path = os.path.join(_base_dir, "assets", "Nick", "win_nick", "1.gif")
_judy_win_gif_path = os.path.join(_base_dir, "assets", "JUDY_HOPPS", "judy_win", "1 (1).gif")
_title_screen_path = os.path.join(_base_dir, "assets", "BG_perso", "1.png")
_versus_gif_path = os.path.join(_base_dir, "assets", "BG_perso", "1 (4).gif")
_versus_gif_p1_confirm_path = os.path.join(_base_dir, "assets", "BG_perso", "1 (5).gif")
_enter_gif_path = os.path.join(_base_dir, "assets", "BG_perso", "1 (2).gif")
_enter_then_a_gif_path = os.path.join(_base_dir, "assets", "BG_perso", "1 (3).gif")
NICK_WIN_FRAMES = load_gif_frames(_nick_win_gif_path, scale_size=(_screen_w, _screen_h))
VERSUS_GIF_FRAMES = load_gif_frames(_versus_gif_path, scale_size=(_screen_w, _screen_h))
P1_CONFIRM_GIF_FRAMES = load_gif_frames(_versus_gif_p1_confirm_path, scale_size=(_screen_w, _screen_h))
ENTER_GIF_FRAMES = load_gif_frames(_enter_gif_path, scale_size=(_screen_w, _screen_h))
ENTER_THEN_A_GIF_FRAMES = load_gif_frames(_enter_then_a_gif_path, scale_size=(_screen_w, _screen_h))
JUDY_WIN_FRAMES = load_gif_frames(_judy_win_gif_path, scale_size=(_screen_w, _screen_h))
try:
    _title_img = pygame.image.load(_title_screen_path).convert()
    TITLE_SCREEN = pygame.transform.smoothscale(_title_img, (_screen_w, _screen_h))
except Exception:
    TITLE_SCREEN = None

_counter_dir = os.path.join(_base_dir, "assets", "counter")
COUNTER_HEIGHT = 180
COUNTER_SURFACES = []
for name in ("3.png", "2.png", "1.png", "go.png"):
    try:
        img = pygame.image.load(os.path.join(_counter_dir, name)).convert_alpha()
        w = int(img.get_width() * COUNTER_HEIGHT / img.get_height())
        COUNTER_SURFACES.append(pygame.transform.smoothscale(img, (w, COUNTER_HEIGHT)))
    except Exception:
        COUNTER_SURFACES.append(None)

_ping_dir = os.path.join(_base_dir, "assets", "Ping")
PING_HEIGHT = 60
try:
    _p1_img = pygame.image.load(os.path.join(_ping_dir, "P1.png")).convert_alpha()
    PING_P1 = pygame.transform.smoothscale(_p1_img, (int(_p1_img.get_width() * PING_HEIGHT / _p1_img.get_height()), PING_HEIGHT))
except Exception:
    PING_P1 = None
try:
    _p2_img = pygame.image.load(os.path.join(_ping_dir, "P2.png")).convert_alpha()
    PING_P2 = pygame.transform.smoothscale(_p2_img, (int(_p2_img.get_width() * PING_HEIGHT / _p2_img.get_height()), PING_HEIGHT))
except Exception:
    PING_P2 = None
PING_OFFSET_ABOVE = 15

nick_win_frame_index = 0
nick_win_frame_timer_ms = 0
judy_win_frame_index = 0
judy_win_frame_timer_ms = 0
game_state = "title_screen"
countdown_step = 0
countdown_timer_ms = 0
COUNTDOWN_DURATION_MS = 1000
versus_gif_frame_index = 0
versus_gif_timer_ms = 0
versus_gif_phase = "playing"
wait_after_gif_timer_ms = 0
WAIT_AFTER_GIF_MS = 2000
p1_confirm_frame_index = 0
p1_confirm_timer_ms = 0
p1_confirm_phase = "playing"
wait_after_p1_confirm_timer_ms = 0
WAIT_AFTER_P1_CONFIRM_MS = 2000
enter_gif_frame_index = 0
enter_gif_timer_ms = 0
enter_gif_phase = "playing"
wait_after_enter_gif_timer_ms = 0
enter_then_a_frame_index = 0
enter_then_a_timer_ms = 0
enter_then_a_phase = "playing"
wait_after_enter_then_a_timer_ms = 0
WAIT_AFTER_ENTER_GIF_MS = 2000
WAIT_AFTER_ENTER_THEN_A_MS = 2000

player1 = Player(
    start_pos=(WORLD_W // 2 - 200, WORLD_H // 2),
    color=(255, 0, 0),
    controls={
        "left": pygame.K_q,
        "right": pygame.K_d,
        "jump": pygame.K_SPACE,
        "down": pygame.K_s,
        "attacking": pygame.K_f,
        "special": pygame.K_e,
        "grab": pygame.K_g,
        "counter": pygame.K_h,
    },
    screen_size=(WORLD_W, WORLD_H)
)

player2 = Player(
    start_pos=(WORLD_W // 2 + 200, WORLD_H // 2),
    color=(0, 0, 255),
    controls={
        "left": pygame.K_LEFT,
        "right": pygame.K_RIGHT,
        "jump": pygame.K_UP,
        "down": pygame.K_DOWN,
        "attacking": pygame.K_m,
        "special": pygame.K_i,
        "grab": pygame.K_o,
        "counter": pygame.K_j,
    },
    screen_size=(WORLD_W, WORLD_H),
    character="nick",
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


def draw_player_ping(surface, player, ping_surface):
    """Dessine l'indicateur P1/P2 au-dessus du joueur (comme Smash Bros)."""
    if ping_surface is None or getattr(player, "lives", 1) <= 0:
        return
    r = ping_surface.get_rect(centerx=player.rect.centerx, bottom=player.rect.top - PING_OFFSET_ABOVE)
    surface.blit(ping_surface, r.topleft)


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

world_center_x = WORLD_W // 2
world_center_y = WORLD_H // 2

platforms.add(
    Platform(
        (MAIN_W, MAIN_H),
        (world_center_x - MAIN_W // 2, world_center_y + 200)
    ),
    Platform(
        (SMALL_W, SMALL_H),
        (world_center_x - 350 - SMALL_W // 2, world_center_y),
        one_way=True
    ),
    Platform(
        (SMALL_W, SMALL_H),
        (world_center_x + 350 - SMALL_W // 2, world_center_y),
        one_way=True
    ),
)

running = True
while running:
    if game_state == "title_screen":
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            if event.type == pygame.KEYDOWN and event.key == pygame.K_a:
                game_state = "versus_gif"
                versus_gif_frame_index = 0
                versus_gif_timer_ms = 0
                versus_gif_phase = "playing"
                wait_after_gif_timer_ms = 0
            if event.type == pygame.KEYDOWN and event.key == pygame.K_RETURN:
                game_state = "versus_gif_enter"
                enter_gif_frame_index = 0
                enter_gif_timer_ms = 0
                enter_gif_phase = "playing"
                wait_after_enter_gif_timer_ms = 0
        if not running:
            break
        if game_state == "title_screen":
            if TITLE_SCREEN:
                screen.blit(TITLE_SCREEN, (0, 0))
            pygame.display.flip()
            clock.tick(60)
            continue

    if game_state == "versus_gif_enter":
        dt_ms = clock.get_time()
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            if event.type == pygame.KEYDOWN and event.key == pygame.K_a:
                game_state = "versus_gif_enter_then_a"
                enter_then_a_frame_index = 0
                enter_then_a_timer_ms = 0
                enter_then_a_phase = "playing"
                wait_after_enter_then_a_timer_ms = 0
        if not running:
            break
        if enter_gif_phase == "playing" and ENTER_GIF_FRAMES:
            enter_gif_timer_ms += dt_ms
            surf, duration_ms = ENTER_GIF_FRAMES[enter_gif_frame_index]
            while enter_gif_timer_ms >= duration_ms:
                enter_gif_timer_ms -= duration_ms
                enter_gif_frame_index += 1
                if enter_gif_frame_index >= len(ENTER_GIF_FRAMES):
                    enter_gif_phase = "waiting"
                    enter_gif_frame_index = len(ENTER_GIF_FRAMES) - 1
                    break
                surf, duration_ms = ENTER_GIF_FRAMES[enter_gif_frame_index]
            if ENTER_GIF_FRAMES:
                surf, _ = ENTER_GIF_FRAMES[enter_gif_frame_index]
                screen.blit(surf, (0, 0))
        elif enter_gif_phase == "waiting":
            wait_after_enter_gif_timer_ms += dt_ms
            if ENTER_GIF_FRAMES:
                surf, _ = ENTER_GIF_FRAMES[-1]
                screen.blit(surf, (0, 0))
            if wait_after_enter_gif_timer_ms >= WAIT_AFTER_ENTER_GIF_MS:
                game_state = "versus_gif_enter_then_a"
                enter_then_a_frame_index = 0
                enter_then_a_timer_ms = 0
                enter_then_a_phase = "playing"
                wait_after_enter_then_a_timer_ms = 0
        else:
            game_state = "versus_gif_enter_then_a"
            enter_then_a_frame_index = 0
            enter_then_a_timer_ms = 0
            enter_then_a_phase = "playing"
            wait_after_enter_then_a_timer_ms = 0
        pygame.display.flip()
        clock.tick(60)
        continue

    if game_state == "versus_gif_enter_then_a":
        dt_ms = clock.get_time()
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
        if not running:
            break
        if enter_then_a_phase == "playing" and ENTER_THEN_A_GIF_FRAMES:
            enter_then_a_timer_ms += dt_ms
            surf, duration_ms = ENTER_THEN_A_GIF_FRAMES[enter_then_a_frame_index]
            while enter_then_a_timer_ms >= duration_ms:
                enter_then_a_timer_ms -= duration_ms
                enter_then_a_frame_index += 1
                if enter_then_a_frame_index >= len(ENTER_THEN_A_GIF_FRAMES):
                    enter_then_a_phase = "waiting"
                    enter_then_a_frame_index = len(ENTER_THEN_A_GIF_FRAMES) - 1
                    break
                surf, duration_ms = ENTER_THEN_A_GIF_FRAMES[enter_then_a_frame_index]
            if ENTER_THEN_A_GIF_FRAMES:
                surf, _ = ENTER_THEN_A_GIF_FRAMES[enter_then_a_frame_index]
                screen.blit(surf, (0, 0))
        elif enter_then_a_phase == "waiting":
            wait_after_enter_then_a_timer_ms += dt_ms
            if ENTER_THEN_A_GIF_FRAMES:
                surf, _ = ENTER_THEN_A_GIF_FRAMES[-1]
                screen.blit(surf, (0, 0))
            if wait_after_enter_then_a_timer_ms >= WAIT_AFTER_ENTER_THEN_A_MS:
                game_state = "countdown"
                countdown_step = 0
                countdown_timer_ms = 0
        else:
            game_state = "countdown"
            countdown_step = 0
            countdown_timer_ms = 0
        pygame.display.flip()
        clock.tick(60)
        continue

    if game_state == "versus_gif":
        dt_ms = clock.get_time()
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            if event.type == pygame.KEYDOWN and event.key == pygame.K_RETURN:
                game_state = "versus_gif_p1_confirm"
                p1_confirm_frame_index = 0
                p1_confirm_timer_ms = 0
                p1_confirm_phase = "playing"
                wait_after_p1_confirm_timer_ms = 0
        if not running:
            break
        if versus_gif_phase == "playing" and VERSUS_GIF_FRAMES:
            versus_gif_timer_ms += dt_ms
            surf, duration_ms = VERSUS_GIF_FRAMES[versus_gif_frame_index]
            while versus_gif_timer_ms >= duration_ms:
                versus_gif_timer_ms -= duration_ms
                versus_gif_frame_index += 1
                if versus_gif_frame_index >= len(VERSUS_GIF_FRAMES):
                    versus_gif_phase = "waiting"
                    versus_gif_frame_index = len(VERSUS_GIF_FRAMES) - 1
                    break
                surf, duration_ms = VERSUS_GIF_FRAMES[versus_gif_frame_index]
            if VERSUS_GIF_FRAMES:
                surf, _ = VERSUS_GIF_FRAMES[versus_gif_frame_index]
                screen.blit(surf, (0, 0))
        elif versus_gif_phase == "waiting":
            wait_after_gif_timer_ms += dt_ms
            if VERSUS_GIF_FRAMES:
                surf, _ = VERSUS_GIF_FRAMES[-1]
                screen.blit(surf, (0, 0))
            if wait_after_gif_timer_ms >= WAIT_AFTER_GIF_MS:
                game_state = "wait_p1_enter"
        else:
            game_state = "wait_p1_enter"
        pygame.display.flip()
        clock.tick(60)
        continue

    if game_state == "wait_p1_enter":
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            if event.type == pygame.KEYDOWN and event.key == pygame.K_RETURN:
                game_state = "versus_gif_p1_confirm"
                p1_confirm_frame_index = 0
                p1_confirm_timer_ms = 0
                p1_confirm_phase = "playing"
                wait_after_p1_confirm_timer_ms = 0
        if not running:
            break
        if VERSUS_GIF_FRAMES:
            surf, _ = VERSUS_GIF_FRAMES[-1]
            screen.blit(surf, (0, 0))
        pygame.display.flip()
        clock.tick(60)
        continue

    if game_state == "versus_gif_p1_confirm":
        dt_ms = clock.get_time()
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
        if not running:
            break
        if p1_confirm_phase == "playing" and P1_CONFIRM_GIF_FRAMES:
            p1_confirm_timer_ms += dt_ms
            surf, duration_ms = P1_CONFIRM_GIF_FRAMES[p1_confirm_frame_index]
            while p1_confirm_timer_ms >= duration_ms:
                p1_confirm_timer_ms -= duration_ms
                p1_confirm_frame_index += 1
                if p1_confirm_frame_index >= len(P1_CONFIRM_GIF_FRAMES):
                    p1_confirm_phase = "waiting"
                    p1_confirm_frame_index = len(P1_CONFIRM_GIF_FRAMES) - 1
                    break
                surf, duration_ms = P1_CONFIRM_GIF_FRAMES[p1_confirm_frame_index]
            if P1_CONFIRM_GIF_FRAMES:
                surf, _ = P1_CONFIRM_GIF_FRAMES[p1_confirm_frame_index]
                screen.blit(surf, (0, 0))
        elif p1_confirm_phase == "waiting":
            wait_after_p1_confirm_timer_ms += dt_ms
            if P1_CONFIRM_GIF_FRAMES:
                surf, _ = P1_CONFIRM_GIF_FRAMES[-1]
                screen.blit(surf, (0, 0))
            if wait_after_p1_confirm_timer_ms >= WAIT_AFTER_P1_CONFIRM_MS:
                game_state = "countdown"
                countdown_step = 0
                countdown_timer_ms = 0
        else:
            game_state = "countdown"
            countdown_step = 0
            countdown_timer_ms = 0
        pygame.display.flip()
        clock.tick(60)
        continue

    if game_state == "countdown":
        dt_ms = clock.get_time()
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
        if not running:
            break
        countdown_timer_ms += dt_ms
        if countdown_timer_ms >= COUNTDOWN_DURATION_MS:
            countdown_timer_ms = 0
            countdown_step += 1
            if countdown_step >= 4:
                game_state = "playing"
                pygame.display.flip()
                clock.tick(60)
                continue
        world_surface.blit(BACKGROUND, (0, 0))
        platforms.draw(world_surface)
        players.draw(world_surface)
        draw_player_ping(world_surface, player1, PING_P1)
        draw_player_ping(world_surface, player2, PING_P2)
        screen.blit(world_surface, (0, 0), (int(camera_x), int(camera_y), _screen_w, _screen_h))
        if countdown_step < 4 and COUNTER_SURFACES and COUNTER_SURFACES[countdown_step]:
            surf = COUNTER_SURFACES[countdown_step]
            x = (_screen_w - surf.get_width()) // 2
            y = (_screen_h - surf.get_height()) // 2
            screen.blit(surf, (x, y))
        pygame.display.flip()
        clock.tick(60)
        continue

    if game_state == "playing" and player1.lives <= 0 and player2.lives > 0 and getattr(player2, "character", None) == "nick":
        game_state = "nick_wins"
        nick_win_frame_index = 0
        nick_win_frame_timer_ms = 0
    if game_state == "playing" and player2.lives <= 0 and player1.lives > 0 and getattr(player1, "character", "judy") == "judy":
        game_state = "judy_wins"
        judy_win_frame_index = 0
        judy_win_frame_timer_ms = 0

    if game_state == "nick_wins":
        dt_ms = clock.get_time()
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    running = False
                else:
                    game_state = "playing"
                    player1.respawn()
                    player2.respawn()
                    player1.lives = 3
                    player2.lives = 3
        if not running:
            break
        if NICK_WIN_FRAMES:
            nick_win_frame_timer_ms += dt_ms
            surf, duration_ms = NICK_WIN_FRAMES[nick_win_frame_index]
            while nick_win_frame_timer_ms >= duration_ms and len(NICK_WIN_FRAMES) > 1:
                nick_win_frame_timer_ms -= duration_ms
                nick_win_frame_index = (nick_win_frame_index + 1) % len(NICK_WIN_FRAMES)
                surf, duration_ms = NICK_WIN_FRAMES[nick_win_frame_index]
            screen.blit(surf, (0, 0))
        pygame.display.flip()
        clock.tick(60)
        continue

    if game_state == "judy_wins":
        dt_ms = clock.get_time()
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    running = False
                else:
                    game_state = "playing"
                    player1.respawn()
                    player2.respawn()
                    player1.lives = 3
                    player2.lives = 3
        if not running:
            break
        if JUDY_WIN_FRAMES:
            judy_win_frame_timer_ms += dt_ms
            surf, duration_ms = JUDY_WIN_FRAMES[judy_win_frame_index]
            while judy_win_frame_timer_ms >= duration_ms and len(JUDY_WIN_FRAMES) > 1:
                judy_win_frame_timer_ms -= duration_ms
                judy_win_frame_index = (judy_win_frame_index + 1) % len(JUDY_WIN_FRAMES)
                surf, duration_ms = JUDY_WIN_FRAMES[judy_win_frame_index]
            screen.blit(surf, (0, 0))
        pygame.display.flip()
        clock.tick(60)
        continue

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

            if event.key == player1.controls.get("counter") and player1.lives > 0:
                player1.start_counter()
            if event.key == player2.controls.get("counter") and player2.lives > 0:
                player2.start_counter()

            if event.key == player1.controls.get("special") and player1.lives > 0:
                if keys[player1.controls["left"]] or keys[player1.controls["right"]]:
                    player1.start_attack("side_special", hitboxes)
                elif keys[player1.controls["jump"]]:
                    player1.start_attack("up_special", hitboxes)
                elif keys[player1.controls["down"]]:
                    player1.start_attack("down_special", hitboxes)
                else:
                    ProjectileSprite(player1, hitboxes)
                    player1.start_distance_attack_animation()
            if event.key == player2.controls.get("special") and player2.lives > 0:
                if keys[player2.controls["left"]] or keys[player2.controls["right"]]:
                    player2.start_attack("side_special", hitboxes)
                elif keys[player2.controls["jump"]]:
                    player2.start_attack("up_special", hitboxes)
                elif keys[player2.controls["down"]]:
                    player2.start_attack("down_special", hitboxes)
                else:
                    ProjectileSprite(player2, hitboxes)
                    player2.start_distance_attack_animation()

    player1.handle_input()
    player2.handle_input()

    player1.update([player2] + list(platforms))
    player2.update([player1] + list(platforms))

    hitboxes.update(list(players))

    living = [p for p in (player1, player2) if getattr(p, "lives", 1) > 0]
    if living:
        cx = sum(p.rect.centerx for p in living) / len(living)
        cy = sum(p.rect.centery for p in living) / len(living)
        target_x = cx - _screen_w / 2
        target_y = cy - _screen_h / 2
        target_x = max(0, min(WORLD_W - _screen_w, target_x))
        target_y = max(0, min(WORLD_H - _screen_h, target_y))
        camera_x += (target_x - camera_x) * CAMERA_LERP
        camera_y += (target_y - camera_y) * CAMERA_LERP
        camera_x = max(0, min(WORLD_W - _screen_w, camera_x))
        camera_y = max(0, min(WORLD_H - _screen_h, camera_y))

    world_surface.blit(BACKGROUND, (0, 0))
    hitboxes.draw(world_surface)
    for hb in hitboxes:
        hb.draw_hitboxes_debug(world_surface)
    platforms.draw(world_surface)
    players.draw(world_surface)
    draw_player_ping(world_surface, player1, PING_P1)
    draw_player_ping(world_surface, player2, PING_P2)

    screen.blit(world_surface, (0, 0), (int(camera_x), int(camera_y), _screen_w, _screen_h))

    draw_percent_hud(screen, player1, 80, 60, align_left=True)
    draw_percent_hud(screen, player2, _screen_w - 80, 60, align_left=False)

    pygame.display.flip()
    clock.tick(60)

pygame.quit()
