from src.model.Monster import Monster
import random

class Goblin(Monster):
    def __init__(self):
        super().__init__("Goblin", 80, 0, is_boss=False)
        self.attack_speed = 4
        self.movement_speed = 40.0
        self.specialSkill = "Speed X2"

        # Combat stats
        self.chance_to_hit = 0.7
        self.min_damage = 10
        self.max_damage = 25

        # Healing stats
        self.chance_to_heal = 0.2
        self.min_heal = 10
        self.max_heal = 25

    def attack(self, player):
        print(f"{self.name} strikes with blinding speed!")
        if random.random() <= self.chance_to_hit:
            damage = random.randint(self.min_damage, self.max_damage)
            player.take_damage(damage)
            return damage
        else:
            print(f"{self.name}'s quick attack misses!")
            return 0

    def setSpecialSkill(self, skill):
        self.specialSkill = skill

    def setHitPoints(self, hp):
        self.health = hp

    def getHitPoints(self):
        return self.health

    def setMovementSpeed(self, speed):
        self.movement_speed = speed
