import random
import pygame
from src.model.Monster import Monster
from enum import Enum, auto

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

class Skeleton(Monster):
    def __init__(self, x=0, y=0):
        super().__init__("Skeleton", 100, 25, is_boss=False)
        # Basic stats
        self.__max_health = 100
        self.__health = 100
        self.__is_alive = True
        self.__is_invulnerable = False
        self.__invulnerable_timer = 0
        self.__attack_cooldown = 0
        self.__attack_cooldown_max = 1.5  # 1.5 seconds between attacks
        self.__damage = 25
        self.__special_skill = "Bone Strike"
        self.__attack_range = 80  # Pixels
        self.__target = None
        self.__animation_state = AnimationState.IDLE
        self.__direction = Direction.RIGHT

        # Set movement speed using parent class method
        self.set_movement_speed(25.0)
        self.set_attack_range(self.__attack_range)
        self.set_attack_cooldown(self.__attack_cooldown_max)

        # Set combat stats using parent class setters
        self.set_chance_to_hit(0.8)
        self.set_damage_range(20, 30)

        # Set healing stats using parent class setters
        self.set_heal_chance(0.1)  # Reduced heal chance
        self.set_heal_range(10, 20)  # Lower heal amounts

        # In Skeleton.__init__:
        # Set up sprite image and rect
        self.image = pygame.Surface((48, 64))
        self.image.fill((255, 255, 255))  # White placeholder
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y

        # Set up hitbox for collision detection
        self.hitbox = pygame.Rect(x + 12, y + 16, 24, 48)  # Smaller than visual sprite

    @property
    def is_alive(self):
        """Check if skeleton is alive"""
        return self.__is_alive
    
    def get_enemy_type(self):
        """Get the enemy type"""
        return "skeleton"
    
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
        """Check if skeleton is currently invulnerable"""
        return self.__is_invulnerable
    
    def is_attacking(self):
        """Check if skeleton is attacking"""
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
            # Set invulnerability briefly
            self.__is_invulnerable = True
            self.__invulnerable_timer = 0.5  # Half-second invulnerability
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
                
            # Set attack cooldown
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
        """Move the skeleton towards a target position"""
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
        self.hitbox.x = self.rect.x + 12  # Adjust as needed
        self.hitbox.y = self.rect.y + 16  # Adjust as needed
    
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
    
    def __str__(self):
        """String representation of the skeleton"""
        status = "DEAD" if not self.__is_alive else f"HP: {self.__health}/{self.__max_health}"
        return f"Skeleton ({status}, DMG: {self.__damage})"

    def is_visible_on_screen(self, camera_x, camera_y, screen_width, screen_height):
        """Check if the skeleton is visible on screen with current camera position"""
        screen_x = self.rect.x - camera_x
        screen_y = self.rect.y - camera_y
        return (screen_x + self.rect.width > 0 and screen_x < screen_width and
                screen_y + self.rect.height > 0 and screen_y < screen_height)