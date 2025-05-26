import pygame
from src.model.DungeonEntity import Direction, AnimationState
from src.model.DungeonHero import Hero


class Archer(Hero):
    """Updated Archer hero class with projectile handling"""

    def __init__(self, x, y):
        super().__init__(x, y, hero_type="archer")
        self.projectile_speed = 12
        self.projectile_range = 500
        self.arrow_damage = self.damage  # Base damage for arrows
        self.projectile_manager = None  # Will be set by the game
        self.arrow_fired = False  # Track if arrow was fired in current attack

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

    def attack(self, targets):
        """Override attack to fire arrows"""
        if not self.is_attacking or not self.is_alive:
            return []

        # Track if we hit any targets
        hit_targets = []

        # Calculate arrow starting position
        if self.direction == Direction.RIGHT:
            start_x = self.x + 40
        else:
            start_x = self.x - 10

        start_y = self.y + 20  # Adjust to match animation

        # Fire arrow at a specific frame of the attack animation
        # For example, frame 2 might be when the bow is fully drawn
        if self.frame_index == 2 and not self.arrow_fired and self.projectile_manager is not None:
            from ProjectileManager import Projectile, ProjectileType

            # Create new arrow projectile
            arrow = Projectile(
                x=start_x,
                y=start_y,
                direction=self.direction,
                projectile_type=ProjectileType.ARROW,
                owner=self,
                damage=self.arrow_damage,
                speed=self.projectile_speed,
                range=self.projectile_range
            )

            # Add to projectile manager
            self.projectile_manager.add_projectile(arrow)

            # Mark arrow as fired for this attack
            self.arrow_fired = True

        # Reset arrow_fired flag when attack is complete
        if self.attack_complete:
            self.arrow_fired = False

        # Handle melee attacks too (for close-up enemies)
        attack_hitbox = self.get_attack_hitbox()

        if attack_hitbox:
            for target in targets:
                # Skip targets already hit by this attack or that aren't alive
                if target in self.hit_targets or not target.is_alive:
                    continue

                # Check collision with target's hitbox
                if attack_hitbox.colliderect(target.hitbox):
                    # Calculate damage
                    damage = self.calculate_damage(target)
                    # Hit successful
                    hit = target.take_damage(damage)
                    if hit:
                        self.hit_targets.add(target)
                        hit_targets.append(target)

        return hit_targets

    def activate_special_ability(self):
        """Archer special: rain of arrows (area attack)"""
        super().activate_special_ability()

        if self.projectile_manager is None:
            return

        from ProjectileManager import Projectile, ProjectileType

        # Fire multiple arrows in a spread pattern
        num_arrows = 5
        spread_angle = 30  # Total spread in degrees
        angle_step = spread_angle / (num_arrows - 1)

        base_damage = self.damage * 0.8  # Each arrow does slightly less damage

        for i in range(num_arrows):
            # Calculate angle offset from center
            angle_offset = -spread_angle / 2 + i * angle_step

            # Calculate starting position
            if self.direction == Direction.RIGHT:
                start_x = self.x + 40
                angle = 0 + angle_offset  # 0 degrees = right
            else:
                start_x = self.x - 10
                angle = 180 + angle_offset  # 180 degrees = left

            start_y = self.y + 10

            # Create arrow with angle
            arrow = Projectile(
                x=start_x,
                y=start_y,
                direction=self.direction,
                projectile_type=ProjectileType.ARROW,
                owner=self,
                damage=int(base_damage),
                speed=self.projectile_speed,
                range=self.projectile_range
            )

            # Set trajectory angle
            arrow.angle = angle

            # Add to projectile manager
            self.projectile_manager.add_projectile(arrow)