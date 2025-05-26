from src.Model.Monster import Monster


class Goblin(Monster):
    def __init__(self):
        super().__init__("Goblin", 380, 30, is_boss=False)
        self.attack_speed = 1.0
        self.movement_speed = 40.0
        self.specialSkill = "Speed X2"

    def attack(self, player):
        print("Goblin strikes quickly!")
        return self.attackDamage

    def isAlive(self):
        return self.health > 0

    def setSpecialSkill(self, skill):
        self.specialSkill = skill

    def setHitPoints(self, hp):
        self.health = hp

    def getHitPoints(self):
        return self.health

    def setMovementSpeed(self, speed):
        self.movement_speed = speed
