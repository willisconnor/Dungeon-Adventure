import pygame

from src.model.DungeonHero import Hero

class Knight(Hero):
    """Knight hero subclass - specializes in defense and melee combat"""

    def __init__(self, x, y):
        super().__init__(x, y, hero_type="knight")
        self._facing_right = True
        self._mirrored_sprites = {}


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

    def get_current_sprite(self):
        """Get sprite, flipped if facing left"""
        base_sprite = super().get_current_sprite()  # Get normal sprite

        if base_sprite and not self._facing_right:
            sprite_id = id(base_sprite)
            if sprite_id not in self._mirrored_sprites:
                # Create and cache flipped sprite
                self._mirrored_sprites[sprite_id] = pygame.transform.flip(base_sprite, True, False)
            return self._mirrored_sprites[sprite_id]

        return base_sprite