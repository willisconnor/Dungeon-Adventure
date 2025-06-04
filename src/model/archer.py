import pygame
from src.model.DungeonEntity import Direction, AnimationState
from src.model.DungeonHero import Hero


class Archer(Hero):
    """Updated Archer hero class with projectile handling"""

    def __init__(self, x, y):
        super().__init__(x, y, hero_type="archer")
        self.__projectile_speed = 12
        self.__projectile_range = 500
        self.__arrow_damage = self.get_damage()  # Base damage for arrows
        self.__projectile_manager = None  # Will be set by the game
        self.__arrow_fired = False  # Track if arrow was fired in current attack

    def get_attack_hitbox(self):
        """Override to provide different attack hitbox for archer"""
        if not self.is_attacking() and not self.is_using_special():
            return None

        # Archer has longer, narrower hitbox
        width = self.get_attack_range() * 2  # Longer range
        height = 40  # Narrower

        if self.get_direction() == Direction.RIGHT:
            x = self.get_x() + 25  # Offset from character center
            y = self.get_y() - height // 2 + 10  # Adjusted to match animation
        else:  # Direction.LEFT
            x = self.get_x() - 25 - width  # Offset from character center
            y = self.get_y() - height // 2 + 10  # Adjusted to match animation

        return pygame.Rect(x, y, width, height)

    def attack(self, targets):
        """Override attack to fire arrows"""
        if not self.is_attacking() or not self.is_alive():
            return []

        # Track if we hit any targets
        hit_targets = []

        # Calculate arrow starting position
        if self.get_direction() == Direction.RIGHT:
            start_x = self.get_x() + 40
        else:
            start_x = self.get_x() - 10

        start_y = self.get_y() + 20  # Adjust to match animation

        # Fire arrow at a specific frame of the attack animation
        # For example, frame 2 might be when the bow is fully drawn
        if self.get_frame_index() == 2 and not self.__arrow_fired and self.__projectile_manager is not None:
            from src.model.ProjectileManager import Projectile, ProjectileType

            # Create new arrow projectile
            arrow = Projectile(
                x=start_x,
                y=start_y,
                direction=self.get_direction(),
                projectile_type=ProjectileType.ARROW,
                owner=self,
                damage=self.__arrow_damage,
                speed=self.__projectile_speed,
                range=self.__projectile_range
            )

            # Add to projectile manager
            self.__projectile_manager.add_projectile(arrow)

            # Mark arrow as fired for this attack
            self.__arrow_fired = True

        # Reset arrow_fired flag when attack is complete
        if self.is_attack_complete():
            self.__arrow_fired = False

        # Handle melee attacks too (for close-up enemies)
        attack_hitbox = self.get_attack_hitbox()

        if attack_hitbox:
            for target in targets:
                # Skip targets already hit by this attack or that aren't alive
                if target in self.get_hit_targets() or not hasattr(target, 'is_alive') or not target.is_alive:
                    continue

                # Check collision with target's hitbox
                if hasattr(target, 'hitbox') and attack_hitbox.colliderect(target.hitbox):
                    # Calculate damage
                    damage = self.calculate_damage(target)
                    # Hit successful
                    hit = target.take_damage(damage)
                    if hit:
                        self.add_hit_target(target)
                        hit_targets.append(target)

        return hit_targets

    def activate_special_ability(self):
        """Archer special: rain of arrows (area attack)"""
        super().activate_special_ability()

        if self.__projectile_manager is None:
            return

        from src.model.ProjectileManager import Projectile, ProjectileType

        # Fire multiple arrows in a spread pattern
        num_arrows = 5
        spread_angle = 30  # Total spread in degrees
        angle_step = spread_angle / (num_arrows - 1)

        base_damage = self.get_damage() * 0.8  # Each arrow does slightly less damage

        for i in range(num_arrows):
            # Calculate angle offset from center
            angle_offset = -spread_angle / 2 + i * angle_step

            # Calculate starting position
            if self.get_direction() == Direction.RIGHT:
                start_x = self.get_x() + 40
                angle = 0 + angle_offset  # 0 degrees = right
            else:
                start_x = self.get_x() - 10
                angle = 180 + angle_offset  # 180 degrees = left

            start_y = self.get_y() + 10

            # Create arrow with angle
            arrow = Projectile(
                x=start_x,
                y=start_y,
                direction=self.get_direction(),
                projectile_type=ProjectileType.ARROW,
                owner=self,
                damage=int(base_damage),
                speed=self.__projectile_speed,
                range=self.__projectile_range
            )

            # Set trajectory angle
            arrow.angle = angle

            # Add to projectile manager
            self.__projectile_manager.add_projectile(arrow)

    def __str__(self):
        """String representation of the Archer"""
        base_str = super().__str__()
        archer_specific = (
                f" | Arrow Damage: {self.__arrow_damage}" +
                f" | Projectile Range: {self.__projectile_range}" +
                f" | Projectile Speed: {self.__projectile_speed}"
        )
        return base_str + archer_specific

    # Getters and setters for encapsulation
    def get_projectile_speed(self):
        """Get archer's projectile speed"""
        return self.__projectile_speed

    def set_projectile_speed(self, speed):
        """Set archer's projectile speed"""
        self.__projectile_speed = speed

    def get_projectile_range(self):
        """Get archer's projectile range"""
        return self.__projectile_range

    def set_projectile_range(self, range_val):
        """Set archer's projectile range"""
        self.__projectile_range = range_val

    def get_arrow_damage(self):
        """Get archer's arrow damage"""
        return self.__arrow_damage

    def set_arrow_damage(self, damage):
        """Set archer's arrow damage"""
        self.__arrow_damage = damage

    def is_arrow_fired(self):
        """Check if arrow has been fired in current attack"""
        return self.__arrow_fired

    def set_arrow_fired(self, fired):
        """Set whether arrow has been fired in current attack"""
        self.__arrow_fired = fired

    def get_projectile_manager(self):
        """Get archer's projectile manager"""
        return self.__projectile_manager

    def set_projectile_manager(self, manager):
        """Set archer's projectile manager"""
        self.__projectile_manager = manager

    # Property to maintain backward compatibility
    @property
    def projectile_manager(self):
        return self.__projectile_manager

    @projectile_manager.setter
    def projectile_manager(self, manager):
        self.__projectile_manager = manager
