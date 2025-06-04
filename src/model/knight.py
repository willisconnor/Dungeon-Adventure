from src.model.DungeonHero import Hero


class Knight(Hero):
    """Knight hero subclass - specializes in defense and melee combat"""

    def __init__(self, x, y):
        super().__init__(x, y, hero_type="knight")
        self.__shield_bash_stun_duration = 2.0  # Seconds to stun enemies
        self.__defense_bonus = 0.25  # 25% damage reduction when defending

    def calculate_damage(self, target):
        """Knights deal extra damage when at low health"""
        health_percent = self.get_health() / self.get_max_health()

        if health_percent < 0.3:
            return int(self.get_damage() * 1.5)  # 50% bonus damage when below 30% health
        return self.get_damage()

    def activate_special_ability(self):
        """Knight special: shield bash that stuns enemies"""
        super().activate_special_ability()
        # Shield bash logic would be implemented in game system
        # For now, we just trigger the animation

    def take_damage(self, amount):
        """Knights take reduced damage when defending"""
        if self.is_defending():
            # Apply defense bonus when defending
            amount = int(amount * (1 - self.__defense_bonus))
        return super().take_damage(amount)

    def __str__(self):
        """String representation of the Knight"""
        base_str = super().__str__()
        knight_specific = (
                f" | Shield Bash Stun: {self.__shield_bash_stun_duration}s" +
                f" | Defense Bonus: {self.__defense_bonus * 100:.0f}%"
        )
        return base_str + knight_specific

    # Getters and setters ~Jayda
    def get_shield_bash_stun_duration(self):
        """Get knight's shield bash stun duration"""
        return self.__shield_bash_stun_duration

    def set_shield_bash_stun_duration(self, duration):
        """Set knight's shield bash stun duration"""
        self.__shield_bash_stun_duration = duration

    def get_defense_bonus(self):
        """Get knight's defense bonus"""
        return self.__defense_bonus

    def set_defense_bonus(self, bonus):
        """Set knight's defense bonus"""
        self.__defense_bonus = max(0.0, min(0.9, bonus))  # Clamp between 0% and 90%
