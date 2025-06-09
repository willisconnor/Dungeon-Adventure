"""
DungeonCharacter.py - Base character class for heroes and enemies
@author Connor Willis
"""
import pygame
from src.model.DungeonEntity import Direction, AnimationState

class DungeonCharacter:
    """Base class for all characters in the dungeon (heroes and enemies)"""
    
    def __init__(self, x, y, width, height, name, max_health, health, speed, damage):
        # Position and size
        self.x = x
        self.y = y
        self.width = width
        self.height = height
        self.rect = pygame.Rect(x, y, width, height)
        self.hitbox = pygame.Rect(x + width * 0.2, y + height * 0.2, width * 0.6, height * 0.8)
        
        # Basic attributes
        self.name = name
        self.max_health = max_health
        self.health = health
        self.speed = speed
        self.damage = damage
        self.is_alive = True
        
        # Movement attributes
        self.direction = Direction.RIGHT
        self.is_moving = False
        self.is_jumping = False
        self.is_falling = True
        self.y_velocity = 0
        self.gravity = 0.5
        self.jump_strength = -12
        
        # Combat attributes
        self.is_attacking = False
        self.attack_combo = 0
        self.hit_targets = set()
        self.is_defending = False
        self.using_special = False
        self.attack_timer = 0
        self.attack_duration = 0.5  # Half a second per attack
        self.critical_chance = 0.1  # 10% critical hit chance
        self.critical_damage = 1.5  # 50% bonus damage on critical hits
        
        # Status effects
        self.is_invulnerable = False
        self.invulnerable_timer = 0
        
        # Special ability
        self.special_cooldown = 5.0  # Default cooldown in seconds
        self.special_cooldown_remaining = 0
        
        # Animation
        self.animation_state = AnimationState.IDLE
        self.last_animation_state = AnimationState.IDLE
        self.current_frame = 0
        self.animation_timer = 0
        self.animation_speed = 0.1  # Seconds per frame
    
    def update(self, dt):
        """Update character state"""
        # Update position based on physics
        self._apply_gravity(dt)
        
        # Update hitbox position
        self._update_hitbox()
        
        # Update attack state
        if self.is_attacking:
            self.attack_timer += dt
            if self.attack_timer >= self.attack_duration:
                self.is_attacking = False
                self.attack_timer = 0
                self.hit_targets.clear()
        
        # Update invulnerability
        if self.is_invulnerable:
            self.invulnerable_timer -= dt
            if self.invulnerable_timer <= 0:
                self.is_invulnerable = False
        
        # Update special cooldown
        if self.special_cooldown_remaining > 0:
            self.special_cooldown_remaining -= dt
            if self.special_cooldown_remaining < 0:
                self.special_cooldown_remaining = 0
        
        # Update animation
        self.animation_timer += dt
        if self.animation_timer >= self.animation_speed:
            self.animation_timer = 0
            self.current_frame += 1
            # Reset frame if we've reached the end (assuming 4 frames per animation)
            if self.current_frame >= 4:
                self.current_frame = 0
                
                # If this was a one-time animation (like attacking), go back to idle
                if self.animation_state in [AnimationState.ATTACKING_1, AnimationState.ATTACKING_2, 
                                           AnimationState.ATTACKING_3, AnimationState.HURT,
                                           AnimationState.SPECIAL_SKILL] and not self.is_attacking:
                    self.animation_state = AnimationState.IDLE
    
    def _apply_gravity(self, dt):
        """Apply gravity to the character"""
        if self.is_falling or self.is_jumping:
            # Apply gravity to y velocity
            self.y_velocity += self.gravity * dt * 60
            
            # Apply y velocity to position
            self.y += self.y_velocity * dt * 60
            
            # Check if we're falling
            if self.y_velocity > 0:
                self.is_falling = True
                self.is_jumping = False
    
    def _update_hitbox(self):
        """Update hitbox position based on character position"""
        self.rect.x = self.x
        self.rect.y = self.y
        self.hitbox.x = self.x + self.width * 0.2
        self.hitbox.y = self.y + self.height * 0.2
    
    def take_damage(self, damage):
        """Handle taking damage"""
        if not self.is_alive or self.is_invulnerable:
            return False
        
        # Reduce damage if defending
        if self.is_defending:
            damage = max(1, int(damage * 0.5))  # At least 1 damage
        
        # Apply damage
        self.health -= damage
        
        # Check if dead
        if self.health <= 0:
            self.health = 0
            self.is_alive = False
            self.animation_state = AnimationState.DYING
            return True
        
        # Apply hit reaction
        self.is_invulnerable = True
        self.invulnerable_timer = 0.5  # Half second of invulnerability
        self.animation_state = AnimationState.HURT
        
        return True
    
    def heal(self, amount):
        """Heal the character"""
        if not self.is_alive:
            return False
        
        self.health = min(self.max_health, self.health + amount)
        return True
    
    def start_attack(self):
        """Start an attack"""
        if not self.is_alive or self.is_attacking or self.using_special:
            return False
        
        self.is_attacking = True
        self.attack_timer = 0
        self.hit_targets.clear()
        
        # Cycle through attack combos (1-2-3)
        self.attack_combo = (self.attack_combo % 3) + 1
        
        # Set animation state based on combo
        if self.attack_combo == 1:
            self.animation_state = AnimationState.ATTACKING_1
        elif self.attack_combo == 2:
            self.animation_state = AnimationState.ATTACKING_2
        else:  # attack_combo == 3
            self.animation_state = AnimationState.ATTACKING_3
        
        self.current_frame = 0
        return True
    
    def use_special_ability(self):
        """Use character's special ability"""
        if not self.is_alive or self.is_attacking or self.using_special or self.special_cooldown_remaining > 0:
            return False
        
        self.using_special = True
        self.special_cooldown_remaining = self.special_cooldown
        self.animation_state = AnimationState.SPECIAL_SKILL
        self.current_frame = 0
        return True
    
    def get_attack_hitbox(self):
        """Get the hitbox for the current attack"""
        if not self.is_attacking and not self.using_special:
            return None
        
        # Calculate attack hitbox based on direction
        if self.direction == Direction.RIGHT:
            attack_x = self.x + self.width * 0.8
            attack_width = self.width * 0.8
        else:  # LEFT
            attack_x = self.x - self.width * 0.8
            attack_width = self.width * 0.8
        
        attack_y = self.y + self.height * 0.2
        attack_height = self.height * 0.6
        
        return pygame.Rect(attack_x, attack_y, attack_width, attack_height)
    
    def calculate_damage(self, target):
        """Calculate damage dealt to target"""
        base_damage = self.damage
        
        # Critical hit chance
        import random
        if random.random() < self.critical_chance:
            base_damage = int(base_damage * self.critical_damage)
        
        return base_damage
    
    def move_towards_target(self, target_x, target_y, dt):
        """Move character towards a target position"""
        if not self.is_alive or self.is_attacking:
            return
        
        dx = target_x - self.x
        
        # Determine movement direction
        direction = 1 if dx > 0 else -1
        
        # Don't move if very close
        if abs(dx) < 10:
            self.is_moving = False
            return
        
        # Move character
        self.x += direction * self.speed * dt * 60
        
        # Update direction
        self.direction = Direction.RIGHT if direction > 0 else Direction.LEFT
        
        # Set moving state
        self.is_moving = True
        
        # Update animation
        if self.is_moving and self.animation_state not in [AnimationState.ATTACKING_1, 
                                                         AnimationState.ATTACKING_2, 
                                                         AnimationState.ATTACKING_3,
                                                         AnimationState.HURT,
                                                         AnimationState.DYING,
                                                         AnimationState.SPECIAL_SKILL]:
            self.animation_state = AnimationState.WALKING
    
    def land(self):
        """Handle landing after falling"""
        self.is_falling = False
        self.is_jumping = False
        self.y_velocity = 0
        
        if self.animation_state == AnimationState.FALLING:
            self.animation_state = AnimationState.IDLE
    
    def jump(self):
        """Make character jump"""
        if not self.is_alive or self.is_jumping or self.is_falling:
            return False
        
        self.is_jumping = True
        self.is_falling = False
        self.y_velocity = self.jump_strength
        self.animation_state = AnimationState.JUMPING
        return True
    
    def start_defend(self):
        """Start defending"""
        if not self.is_alive or self.is_attacking or self.using_special:
            return False
        
        self.is_defending = True
        self.animation_state = AnimationState.DEFENDING
        return True
    
    def stop_defend(self):
        """Stop defending"""
        if self.is_defending:
            self.is_defending = False
            if self.animation_state == AnimationState.DEFENDING:
                self.animation_state = AnimationState.IDLE
            return True
        return False
    
    def handle_input(self, keys, space_pressed):
        """Handle input for character control - to be implemented by subclasses"""
        pass
