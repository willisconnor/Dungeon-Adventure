from src.Module.Hero import Hero


class Mage(Hero):
    def __init__(self, name="Mage"):
        super().__init__(name)
        self.hit_points = 250
        self.attack_speed = 0.75
        self.attack_damage = 85
        self.movement_speed = 35.0
        self.specialSkill = "Healing"

    def attack(self):
        print(f"{self.character_name} casts a powerful spell.")

    def setMovementSpeed(self, speed):
        self.movement_speed = speed

    def setSpecialSkill(self, skill):
        self.specialSkill = skill

    def setHitPoints(self, hp):
        self.hit_points = hp

    def getHitPoints(self):
        return self.hit_points