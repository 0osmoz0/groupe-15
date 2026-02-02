import pygame
import sys

# Initialisation
pygame.init()

# Taille de la fenêtre
WIDTH, HEIGHT = 800, 600
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Menu avec Settings")

# Horloge pour FPS
clock = pygame.time.Clock()

# Couleurs
BG_COLOR = (0, 206, 200)
BUTTON_COLOR = (255, 255, 255)
BUTTON_HOVER = (200, 200, 200)
TEXT_COLOR = (0, 0, 0)

# Police
font = pygame.font.SysFont(None, 50)

# Fonctions utilitaires
def draw_button(text, rect):
    """Dessine un bouton et retourne True si cliqué"""
    mouse_pos = pygame.mouse.get_pos()
    mouse_click = pygame.mouse.get_pressed()
    
    color = BUTTON_HOVER if rect.collidepoint(mouse_pos) else BUTTON_COLOR
    pygame.draw.rect(screen, color, rect)
    
    label = font.render(text, True, TEXT_COLOR)
    label_rect = label.get_rect(center=rect.center)
    screen.blit(label, label_rect)
    
    # Retourne True si bouton cliqué
    if rect.collidepoint(mouse_pos) and mouse_click[0]:
        return True
    return False

# Menu
def main_menu():
    buttons = {
        "Play": pygame.Rect(300, 200, 200, 60),
        "Settings": pygame.Rect(300, 300, 200, 60),
        "Quit": pygame.Rect(300, 400, 200, 60)
    }
    
    while True:
        screen.fill(BG_COLOR)
        
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
        
        # Dessiner les boutons et gérer clic
        if draw_button("Play", buttons["Play"]):
            print("Play clicked!")
        if draw_button("Settings", buttons["Settings"]):
            settings_menu()
        if draw_button("Quit", buttons["Quit"]):
            pygame.quit()
            sys.exit()
        
        pygame.display.flip()
        clock.tick(60)

# Page Settings
def settings_menu():
    buttons = {
        "Option 1": pygame.Rect(300, 200, 200, 60),
        "Option 2": pygame.Rect(300, 300, 200, 60),
        "Back": pygame.Rect(300, 400, 200, 60)
    }
    
    # Exemples de paramètres
    option1_enabled = False
    option2_enabled = True
    
    while True:
        screen.fill((180, 180, 255))  # couleur différente pour settings
        
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
        
        # Bouton Option 1
        if draw_button(f"Option 1: {'On' if option1_enabled else 'Off'}", buttons["Option 1"]):
            option1_enabled = not option1_enabled
            pygame.time.delay(200)  # petite pause pour éviter clic multiple rapide
            
        # Bouton Option 2
        if draw_button(f"Option 2: {'On' if option2_enabled else 'Off'}", buttons["Option 2"]):
            option2_enabled = not option2_enabled
            pygame.time.delay(200)
        
        # Bouton Back
        if draw_button("Back", buttons["Back"]):
            return  # retourne au menu principal
        
        pygame.display.flip()
        clock.tick(60)

# Lancer le jeu
if __name__ == "__main__":
    main_menu()