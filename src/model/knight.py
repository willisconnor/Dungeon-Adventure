from src.model.DungeonHero import Hero

class Knight(Hero):
    """Knight hero subclass - specializes in defense and melee combat"""

    def __init__(self, x, y):
        super().__init__(x, y, hero_type="knight")


    def calculate_damage(self, target):
        """Knights deal extra damage when at low health"""
        health_percent = self.health / self.max_health

        if health_percent < 0.3:
            return int(self.damage * 1.5)  # 50% bonus damage when below 30% health
        return self.damage

    def activate_special_ability(self):
        """Knight special: shield bash that stuns enemies"""
        super().activate_special_ability()
        # Shield bash logic would be implemented in game system
        # For now, we just trigger the animation