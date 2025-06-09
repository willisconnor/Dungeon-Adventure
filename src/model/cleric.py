from src.model.DungeonEntity import Direction, AnimationState
from src.model.DungeonHero import Hero


class Cleric(Hero):
    """Updated Cleric hero class with projectile handling"""

    def __init__(self, x, y):
        super().__init__(x, y, hero_type="cleric")
        self.__healing_power = 20
        self.__fireball_damage = self.get_damage() * 2  # Fireballs deal double damage
        self.__fireball_speed = 8
        self.__fireball_range = 400
        self.__projectile_manager = None  # Will be set by the game

    def calculate_damage(self, target):
        """Clerics deal more damage to undead enemies"""
        if hasattr(target, 'enemy_type') and target.enemy_type == 'undead':
            return int(self.get_damage() * 2)  # Double damage vs undead
        return self.get_damage()

    def activate_special_ability(self):
        """Cleric special: heal self and cast fireball"""
        super().activate_special_ability()

        # Restore health
        healing = min(self.__healing_power, self.get_max_health() - self.get_health())
        self.set_health(self.get_health() + healing)

        # Cast fireball if we have a projectile manager
        if self.__projectile_manager is not None:
            from src.model.ProjectileManager import Projectile, ProjectileType

            # Calculate fireball starting position
            if self.get_direction() == Direction.RIGHT:
                start_x = self.get_x() + 50
            else:
                start_x = self.get_x() - 20

            start_y = self.get_y() + 10  # Adjust to match animation

            # Create and cast fireball
            fireball = Projectile(
                x=start_x,
                y=start_y,
                direction=self.get_direction(),
                projectile_type=ProjectileType.FIREBALL,
                owner=self,
                damage=self.__fireball_damage,
                speed=self.__fireball_speed,
                range=self.__fireball_range
            )

            # Add to projectile manager
            self.__projectile_manager.add_projectile(fireball)

    def get_attack_hitbox(self):
        """Get hitbox for current attack"""
        if not self.is_attacking() and not self.is_using_special():
            return None

        # Create attack hitbox based on character direction
        width = self.get_attack_range()
        height = 80

        if self.get_direction() == Direction.RIGHT:
            x = self.get_x() + 25
            y = self.get_y() - height // 2
        else:
            x = self.get_x() - 25 - width
            y = self.get_y() - height // 2

        return pygame.Rect(x, y, width, height)

    def attack(self, targets):
        """Attempt to attack a list of target entities"""
        if (not self.is_attacking() and not self.is_using_special()) or not self.is_alive():
            return []

        hit_targets = []
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

    def heal_ally(self, ally):
        """Heal an ally hero"""
        if not self.is_alive() or ally is None or not ally.is_alive():
            return 0

        # Calculate healing amount (can be modified by abilities or potions)
        healing = self.__healing_power

        # Apply healing
        actual_healing = min(healing, ally.get_max_health() - ally.get_health())
        ally.set_health(ally.get_health() + actual_healing)

        return actual_healing

    def __str__(self):
        """String representation of the Cleric"""
        base_str = super().__str__()
        cleric_specific = (
                f" | Healing Power: {self.__healing_power}" +
                f" | Fireball Damage: {self.__fireball_damage}" +
                f" | Fireball Range: {self.__fireball_range}"
        )
        return base_str + cleric_specific

    # Getters and setters!!
    def get_healing_power(self):
        """Get cleric's healing power"""
        return self.__healing_power

    def set_healing_power(self, power):
        """Set cleric's healing power"""
        self.__healing_power = power

    def get_fireball_damage(self):
        """Get cleric's fireball damage"""
        return self.__fireball_damage

    def set_fireball_damage(self, damage):
        """Set cleric's fireball damage"""
        self.__fireball_damage = damage

    def get_fireball_speed(self):
        """Get cleric's fireball speed"""
        return self.__fireball_speed

    def set_fireball_speed(self, speed):
        """Set cleric's fireball speed"""
        self.__fireball_speed = speed

    def get_fireball_range(self):
        """Get cleric's fireball range"""
        return self.__fireball_range

    def set_fireball_range(self, range_val):
        """Set cleric's fireball range"""
        self.__fireball_range = range_val

    def get_projectile_manager(self):
        """Get cleric's projectile manager"""
        return self.__projectile_manager

    def set_projectile_manager(self, manager):
        """Set cleric's projectile manager"""
        self.__projectile_manager = manager

    # Property to maintain backward compatibility
    @property
    def projectile_manager(self):
        return self.__projectile_manager

    @projectile_manager.setter
    def projectile_manager(self, manager):
        self.__projectile_manager = manager

    @property
    def healing_power(self):
        return self.__healing_power