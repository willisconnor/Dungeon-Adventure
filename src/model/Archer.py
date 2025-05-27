from src.model.Hero import Hero


class Archer(Hero):
    def __init__(self, name="Archer"):
        super().__init__(name)
        self.hit_points = 150
        self.attack_speed = 2.0
        self.attack_damage = 40
        self.movement_speed = 50.0
        self.specialSkill = "Double Jump"

    def attack(self):
        print(f"{self.character_name} uses a ranged attack.")

    def setMovementSpeed(self, speed):
        self.movement_speed = speed

    def setSpecialSkill(self, skill):
        self.specialSkill = skill

    def setHitPoints(self, hp):
        self.hit_points = hp

    def getHitPoints(self):
        return self.hit_points