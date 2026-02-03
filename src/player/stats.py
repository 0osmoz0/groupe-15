class Stats:
    def __init__(self, weight=1.0):
        self.percent = 0
        self.weight = weight
        self.stocks = 3
    
    def take_damage(self, dmg):
        self.percent += dmg