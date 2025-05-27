from src.model.DungeonEntity import Direction, AnimationState
from src.model.DungeonHero import Hero


class Cleric(Hero):
    """Updated Cleric hero class with projectile handling"""

    def __init__(self, x, y):
        super().__init__(x, y, hero_type="cleric")
        self.healing_power = 20
        self.fireball_damage = self.damage * 2  # Fireballs deal double damage
        self.fireball_speed = 8
        self.fireball_range = 400
        self.projectile_manager = None  # Will be set by the game

    def calculate_damage(self, target):
        """Clerics deal more damage to undead enemies"""
        if hasattr(target, 'enemy_type') and target.enemy_type == 'undead':
            return int(self.damage * 2)  # Double damage vs undead
        return self.damage

    def activate_special_ability(self):
        """Cleric special: heal self and cast fireball"""
        super().activate_special_ability()

        # Restore health
        healing = min(self.healing_power, self.max_health - self.health)
        self.health += healing

        # Cast fireball if we have a projectile manager
        if self.projectile_manager is not None:
            from ProjectileManager import Projectile, ProjectileType

            # Calculate fireball starting position
            if self.direction == Direction.RIGHT:
                start_x = self.x + 50
            else:
                start_x = self.x - 20

            start_y = self.y + 10  # Adjust to match animation

            # Create and cast fireball
            fireball = Projectile(
                x=start_x,
                y=start_y,
                direction=self.direction,
                projectile_type=ProjectileType.FIREBALL,
                owner=self,
                damage=self.fireball_damage,
                speed=self.fireball_speed,
                range=self.fireball_range
            )

            # Add to projectile manager
            self.projectile_manager.add_projectile(fireball)

    def get_attack_hitbox(self):
        """Get hitbox for current attack"""
        if not self.is_attacking and not self.using_special:
            return None

        # Create attack hitbox based on character direction
        width = self.attack_range
        height = 80

        if self.direction == Direction.RIGHT:
            x = self.x + 25
            y = self.y - height // 2
        else:
            x = self.x - 25 - width
            y = self.y - height // 2

        return pygame.Rect(x, y, width, height)

    def attack(self, targets):
        """Attempt to attack a list of target entities"""
        if (not self.is_attacking and not self.using_special) or not self.is_alive:
            return []

        hit_targets = []
        attack_hitbox = self.get_attack_hitbox()

        if attack_hitbox:
            for target in targets:
                # Skip targets already hit by this attack or by those that aren't alive
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

    def heal_ally(self, ally):
        """Heal an ally hero"""
        if not self.is_alive or ally is None or not ally.is_alive:
            return 0

        # Calculate healing amount (can be modified by abilities or potions)
        healing = self.healing_power

        # Apply healing
        actual_healing = min(healing, ally.max_health - ally.health)
        ally.health += actual_healing

        return actual_healing