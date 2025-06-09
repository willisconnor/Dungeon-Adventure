from src.model.Monster import Monster
import random


class Ogre(Monster):
    """Ogre monster - a powerful boss enemy"""

    def __init__(self):
        super().__init__("Grar the Ogre", 200, 0, is_boss=True)
        self.__attack_speed = 2
        self.__movement_speed = 10.0
        self.__special_skill = "Stun"

        # Set combat stats using parent class setters
        self.set_chance_to_hit(0.6)
        self.set_damage_range(30, 60)

        # Set healing stats using parent class setters
        self.set_heal_chance(0.1)
        self.set_heal_range(30, 60)

    def attack(self, player):
        """Attempt to attack the player"""
        print(f"{self.get_name()} uses {self.__special_skill}!")
        if random.random() <= self.get_chance_to_hit():
            min_damage, max_damage = self.get_damage_range()
            damage = random.randint(min_damage, max_damage)
            player.take_damage(damage)
            return damage
        else:
            print(f"{self.get_name()} missed!")
            return 0

    def __str__(self):
        """String representation of the ogre"""
        base_str = f"{self.get_name()} (HP: {self.get_health()})"
        ogre_specific = (
                f" | Special Skill: {self.__special_skill}" +
                f" | Attack Speed: {self.__attack_speed}" +
                f" | Movement Speed: {self.__movement_speed}"
        )
        return base_str + ogre_specific

    # Getter and setter methods
    def get_attack_speed(self):
        """Get the ogre's attack speed"""
        return self.__attack_speed

    def set_attack_speed(self, speed):
        """Set the ogre's attack speed"""
        self.__attack_speed = speed

    def get_movement_speed(self):
        """Get the ogre's movement speed"""
        return self.__movement_speed

    def set_movement_speed(self, speed):
        """Set the ogre's movement speed"""
        self.__movement_speed = speed

    def get_special_skill(self):
        """Get the ogre's special skill name"""
        return self.__special_skill

    def set_special_skill(self, skill):
        """Set the ogre's special skill name"""
        self.__special_skill = skill

    # Legacy method support for backward compatibility
    def setSpecialSkill(self, skill):
        """Legacy method for setting special skill"""
        self.set_special_skill(skill)

    def setMovementSpeed(self, speed):
        """Legacy method for setting movement speed"""
        self.set_movement_speed(speed)

    # Properties for easier access while maintaining encapsulation
    @property
    def attack_speed(self):
        return self.__attack_speed

    @attack_speed.setter
    def attack_speed(self, value):
        self.__attack_speed = value

    @property
    def movement_speed(self):
        return self.__movement_speed

    @movement_speed.setter
    def movement_speed(self, value):
        self.__movement_speed = value

    @property
    def specialSkill(self):
        return self.__special_skill

    @specialSkill.setter
    def specialSkill(self, value):
        self.__special_skill = value