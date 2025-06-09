import random

class Monster:
    def __init__(self, name: str, health: int, attack_damage: int, is_boss: bool):
        self.__name = name
        self.__health = health
        self.__attack_damage = attack_damage
        self.__is_boss = is_boss

        # Optional attributes you can set in subclasses
        self.__chance_to_hit = 1.0
        self.__min_damage = attack_damage
        self.__max_damage = attack_damage
        self.__chance_to_heal = 0.0
        self.__min_heal = 0
        self.__max_heal = 0

    def attack(self, player):
        """Attempt to attack the player"""
        if random.random() <= self.__chance_to_hit:
            damage = random.randint(self.__min_damage, self.__max_damage)
            player.take_damage(damage)
            return damage
        return 0

    def is_alive(self):
        """Check if the monster is still alive"""
        return self.__health > 0

    def take_damage(self, damage):
        """Reduce health by damage amount and try to heal if still alive"""
        self.__health -= damage
        if self.__health > 0:
            self.__try_heal()

    def __try_heal(self):
        """Private method to attempt healing based on chance"""
        if random.random() <= self.__chance_to_heal:
            heal_amount = random.randint(self.__min_heal, self.__max_heal)
            self.__health += heal_amount
            print(f"{self.__name} heals for {heal_amount} HP!")

    # Getters
    def get_name(self):
        """Get monster name"""
        return self.__name

    def get_health(self):
        """Get current health"""
        return self.__health

    def get_attack_damage(self):
        """Get base attack damage"""
        return self.__attack_damage

    def is_boss_monster(self):
        """Check if this is a boss monster"""
        return self.__is_boss

    def get_chance_to_hit(self):
        """Get monster's chance to hit"""
        return self.__chance_to_hit

    def get_damage_range(self):
        """Get damage range as tuple (min, max)"""
        return (self.__min_damage, self.__max_damage)

    def get_heal_chance(self):
        """Get chance to heal"""
        return self.__chance_to_heal

    def get_heal_range(self):
        """Get healing range as tuple (min, max)"""
        return (self.__min_heal, self.__max_heal)

    # Setters
    def set_health(self, hp):
        """Set monster's current health"""
        self.__health = hp

    def set_chance_to_hit(self, chance):
        """Set monster's chance to hit (0.0-1.0)"""
        self.__chance_to_hit = max(0.0, min(1.0, chance))  # Clamp between 0 and 1

    def set_damage_range(self, min_damage, max_damage):
        """Set monster's damage range"""
        self.__min_damage = min_damage
        self.__max_damage = max(min_damage, max_damage)  # Ensure max >= min

    def set_heal_chance(self, chance):
        """Set monster's chance to heal (0.0-1.0)"""
        self.__chance_to_heal = max(0.0, min(1.0, chance))  # Clamp between 0 and 1

    def set_heal_range(self, min_heal, max_heal):
        """Set monster's healing range"""
        self.__min_heal = min_heal
        self.__max_heal = max(min_heal, max_heal)  # Ensure max >= min