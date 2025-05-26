from src.Model.Monster import Monster


class Ogre(Monster):
    def __init__(self):
        super().__init__("Ogre", 500, 70, is_boss=False)
        self.attack_speed = 0.35
        self.movement_speed = 10.0
        self.specialSkill = "Stun"

    def attack(self, player):
        print("Ogre uses stun attack!")
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
