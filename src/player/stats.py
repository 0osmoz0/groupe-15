class Stats:
    def __init__(self):
        self.percent = 0.0
        self.weight = 1.0
        self.stocks = 3
    
    def take_damage(self, dmg):
        self.percent += dmg