from src.model.Monster import Monster
import random

class Skeleton(Monster):
    def __init__(self):
        super().__init__("Bones the Skeleton", 100, 0, is_boss=False)
        self.attack_speed = 3
        self.movement_speed = 20.0
        self.specialSkill = "Charged Attack"

        # Combat stats
        self.chance_to_hit = 0.8
        self.min_damage = 30
        self.max_damage = 50

        # Healing stats
        self.chance_to_heal = 0.3
        self.min_heal = 30
        self.max_heal = 50

    def attack(self, player):
        print(f"{self.name} uses {self.specialSkill}!")
        if random.random() <= self.chance_to_hit:
            damage = random.randint(self.min_damage, self.max_damage)
            player.take_damage(damage)
            return damage
        else:
            print(f"{self.name} missed!")
            return 0

    def setSpecialSkill(self, skill):
        self.specialSkill = skill

    def setHitPoints(self, hp):
        self.health = hp

    def getHitPoints(self):
        return self.health

    def setMovementSpeed(self, speed):
        self.movement_speed = speed
