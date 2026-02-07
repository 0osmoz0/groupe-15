"""
Stats d’un joueur : pourcentage de dégâts (utilisé pour le knockback) et poids.
Chaque Player a une instance Stats.
"""
class Stats:
    def __init__(self, weight=1.0):
        self.percent = 0
        self.weight = weight
        self.stocks = 3

    def take_damage(self, dmg):
        self.percent += dmg