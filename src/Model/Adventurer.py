class Adventurer:
    def __init__(self, name: str):
        self.name = name
        self.hit_points = 100
        self.ability_to_move = True
        self.total_healing_potions = 0
        self.total_vision_potions = 0
        self.pillars_found = 0

    def __str__(self):
        return f"Adventurer {self.name}"

    def takeDamage(self):
        pass

    def usePotions(self):
        pass

    def pickItem(self):
        pass

    def blockAttack(self):
        pass