import pygame

from src.model.DungeonEntity import Direction
from src.model.DungeonHero import Hero


class Archer(Hero):
    """Archer hero subclass - specializes in ranged attacks"""

    def __init__(self, x, y):
        super().__init__(x, y, hero_type="archer")
        self.projectile_speed = 12
        self.projectile_range = 500

    def get_attack_hitbox(self):
        """Override to provide different attack hitbox for archer"""
        if not self.is_attacking and not self.using_special:
            return None

        # Archer has longer, narrower hitbox
        width = self.attack_range * 2  # Longer range
        height = 40  # Narrower

        if self.direction == Direction.RIGHT:
            x = self.x + 25  # Offset from character center
            y = self.y - height // 2 + 10  # Adjusted to match animation
        else:  # Direction.LEFT
            x = self.x - 25 - width  # Offset from character center
            y = self.y - height // 2 + 10  # Adjusted to match animation

        return pygame.Rect(x, y, width, height)

    def activate_special_ability(self):
        """Archer special: rain of arrows (area attack)"""
        super().activate_special_ability()
        # Rain of arrows logic would be implemented in game system
        # Would apply damage to all enemies in a larger area