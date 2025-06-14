import random
import pygame
import os
from src.utils.SpriteSheet import SpriteSheet
from src.model.DungeonEntity import AnimationState, Direction
import sqlite3


class Monster(pygame.sprite.Sprite):
    def __init__(self, name: str, health: int, attack_damage: int, is_boss: bool, x = 0, y = 0):
        super().__init__()  # Initialize pygame.sprite.Sprite

        self.__name = name
        self.__health = health
        self.__max_health = health
        self.__attack_damage = attack_damage
        self.__is_boss = is_boss
        self.__is_alive = True  # Add this line

        #position properties
        self.x = x
        self.y = y
        self.ground_y = y


        # Optional attributes you can set in subclasses
        self.__chance_to_hit = 1.0
        self.__min_damage = attack_damage
        self.__max_damage = attack_damage
        self.__chance_to_heal = 0.0
        self.__min_heal = 0
        self.__max_heal = 0

        # Add attack range attribute
        self.__attack_range = 100  # Default attack range in pixels
        self.__attack_cooldown = 0  # Cooldown timer for attacks
        self.__attack_cooldown_max = 1.0  # 1 second between attacks

        # Target for AI behavior
        self.__target = None

        self.ground_constrained = False
        self.ground_y = y
        self.gravity_enabled = True

        # Default movement speed (can be overridden in subclasses)
        self.__movement_speed = 30.0

        #Animation properties
        self.__animation_state = getattr(AnimationState, 'IDLE', 'idle')
        self.__direction = getattr(Direction, 'RIGHT', 'right')
        self.__is_invulnerable = False
        self.__invulnerable_timer = 0

        self._load_sprite_from_database()
        self._load_movement_stats()

        # Required pygame sprite attributes - subclasses should override these
        self.image = pygame.Surface((32, 32))  # Default placeholder
        self.image.fill((255, 0, 0))  # Fill with red so it's visible as fallback
        pygame.draw.rect(self.image, (0, 0, 0), pygame.Rect(0, 0, 32, 32), 2)  # Add black border
        self.rect = self.image.get_rect()

        # Fallback sprite setup if database loading fails
        if not hasattr(self, 'image') or self.image is None:
            self._create_fallback_sprite()

        # Set up rect
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y

        # ADD hitbox
        self._initialize_hitbox()

        # Animation state tracking
        self.animation_state = "idle"  # Default animation state
        self.is_attacking = False      # Flag for attack animation
        self.attack_timer = 0          # Timer for attack animation
        self.attack_animation_duration = 0.5  # Attack animation duration in seconds
        
        # Debug flag - for development use
        self.debug = False

    def _load_sprite_from_database(self):
        """Load monster sprite from database using existing monster_animations table"""
        try:
            conn = sqlite3.connect('game_data.db')
            c = conn.cursor()

            # Get monster type from name
            monster_type = self._get_monster_type_from_name()

            # Try both 'IDLE' and 'idle' animation states for compatibility
            for idle_state in ['IDLE', 'idle']:
                c.execute('''
                          SELECT sprite_path, frame_width, frame_height
                          FROM monster_animations
                          WHERE monster_type = ?
                            AND animation_state = ?
                          ''', (monster_type, idle_state))

                result = c.fetchone()
                if result:
                    break

            conn.close()

            if result and os.path.exists(result[0]):
                # Load the sprite image
                sprite_image = pygame.image.load(result[0]).convert_alpha()

                # If it's a sprite sheet, take the first frame
                if hasattr(SpriteSheet, '__init__'):
                    sheet = SpriteSheet(sprite_image)
                    self.image = sheet.get_frame(0, result[1], result[2], scale=1.0)
                else:
                    # Simple image loading
                    self.image = sprite_image

                print(f"Loaded sprite for {self.__name} from database")
                return True

        except Exception as e:
            print(f"Could not load sprite for {self.__name}: {e}")
            return False

        return False

    def _load_movement_stats(self):
        """Load movement stats from database"""
        try:
            conn = sqlite3.connect('game_data.db')
            c = conn.cursor()

            monster_type = self._get_monster_type_from_name()

            # Try to get movement stats from monster_stats table
            c.execute('''
                      SELECT movement_speed, attack_cooldown
                      FROM monster_stats
                      WHERE monster_type = ?
                      ''', (monster_type,))

            result = c.fetchone()
            conn.close()

            if result:
                if result[0] is not None:  # movement_speed
                    self.__movement_speed = result[0]
                if result[1] is not None:  # attack_cooldown
                    self.__attack_cooldown_max = result[1]
                print(f"Loaded movement stats for {monster_type}")

        except Exception as e:
            print(f"Could not load movement stats: {e}")
            # Use defaults already set in constructor




    # Add a custom draw method like DemonBoss has
    def draw(self, surface, camera_x=0, camera_y=0):
        """Draw the monster on the given surface"""
        # Calculate screen position
        screen_x = self.rect.x - camera_x
        screen_y = self.rect.y - camera_y
        
        # Draw the monster sprite
        surface.blit(self.image, (screen_x, screen_y))
        
        # Optionally draw debug information
        if self.debug:
            # Draw border around sprite
            pygame.draw.rect(surface, (255, 255, 0), 
                            pygame.Rect(screen_x, screen_y, self.rect.width, self.rect.height), 
                            2)
            
            # Draw hitbox if it exists
            if hasattr(self, 'hitbox'):
                hitbox_screen_x = self.hitbox.x - camera_x
                hitbox_screen_y = self.hitbox.y - camera_y
                pygame.draw.rect(surface, (0, 255, 255),
                                pygame.Rect(hitbox_screen_x, hitbox_screen_y, 
                                            self.hitbox.width, self.hitbox.height),
                                1)

    def _get_monster_type_from_name(self):
        """Get monster type string from monster name"""
        name_lower = self.__name.lower()
        if 'skeleton' in name_lower:
            return 'skeleton'
        elif 'ogre' in name_lower or 'grar' in name_lower:
            return 'ogre'
        elif 'demon' in name_lower or 'boss' in name_lower:
            return 'demon_boss'
        elif 'gorgon' in name_lower:
            return 'gorgon'
        elif 'orc' in name_lower:
            return 'orc'
        else:
            return 'skeleton'  # Default fallback

    def _create_fallback_sprite(self):
        """Create a colored rectangle as fallback sprite"""
        # Different colors based on monster type
        name_lower = self.__name.lower()
        if 'skeleton' in name_lower:
            color = (200, 200, 200)  # Light gray
            size = (48, 64)
        elif 'ogre' in name_lower:
            color = (139, 69, 19)  # Brown
            size = (64, 80)
        elif 'demon' in name_lower or 'boss' in name_lower:
            color = (150, 0, 0)  # Dark red
            size = (96, 120)
        else:
            color = (255, 0, 255)  # Magenta for unknown
            size = (48, 64)

        self.image = pygame.Surface(size, pygame.SRCALPHA)
        self.image.fill(color)
        # Add border for visibility
        pygame.draw.rect(self.image, (0, 0, 0), pygame.Rect(0, 0, size[0], size[1]), 2)
        print(f"Created fallback sprite for {self.__name}")

    def _initialize_hitbox(self):
        """Initialize collision hitbox"""
        if hasattr(self, 'image') and self.image:
            hitbox_width = int(self.image.get_width() * 0.7)
            hitbox_height = int(self.image.get_height() * 0.8)
            hitbox_x = self.rect.x + (self.rect.width - hitbox_width) // 2
            hitbox_y = self.rect.y + (self.rect.height - hitbox_height) // 2
            self.hitbox = pygame.Rect(hitbox_x, hitbox_y, hitbox_width, hitbox_height)
        else:
            self.hitbox = pygame.Rect(self.rect.x, self.rect.y, 32, 32)

    def _update_hitbox(self):
        """Update hitbox position to match sprite"""
        if hasattr(self, 'hitbox'):
            hitbox_width = int(self.rect.width * 0.7)
            hitbox_height = int(self.rect.height * 0.8)
            self.hitbox.x = self.rect.x + (self.rect.width - hitbox_width) // 2
            self.hitbox.y = self.rect.y + (self.rect.height - hitbox_height) // 2

    def set_target(self, target):
        """Set the target for this monster to follow/attack"""
        self.__target = target

    def get_target(self):
        """Get the current target"""
        return self.__target

    def get_name(self):
        """Get the monster's name"""
        return self.__name

    def get_health(self):
        """Get current health"""
        return self.__health

    def get_max_health(self):
        """Get maximum health"""
        return self.__max_health

    def get_enemy_type(self):
        """Get the enemy type"""
        return self._get_monster_type_from_name()

    def get_monster_type(self):
        """Get the monster type"""
        return self._get_monster_type_from_name()

    def get_animation_state(self):
        """Get current animation state"""
        return self.__animation_state

    def get_direction(self):
        """Get current facing direction"""
        return self.__direction

    def is_invulnerable(self):
        """Check if monster is currently invulnerable"""
        return self.__is_invulnerable

    def get_x(self):
        """Get x position"""
        return self.rect.x

    def get_y(self):
        """Get y position"""
        return self.rect.y



    # Change the is_alive method to a property to match the subclasses
    @property
    def is_alive(self):
        """Check if monster is alive"""
        return self.__health > 0 and self.__is_alive
    
    # Add the missing set_position method
    def set_position(self, x, y):
        """Set the position of the monster"""
        self.rect.x = x
        self.rect.y = y
        # Update additional position properties if they exist
        if hasattr(self, 'x'):
            self.x = x
        if hasattr(self, 'y'):
            self.y = y
        
        # Update hitbox if it exists
        if hasattr(self, 'hitbox'):
            self._update_hitbox()
            
    # Add these missing methods that Goblin expects
    def set_movement_speed(self, speed):
        """Set the monster's movement speed"""
        self.__movement_speed = speed
    
    def get_movement_speed(self):
        """Get the monster's movement speed"""
        return self.__movement_speed
    
    def set_attack_range(self, range_value):
        """Set the monster's attack range"""
        self.__attack_range = range_value
    
    def get_attack_range(self):
        """Get the monster's attack range"""
        return self.__attack_range
    
    def set_attack_cooldown(self, cooldown):
        """Set the monster's attack cooldown"""
        self.__attack_cooldown_max = cooldown
        self.__attack_cooldown = 0  # Reset current cooldown
    
    def get_chance_to_hit(self):
        """Get the monster's chance to hit"""
        return self.__chance_to_hit
    
    def set_chance_to_hit(self, chance):
        """Set the monster's chance to hit"""
        self.__chance_to_hit = max(0.0, min(1.0, chance))  # Clamp between 0 and 1
    
    def get_damage_range(self):
        """Get the monster's damage range as (min, max)"""
        return (self.__min_damage, self.__max_damage)
    
    def set_damage_range(self, min_damage, max_damage):
        """Set the monster's damage range"""
        self.__min_damage = min_damage
        self.__max_damage = max(min_damage, max_damage)
    
    def get_heal_chance(self):
        """Get the monster's chance to heal"""
        return self.__chance_to_heal
    
    def set_heal_chance(self, chance):
        """Set the monster's chance to heal"""
        self.__chance_to_heal = max(0.0, min(1.0, chance))  # Clamp between 0 and 1
    
    def get_heal_range(self):
        """Get the monster's healing range as (min, max)"""
        return (self.__min_heal, self.__max_heal)
    
    def set_heal_range(self, min_heal, max_heal):
        """Set the monster's healing range"""
        self.__min_heal = min_heal
        self.__max_heal = max(min_heal, max_heal)

    def is_visible_on_screen(self, camera_x, camera_y, screen_width, screen_height):
        """Check if the monster is visible on screen with current camera position"""
        # Calculate the monster's position on screen
        screen_x = self.rect.x - camera_x
        screen_y = self.rect.y - camera_y

        # Check if monster is at least partially visible on screen
        return (screen_x + self.rect.width > 0 and screen_x < screen_width and
                screen_y + self.rect.height > 0 and screen_y < screen_height)

    def take_damage(self, damage):
        """Take damage, return True if monster died, False otherwise"""
        if not self.__is_alive or self.__is_invulnerable or damage <= 0:
            return False

        # Apply damage
        self.__health -= damage
        print(f"{self.__name} takes {damage} damage! HP: {self.__health}/{self.__max_health}")

        # Check if dead
        if self.__health <= 0:
            self.__health = 0
            self.__is_alive = False
            print(f"{self.__name} has been defeated!")
            return True  # Monster died
        else:
            # Set brief invulnerability
            self.__is_invulnerable = True
            self.__invulnerable_timer = 0.5
            return False  # Monster took damage but didn't die

    def move_towards_target(self, target_x, target_y, dt):
        """Move towards target position along X-axis only"""
        if not self.__is_alive:
            return

        # Calculate distance to target
        dx = target_x - self.rect.centerx
        distance = abs(dx)

        # Set direction
        self.__direction = getattr(Direction, 'RIGHT' if dx > 0 else 'LEFT', 'right' if dx > 0 else 'left')

        # Don't move if in attack range
        if distance <= self.__attack_range:
            return

        # Move towards target
        move_distance = self.__movement_speed * dt
        move_x = min(move_distance, distance) * (1 if dx > 0 else -1)

        # Update position
        self.rect.x += move_x
        self.x = self.rect.x

        # Keep Y position fixed to ground
        self.rect.y = self.ground_y
        self.y = self.ground_y

        self._update_hitbox()

    def attack(self, target):
        """Attack the target"""
        if self.__attack_cooldown > 0 or not self.__is_alive:
            return False

        if random.random() <= self.__chance_to_hit:
            damage = random.randint(self.__min_damage, self.__max_damage)

            if hasattr(target, 'take_damage'):
                target.take_damage(damage)
                print(f"{self.__name} hits for {damage} damage!")

            self.__attack_cooldown = self.__attack_cooldown_max
            return True
        else:
            print(f"{self.__name} missed!")
            self.__attack_cooldown = self.__attack_cooldown_max / 2
            return False

    def update(self, dt=0):
        """Update monster state and AI behavior"""
        if not self.__is_alive:
            return

        # Update timers
        if self.__attack_cooldown > 0:
            self.__attack_cooldown -= dt

        if self.__is_invulnerable:
            self.__invulnerable_timer -= dt
            if self.__invulnerable_timer <= 0:
                self.__is_invulnerable = False

        # AI behavior
        if self.__target and self.__is_alive:
            if hasattr(self.__target, 'rect'):
                target_x = self.__target.rect.centerx
                target_y = self.__target.rect.centery
            else:
                target_x = getattr(self.__target, 'x', 0)
                target_y = getattr(self.__target, 'y', 0)

            distance = ((target_x - self.rect.centerx) ** 2 + (target_y - self.rect.centery) ** 2) ** 0.5

            if distance <= self.__attack_range and self.__attack_cooldown <= 0:
                self.attack(self.__target)
            else:
                self.move_towards_target(target_x, target_y, dt)