from src.Module.Monster import Monster


class Skeleton(Monster):
    def __init__(self):
        super().__init__("Skeleton", 250, 50, is_boss=False)
        self.attack_speed = 0.75
        self.movement_speed = 20.0
        self.specialSkill = "Charged Attack"

    def attack(self, player):
        print("Skeleton uses charged attack!")
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