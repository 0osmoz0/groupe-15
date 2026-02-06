"""Dessin du HUD : pourcentages, stocks, portraits, ping."""
import pygame


def draw_player_ping(surface, player, ping_surface, offset_above: int = 15):
    """Dessine l'indicateur P1/P2 au-dessus du joueur."""
    if ping_surface is None or getattr(player, "lives", 1) <= 0:
        return
    r = ping_surface.get_rect(centerx=player.rect.centerx, bottom=player.rect.top - offset_above)
    surface.blit(ping_surface, r.topleft)


def _render_percent_text(font, percent: int, lives: int, player_color):
    """Rendu du pourcentage en texte lisible (contour noir + blanc)."""
    text = f"{int(percent)}%"
    fg = (255, 255, 255) if lives > 0 else (180, 180, 180)
    img = font.render(text, True, fg)
    outline = font.render(text, True, (0, 0, 0))
    w, h = img.get_size()
    out_surf = pygame.Surface((w + 4, h + 4))
    out_surf.set_colorkey((1, 0, 0))  # magenta comme colorkey pour transparence
    out_surf.fill((1, 0, 0))
    for dx in (-2, -1, 0, 1, 2):
        for dy in (-2, -1, 0, 1, 2):
            if dx == 0 and dy == 0:
                continue
            out_surf.blit(outline, (2 + dx, 2 + dy))
    out_surf.blit(img, (2, 2))
    out_surf.set_colorkey((1, 0, 0))
    return out_surf.convert()


def draw_percent_hud(surface, player, x: int, y: int, assets, align_left: bool = True):
    """Dessine le pourcentage et les stocks (icônes vies ou nombre)."""
    font = assets.font_percent
    life_icon = assets.life_icon_judy if getattr(player, "character", None) == "judy" else assets.life_icon_nick
    if getattr(player, "character", None) != "judy" and getattr(player, "character", None) != "nick":
        life_icon = assets.life_icon_judy or assets.life_icon_nick
    percent = int(getattr(getattr(player, "stats", None), "percent", 0))
    lives = max(0, getattr(player, "lives", 1))
    img_percent = _render_percent_text(font, percent, lives, getattr(player, "color", (255, 255, 255)))
    icon_w = assets.life_icon_size
    gap = 6
    if align_left:
        if life_icon and lives > 0:
            for i in range(lives):
                surface.blit(life_icon, (x + i * (icon_w + gap), y - icon_w // 2))
            stocks_right = x + lives * (icon_w + gap) - gap
            r_percent = img_percent.get_rect(midleft=(stocks_right + 24, y))
        else:
            text_stocks = font.render(f"{lives}", True, (255, 255, 255))
            r_stocks = text_stocks.get_rect(midleft=(x, y))
            surface.blit(text_stocks, r_stocks)
            r_percent = img_percent.get_rect(midleft=(r_stocks.right + 20, y))
        surface.blit(img_percent, r_percent)
    else:
        r_percent = img_percent.get_rect(midright=(x, y))
        surface.blit(img_percent, r_percent)
        if life_icon and lives > 0:
            start_x = r_percent.left - 24 - lives * (icon_w + gap) + gap
            for i in range(lives):
                surface.blit(life_icon, (start_x + i * (icon_w + gap), y - icon_w // 2))
        else:
            text_stocks = font.render(f"{lives}", True, (255, 255, 255))
            r_stocks = text_stocks.get_rect(midright=(r_percent.left - 20, y))
            surface.blit(text_stocks, r_stocks)


def draw_portraits(surface, assets, screen_w: int, hud_y: int, player1=None, player2=None):
    """Dessine les portraits P1 à gauche, P2 à droite (selon qui est Nick/Judy)."""
    portrait_bottom = hud_y - 25
    margin = assets.portrait_side_margin
    char1 = getattr(player1, "character", None) if player1 else "judy"
    char2 = getattr(player2, "character", None) if player2 else "nick"
    left_portrait = assets.nick_portrait if char1 == "nick" else assets.judy_portrait
    right_portrait = assets.judy_portrait if char2 == "judy" else assets.nick_portrait
    if left_portrait:
        r = left_portrait.get_rect(bottomleft=(margin, portrait_bottom))
        surface.blit(left_portrait, r.topleft)
    if right_portrait:
        r = right_portrait.get_rect(bottomright=(screen_w - margin, portrait_bottom))
        surface.blit(right_portrait, r.topleft)
