from src.model.Hero import Hero


class Warrior(Hero):
    def __init__(self, name="Warrior"):
        super().__init__(name)
        self.hit_points = 375
        self.attack_damage = 55
        self.attack_speed = 1.3
        self.movement_speed = 50.0
        self.specialSkill = "Dash"

    def attack(self):
        print(f"{self.character_name} charges in with a heavy strike!")

    def setMovementSpeed(self, speed):
        self.movement_speed = speed

    def setSpecialSkill(self, skill):
        self.specialSkill = skill

    def setHitPoints(self, hp):
        self.hit_points = hp

    def getHitPoints(self):
        return self.hit_points