import pygame

class Hitbox:
    def __init__(self, owner, rect, attack):
        self.owner = owner
        self.rect = rect
        self.attack = attack

    def check_hit(self, target):
        return self.rect.colliderect(target.rect)