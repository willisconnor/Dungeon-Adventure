from src.model.Monster import Monster
import random

class Ogre(Monster):
    def __init__(self):
        super().__init__("Grar the Ogre", 200, 0, is_boss=True)
        self.attack_speed = 2
        self.movement_speed = 10.0
        self.specialSkill = "Stun"

        # Set combat stats
        self.chance_to_hit = 0.6
        self.min_damage = 30
        self.max_damage = 60
        self.chance_to_heal = 0.1
        self.min_heal = 30
        self.max_heal = 60

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

    def setMovementSpeed(self, speed):
        self.movement_speed = speed
