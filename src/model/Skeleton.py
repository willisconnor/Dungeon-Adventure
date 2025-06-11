from src.model.Monster import Monster
import random

class Skeleton(Monster):
    def __init__(self):
        super().__init__("Skeleton", 100, 0, is_boss=False)
        self.__attack_speed = 3
        self.__movement_speed = 20.0
        self.__special_skill = "Charged Attack"

        # Set combat stats using parent class setters
        self.set_chance_to_hit(0.8)
        self.set_damage_range(30, 50)

        # Set healing stats using parent class setters
        self.set_heal_chance(0.3)
        self.set_heal_range(30, 50)

    def attack(self, player):
        print(f"{self.get_name()} uses {self.__special_skill}!")
        if random.random() <= self.get_chance_to_hit():
            min_damage, max_damage = self.get_damage_range()
            damage = random.randint(min_damage, max_damage)
            player.take_damage(damage)
            return damage
        else:
            print(f"{self.get_name()} missed!")
            return 0

    def set_special_skill(self, skill):
        """Set the skeleton's special skill"""
        self.__special_skill = skill

    def get_special_skill(self):
        """Get the skeleton's special skill"""
        return self.__special_skill

    def get_movement_speed(self):
        """Get the skeleton's movement speed"""
        return self.__movement_speed

    def set_movement_speed(self, speed):
        """Set the skeleton's movement speed"""
        self.__movement_speed = speed

    def get_attack_speed(self):
        """Get the skeleton's attack speed"""
        return self.__attack_speed

    def set_attack_speed(self, speed):
        """Set the skeleton's attack speed"""
        self.__attack_speed = speed