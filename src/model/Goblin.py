from src.model.Monster import Monster
import random


class Goblin(Monster):
    def __init__(self):
        super().__init__("Goblin", 80, 0, is_boss=False)
        self.__attack_speed = 4
        self.__movement_speed = 40.0
        self.__special_skill = "Speed X2"

        # Set combat stats using parent class setters
        self.set_chance_to_hit(0.7)
        self.set_damage_range(10, 25)

        # Set healing stats using parent class setters
        self.set_heal_chance(0.2)
        self.set_heal_range(10, 25)

    def attack(self, player):
        """Goblin attack implementation"""
        print(f"{self.get_name()} strikes with blinding speed!")
        if random.random() <= self.get_chance_to_hit():
            min_damage, max_damage = self.get_damage_range()
            damage = random.randint(min_damage, max_damage)
            player.take_damage(damage)
            return damage
        else:
            print(f"{self.get_name()}'s quick attack misses!")
            return 0

    # Getter and setter methods
    def get_special_skill(self):
        """Get the goblin's special skill"""
        return self.__special_skill

    def set_special_skill(self, skill):
        """Set the goblin's special skill"""
        self.__special_skill = skill

    def get_movement_speed(self):
        """Get the goblin's movement speed"""
        return self.__movement_speed

    def set_movement_speed(self, speed):
        """Set the goblin's movement speed"""
        self.__movement_speed = speed

    def get_attack_speed(self):
        """Get the goblin's attack speed"""
        return self.__attack_speed

    def set_attack_speed(self, speed):
        """Set the goblin's attack speed"""
        self.__attack_speed = speed

    def __str__(self):
        """String representation of the goblin"""
        base_str = super().__str__()
        goblin_specific = (
                f" | Special: {self.__special_skill}" +
                f" | Attack Speed: {self.__attack_speed}" +
                f" | Movement Speed: {self.__movement_speed}"
        )
        return base_str + goblin_specific

    def setSpecialSkill(self, skill):
        """method for setting special skill"""
        self.set_special_skill(skill)

    def setHitPoints(self, hp):
        """Method for setting hit points"""
        self.set_health(hp)

    def getHitPoints(self):
        """Method for getting hit points"""
        return self.get_health()

    def setMovementSpeed(self, speed):
        """Method for setting movement speed"""
        self.set_movement_speed(speed)

