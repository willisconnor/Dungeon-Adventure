import random
import pygame
from src.model.Monster import Monster

# Define animation states if not already defined elsewhere
class AnimationState:
    IDLE = "idle"
    WALKING = "walking"
    ATTACKING = "attacking"
    HURT = "hurt"
    DYING = "dying"
    DEAD = "dead"

class Direction:
    LEFT = "left"
    RIGHT = "right"

class Gorgon(Monster):
    """
    Gorgon enemy
    Fast but weaker enemy that attacks and moves quickly
    """

    def __init__(self, x=0, y=0):
        # Initialize with Gorgon stats
        super().__init__("Gorgon", 70, 10, is_boss=False)
        
        # Core attributes
        self.__max_health = 70
        self.__health = 70
        self.__is_alive = True
        self.__is_invulnerable = False
        self.__invulnerable_timer = 0
        self.__attack_cooldown = 0
        self.__attack_cooldown_max = 1.4  # Faster attack speed
        self.__damage = 10
        self.__special_skill = "Snake Strike"
        self.__attack_range = 70  # Shorter attack range than skeleton
        self.__target = None
        self.__animation_state = AnimationState.IDLE
        self.__direction = Direction.RIGHT

        # Set movement speed using parent class method - faster than skeleton
        self.set_movement_speed(40.0)
        self.set_attack_range(self.__attack_range)
        self.set_attack_cooldown(self.__attack_cooldown_max)

        # Set combat stats using parent class setters
        self.set_chance_to_hit(0.75)  # Good accuracy
        self.set_damage_range(8, 12)  # Lower but consistent damage

        # Set healing stats using parent class setters
        self.set_heal_chance(0.15)  # Some self-healing ability
        self.set_heal_range(5, 10)  # Small heals

        # Set up sprite image and rect with more visible colors
        self.image = pygame.Surface((32, 48))  # Smaller than skeleton
        self.image.fill((100, 255, 100))  # Bright green for better visibility
        pygame.draw.rect(self.image, (0, 0, 0), pygame.Rect(0, 0, 32, 48), 2)  # Add black border
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y

        # Set up hitbox for collision detection (slightly smaller than visual)
        self.hitbox = pygame.Rect(x + 8, y + 12, 16, 36)

    @property
    def is_alive(self):
        """Check if gorgon is alive"""
        return self.__is_alive
    
    def get_enemy_type(self):
        """Get the enemy type"""
        return "gorgon"  # For consistency with database references
    
    def get_animation_state(self):
        """Get current animation state"""
        return self.__animation_state
    
    def get_direction(self):
        """Get current facing direction"""
        return self.__direction
    
    def get_max_health(self):
        """Get maximum health"""
        return self.__max_health
    
    def get_health(self):
        """Get current health"""
        return self.__health
    
    def get_damage(self):
        """Get attack damage"""
        return self.__damage
    
    def get_attack_range(self):
        """Get attack range"""
        return self.__attack_range
    
    def get_x(self):
        """Get x position"""
        return self.rect.x
    
    def get_y(self):
        """Get y position"""
        return self.rect.y
    
    def is_invulnerable(self):
        """Check if gorgon is currently invulnerable"""
        return self.__is_invulnerable
    
    def is_attacking(self):
        """Check if gorgon is attacking"""
        return self.__animation_state == AnimationState.ATTACKING
    
    def take_damage(self, damage):
        """Take damage, return True if hit, False if not"""
        # Don't take damage if already dead or invulnerable
        if not self.__is_alive or self.__is_invulnerable:
            return False
            
        if damage <= 0:
            return False
            
        # Apply damage
        self.__health -= damage
        
        # Check if dead
        if self.__health <= 0:
            self.__health = 0
            self.__is_alive = False
            self.__animation_state = AnimationState.DYING
        else:
            # Set invulnerability briefly - shorter than skeleton
            self.__is_invulnerable = True
            self.__invulnerable_timer = 0.3  # Shorter invulnerability than skeleton
            self.__animation_state = AnimationState.HURT
            
        return True
    
    def attack(self, target):
        """Attack the target"""
        # Don't attack if on cooldown or dead
        if self.__attack_cooldown > 0 or not self.__is_alive:
            return False
            
        # Set attacking state
        self.__animation_state = AnimationState.ATTACKING
        
        # Calculate if hit connects
        if random.random() <= self.get_chance_to_hit():
            min_damage, max_damage = self.get_damage_range()
            damage = random.randint(min_damage, max_damage)
            
            # Apply damage to target if it has take_damage method
            if hasattr(target, 'take_damage'):
                target.take_damage(damage)
                
            # Set attack cooldown - shorter than skeleton
            self.__attack_cooldown = self.__attack_cooldown_max
            return True
        
        # Attack missed
        self.__attack_cooldown = self.__attack_cooldown_max / 2  # Shorter cooldown on miss
        return False
    
    def set_target(self, target):
        """Set the target for this enemy to follow/attack"""
        self.__target = target
    
    def get_target(self):
        """Get the current target"""
        return self.__target
    
    def move_towards_target(self, target_x, target_y, dt):
        """Move the gorgon towards a target position"""
        # Don't move if dead, attacking or hurt
        if not self.__is_alive or self.__animation_state in [AnimationState.ATTACKING, AnimationState.HURT, AnimationState.DYING]:
            return
        
        # Calculate distance to target
        dx = target_x - self.rect.centerx
        distance = abs(dx)
        
        # Set direction based on target position
        if dx > 0:
            self.__direction = Direction.RIGHT
        else:
            self.__direction = Direction.LEFT
            
        # Don't move if already in attack range
        if distance <= self.__attack_range:
            self.__animation_state = AnimationState.IDLE
            return
            
        # Set walking animation
        self.__animation_state = AnimationState.WALKING
        
        # Move towards target (horizontal only)
        move_distance = self.get_movement_speed() * dt
        move_x = min(move_distance, distance) * (1 if dx > 0 else -1)
        
        # Update position
        self.rect.x += move_x
        # Update hitbox position
        self._update_hitbox()
    
    def _update_hitbox(self):
        """Update the hitbox position to match the sprite"""
        self.hitbox.x = self.rect.x + 8  # Adjust as needed
        self.hitbox.y = self.rect.y + 12  # Adjust as needed
    
    def _update_attack_cooldown(self, dt):
        """Update attack cooldown timer"""
        if self.__attack_cooldown > 0:
            self.__attack_cooldown -= dt
    
    def _update_invulnerability(self, dt):
        """Update invulnerability timer"""
        if self.__is_invulnerable:
            self.__invulnerable_timer -= dt
            if self.__invulnerable_timer <= 0:
                self.__is_invulnerable = False
                # Return to idle if was hurt
                if self.__animation_state == AnimationState.HURT:
                    self.__animation_state = AnimationState.IDLE
    
    def update(self, dt=0):
        """Update method called by pygame sprite groups"""
        # Don't update if dead
        if not self.__is_alive and self.__animation_state == AnimationState.DEAD:
            return
            
        # Update timers
        self._update_attack_cooldown(dt)
        self._update_invulnerability(dt)
        
        # Handle death animation transition
        if self.__animation_state == AnimationState.DYING:
            # In a real implementation, you'd wait for death animation to finish
            # For now, just transition to DEAD state immediately
            self.__animation_state = AnimationState.DEAD
            return
        
        # If we have a target, move towards it and try to attack
        if self.__target and self.__is_alive:
            if hasattr(self.__target, 'rect'):
                target_x = self.__target.rect.centerx
                target_y = self.__target.rect.centery
            else:
                # Fallback if target doesn't have a rect
                target_x = getattr(self.__target, 'x', 0)
                target_y = getattr(self.__target, 'y', 0)
            
            # Check if in attack range
            distance = ((target_x - self.rect.centerx)**2 + (target_y - self.rect.centery)**2)**0.5
            
            if distance <= self.__attack_range and self.__attack_cooldown <= 0:
                # In range and cooldown ready - attack!
                self.attack(self.__target)
            else:
                # Not in range or on cooldown - move towards target
                self.move_towards_target(target_x, target_y, dt)
        
        # Call parent class update
        super().update(dt)
    
    # Original getter and setter methods for backward compatibility
    def get_special_skill(self):
        """Get the gorgon's special skill"""
        return self.__special_skill

    def set_special_skill(self, skill):
        """Set the gorgon's special skill"""
        self.__special_skill = skill

    def get_movement_speed(self):
        """Get the gorgon's movement speed"""
        return super().get_movement_speed()

    def set_movement_speed(self, speed):
        """Set the gorgon's movement speed"""
        super().set_movement_speed(speed)

    def get_attack_speed(self):
        """Get the gorgon's attack speed"""
        return self.__attack_cooldown_max

    def set_attack_speed(self, speed):
        """Set the gorgon's attack speed"""
        self.__attack_cooldown_max = speed
        self.set_attack_cooldown(speed)

    # Legacy methods for compatibility
    def setSpecialSkill(self, skill):
        """method for setting special skill (legacy)"""
        self.set_special_skill(skill)

    def setHitPoints(self, hp):
        """Method for setting hit points (legacy)"""
        self.__health = hp

    def getHitPoints(self):
        """Method for getting hit points (legacy)"""
        return self.__health

    def setMovementSpeed(self, speed):
        """Method for setting movement speed (legacy)"""
        self.set_movement_speed(speed)
    
    def __str__(self):
        """String representation of the gorgon"""
        status = "DEAD" if not self.__is_alive else f"HP: {self.__health}/{self.__max_health}"
        return f"Gorgon ({status}, DMG: {self.__damage}, Speed: {self.get_movement_speed()})"