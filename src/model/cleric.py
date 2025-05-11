from src.model.DungeonHero import Hero


class Cleric(Hero):
    """Cleric hero subclass - specializes in healing and support"""

    def __init__(self, x, y):
        super().__init__(x, y, hero_type="cleric")
        self.healing_power = 20

    def calculate_damage(self, target):
        """Clerics deal more damage to undead enemies"""
        if hasattr(target, 'enemy_type') and target.enemy_type == 'undead':
            return int(self.damage * 2)  # Double damage vs undead
        return self.damage

    def activate_special_ability(self):
        """Cleric special: heal self"""
        super().activate_special_ability()
        # Restore health
        healing = min(self.healing_power, self.max_health - self.health)
        self.health += healing