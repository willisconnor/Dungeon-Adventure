from src.model.Monster import Monster
import random


class Goblin(Monster):
    """
    Gorgon enemy - refactored from Goblin
    Simple enemy that attacks and moves
    """
    def __init__(self):
        # Initialize as Gorgon with stats from database
        super().__init__("Gorgon", 70, 0, is_boss=False)
        self.__attack_speed = 1.4  # From database
        self.__movement_speed = 40.0  # Keep original movement speed
        self.__special_skill = "Snake Strike"  # Updated for Gorgon theme

        # Set combat stats using parent class setters
        self.set_chance_to_hit(0.75)  # Slightly better accuracy
        self.set_damage_range(8, 12)  # Damage range based on database damage of 10

        # Set healing stats using parent class setters
        self.set_heal_chance(0.15)  # Reduced heal chance
        self.set_heal_range(5, 10)  # Smaller heals

    def attack(self, player):
        """Gorgon attack implementation"""
        print(f"{self.get_name()} strikes with venomous fangs!")
        if random.random() <= self.get_chance_to_hit():
            min_damage, max_damage = self.get_damage_range()
            damage = random.randint(min_damage, max_damage)
            player.take_damage(damage)
            return damage
        else:
            print(f"{self.get_name()}'s serpentine attack misses!")
            return 0

    def get_monster_type(self):
        """Return the monster type for database lookups"""
        return "gorgon"

    # Getter and setter methods
    def get_special_skill(self):
        """Get the gorgon's special skill"""
        return self.__special_skill

    def set_special_skill(self, skill):
        """Set the gorgon's special skill"""
        self.__special_skill = skill

    def get_movement_speed(self):
        """Get the gorgon's movement speed"""
        return self.__movement_speed

    def set_movement_speed(self, speed):
        """Set the gorgon's movement speed"""
        self.__movement_speed = speed

    def get_attack_speed(self):
        """Get the gorgon's attack speed"""
        return self.__attack_speed

    def set_attack_speed(self, speed):
        """Set the gorgon's attack speed"""
        self.__attack_speed = speed

    def __str__(self):
        """String representation of the gorgon"""
        base_str = super().__str__()
        gorgon_specific = (
                f" | Special: {self.__special_skill}" +
                f" | Attack Speed: {self.__attack_speed}" +
                f" | Movement Speed: {self.__movement_speed}"
        )
        return base_str + gorgon_specific

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




# Alias for compatibility if needed
Gorgon = Goblin