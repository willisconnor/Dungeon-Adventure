import math
import pygame
from enum import Enum

from src.model.DungeonEntity import Direction


class ProjectileType(Enum):
    """
    Enumeration for different types of projectiles in the game.

    Constants:
        ARROW: Arrow projectile type (value: 0)
        FIREBALL: Fireball projectile type (value: 1)
    """
    ARROW = 0
    FIREBALL = 1


class Projectile:
    """
    Represents a projectile entity in the game such as arrows and fireballs.

    This class handles the movement, animation, collision detection, and lifecycle
    of projectiles fired by game entities.

    Attributes:
        x (float): Current x-coordinate position
        y (float): Current y-coordinate position
        direction (Direction): Direction the projectile is traveling
        projectile_type (ProjectileType): Type of projectile (ARROW or FIREBALL)
        owner (Entity): Reference to the entity that fired this projectile
        damage (int): Damage dealt by this projectile
        speed (float): Movement speed of the projectile
        max_range (float): Maximum distance the projectile can travel
        distance_traveled (float): Current distance traveled from start position
        active (bool): Whether the projectile is still active
        width (int): Width of the projectile sprite
        height (int): Height of the projectile sprite
        hitbox (pygame.Rect): Collision detection rectangle
        frame_index (int): Current animation frame index
        animation_counter (float): Counter for animation timing
        frames (list): List of loaded sprite frames
        frame_count (int): Total number of animation frames
        start_x (float): Starting x-coordinate for range calculation
        start_y (float): Starting y-coordinate for range calculation
        hit_targets (set): Set of targets already hit by this projectile
        angle (float): Trajectory angle in degrees
        is_homing (bool): Whether this projectile homes in on targets
        target (Entity): Target entity for homing projectiles
        homing_strength (float): Strength of homing effect (0.0 to 1.0)
    """

    def __init__(self, x, y, direction, projectile_type, owner, damage=0, speed=0, range=0):
        """
        Initialize a new projectile instance.

        Args:
            x (float): Starting x-coordinate
            y (float): Starting y-coordinate
            direction (Direction): Direction the projectile travels
            projectile_type (ProjectileType): Type of projectile to create
            owner (Entity): Entity that fired this projectile
            damage (int, optional): Damage dealt by projectile. Defaults to 0.
            speed (float, optional): Movement speed. Defaults to 0.
            range (float, optional): Maximum travel distance. Defaults to 0.
        """
        self.x = x
        self.y = y
        self.direction = direction
        self.projectile_type = projectile_type
        self.owner = owner
        self.damage = damage
        self.speed = speed
        self.max_range = range
        self.distance_traveled = 0
        self.active = True

        # Set projectile dimensions based on type
        if projectile_type == ProjectileType.ARROW:
            self.width = 64
            self.height = 96
        elif projectile_type == ProjectileType.FIREBALL:
            self.width = 64
            self.height = 64

        # Initialize hitbox
        self.hitbox = pygame.Rect(x, y, self.width, self.height)

        # Animation properties
        self.frame_index = 0
        self.animation_counter = 0
        self.frames = []
        self.frame_count = 0

        # Load sprite frames
        self._load_sprite_frames()

        # Cache the starting position for range calculation
        self.start_x = x
        self.start_y = y

        # Track what's been hit by this projectile
        self.hit_targets = set()

        # Trajectory properties
        self.angle = 0
        if direction == Direction.RIGHT:
            self.angle = 0
        else:  # Direction.LEFT
            self.angle = 180

        # For homing projectiles
        self.is_homing = False
        self.target = None
        self.homing_strength = 0.1

    def _load_sprite_frames(self):
        """
        Load sprite frames for projectile animation from asset files.

        Loads different sprites based on projectile type:
        - FIREBALL: Loads from Charge.png sprite sheet (64x64 frames)
        - ARROW: Loads from Arrow.png single sprite

        Falls back to colored rectangles if sprite loading fails.

        Raises:
            Exception: If sprite files cannot be loaded (handled gracefully)
        """
        try:
            if self.projectile_type == ProjectileType.FIREBALL:
                # Load fireball sprite sheet from Charge.png
                sprite_path = "assets/sprites/heroes/cleric/Fire_Cleric/Charge.png"
                sprite_sheet = pygame.image.load(sprite_path).convert_alpha()

                # Get sprite sheet dimensions
                sheet_width, sheet_height = sprite_sheet.get_size()

                # Use 64x64 frames
                frame_width = 64
                frame_height = 64
                num_frames = sheet_width // frame_width

                # Extract frames from sprite sheet
                self.frames = []
                for i in range(num_frames):
                    x = i * frame_width
                    frame = pygame.Surface((frame_width, frame_height), pygame.SRCALPHA)
                    frame.blit(sprite_sheet, (0, 0), (x, 0, frame_width, frame_height))
                    self.frames.append(frame)

                self.frame_count = len(self.frames)
                print(f"Loaded {self.frame_count} fireball frames from Charge.png (64x64)")

            elif self.projectile_type == ProjectileType.ARROW:
                # Load arrow sprite
                sprite_path = "assets/sprites/heroes/archer/Samurai_Archer/Arrow.png"
                arrow_sprite = pygame.image.load(sprite_path).convert_alpha()
                self.frames = [arrow_sprite]
                self.frame_count = 1

        except Exception as e:
            print(f"Error loading projectile sprites: {e}")
            # Fallback: create colored rectangles
            if self.projectile_type == ProjectileType.FIREBALL:
                fallback_sprite = pygame.Surface((32, 32), pygame.SRCALPHA)
                fallback_sprite.fill((255, 100, 0))  # Orange color
                self.frames = [fallback_sprite]
            else:  # Arrow
                fallback_sprite = pygame.Surface((32, 8), pygame.SRCALPHA)
                fallback_sprite.fill((200, 200, 100))  # Yellow color
                self.frames = [fallback_sprite]

            self.frame_count = 1

    def update(self, dt):
        """
        Update projectile position, animation, and check expiration.

        Handles movement based on angle and speed, applies homing effects if enabled,
        updates animation frames, and deactivates projectile if it exceeds max range.

        Args:
            dt (float): Delta time since last update in seconds
        """
        if not self.active:
            return

        # Calculate movement based on angle
        dx = self.speed * math.cos(math.radians(self.angle)) * dt * 60
        dy = self.speed * math.sin(math.radians(self.angle)) * dt * 60

        # Apply homing effect if this is a homing projectile
        if self.is_homing and self.target and self.target.is_alive:
            # Calculate angle to target
            target_dx = self.target.x - self.x
            target_dy = self.target.y - self.y
            target_angle = math.degrees(math.atan2(target_dy, target_dx))

            # Gradually adjust angle towards target
            angle_diff = (target_angle - self.angle + 180) % 360 - 180
            self.angle += angle_diff * self.homing_strength

            # Recalculate movement with new angle
            dx = self.speed * math.cos(math.radians(self.angle)) * dt * 60
            dy = self.speed * math.sin(math.radians(self.angle)) * dt * 60

        # Move projectile
        self.x += dx
        self.y += dy

        # Update hitbox position
        self.hitbox.x = self.x
        self.hitbox.y = self.y

        # Update animation
        self._update_animation(dt)

        # Calculate distance traveled
        dx = self.x - self.start_x
        dy = self.y - self.start_y
        self.distance_traveled = (dx ** 2 + dy ** 2) ** 0.5

        # Deactivate if exceeds maximum range
        if self.distance_traveled >= self.max_range:
            self.active = False

    def _update_animation(self, dt):
        """
        Update projectile animation frames based on projectile type.

        Only fireballs are animated, arrows remain static.

        Args:
            dt (float): Delta time since last update in seconds
        """
        # Different animation speed by projectile type
        frame_rate = 8 if self.projectile_type == ProjectileType.FIREBALL else 0

        # Only animate fireballs
        if self.projectile_type == ProjectileType.FIREBALL:
            self.animation_counter += dt * 60
            if self.animation_counter >= frame_rate:
                self.animation_counter = 0
                self.frame_index = (self.frame_index + 1) % self.frame_count

    def check_collision(self, targets):
        """
        Check collision with potential targets and apply damage.

        Args:
            targets (list): List of target entities to check collision against

        Returns:
            list: List of targets that were hit by this projectile
        """
        if not self.active:
            return []

        hit_targets = []

        for target in targets:
            # Skip already hit targets or dead targets
            if target in self.hit_targets or not target.is_alive:
                continue

            # Check collision with target's hitbox
            if self.hitbox.colliderect(target.hitbox):
                # Process hit
                hit = target.take_damage(self.damage)
                if hit:
                    self.hit_targets.add(target)
                    hit_targets.append(target)

                    # For arrow, deactivate after hitting one target
                    if self.projectile_type == ProjectileType.ARROW:
                        self.active = False
                        break
                    # Fireball continues but can hit each target only once

        return hit_targets

    def get_current_sprite(self):
        """
        Get the current sprite frame for rendering this projectile.

        Returns:
            pygame.Surface: Current sprite frame, or None if no frames loaded
        """
        if self.frames and self.frame_index < len(self.frames):
            return self.frames[self.frame_index]
        return None

    def get_sprite_path(self):
        """
        Get the sprite file path for the current projectile frame.

        Returns:
            str: Path to the sprite file for this projectile type
        """
        if self.projectile_type == ProjectileType.ARROW:
            return "assets/sprites/heroes/archer/Samurai_Archer/Arrow.png"
        elif self.projectile_type == ProjectileType.FIREBALL:
            return f"assets/sprites/heroes/cleric/Fire_Cleric/Fireball_{self.frame_index}.png"


class ProjectileManager:
    """
    Manages all projectiles in the game.

    This class handles updating, collision detection, and cleanup of all active
    projectiles in the game world.

    Attributes:
        projectiles (list): List of all active projectiles
    """

    def __init__(self):
        """
        Initialize a new ProjectileManager instance.
        """
        self.projectiles = []

    def add_projectile(self, projectile):
        """
        Add a projectile to be managed by this manager.

        Args:
            projectile (Projectile): The projectile instance to add
        """
        self.projectiles.append(projectile)

    def update(self, dt):
        """
        Update all active projectiles and remove inactive ones.

        Args:
            dt (float): Delta time since last update in seconds
        """
        # Update each projectile
        for projectile in self.projectiles:
            projectile.update(dt)

        # Remove inactive projectiles
        self.projectiles = [p for p in self.projectiles if p.active]

    def check_collisions(self, targets):
        """
        Check collisions for all projectiles against a list of targets.

        Args:
            targets (list): List of target entities to check collisions against

        Returns:
            list: List of all targets hit by any projectile
        """
        hit_targets = []

        for projectile in self.projectiles:
            targets_hit = projectile.check_collision(targets)
            hit_targets.extend(targets_hit)

        return hit_targets

    def clear(self):
        """
        Remove all projectiles from the manager.
        """
        self.projectiles = []


def extend_archer_with_projectiles(Archer):
    """
    Extend the Archer class with projectile firing functionality.

    This function modifies the Archer class to fire arrows during attacks
    instead of just performing melee attacks.

    Args:
        Archer (class): The Archer class to extend

    Returns:
        class: The modified Archer class with projectile functionality
    """
    # Store the original attack method
    original_attack = Archer.attack

    def new_attack(self, targets):
        """
        Override attack method to fire arrows.

        Args:
            targets (list): List of potential targets

        Returns:
            list: List of targets hit (from original melee attack)
        """
        if not self.is_attacking or not self.is_alive:
            return []

        # Get a reference to the game's projectile manager
        projectile_manager = self.projectile_manager

        # Calculate arrow starting position
        if self.direction == Direction.RIGHT:
            start_x = self.x + 40
        else:
            start_x = self.x - 10

        start_y = self.y + 20

        # Create and fire arrow at appropriate animation frame
        if self.frame_index == 2 and not hasattr(self, 'arrow_fired'):
            # Create new arrow projectile
            arrow = Projectile(
                x=start_x,
                y=start_y,
                direction=self.direction,
                projectile_type=ProjectileType.ARROW,
                owner=self,
                damage=self.damage,
                speed=self.projectile_speed,
                range=self.projectile_range
            )

            # Add to projectile manager
            projectile_manager.add_projectile(arrow)

            # Mark arrow as fired for this attack
            self.arrow_fired = True

        # Reset arrow_fired flag when attack is complete
        if self.attack_complete:
            if hasattr(self, 'arrow_fired'):
                delattr(self, 'arrow_fired')

        # Still call the original attack method for melee range attacks
        return original_attack(self, targets)

    # Replace the attack method
    Archer.attack = new_attack

    return Archer


def extend_cleric_with_projectiles(Cleric):
    """
    Extend the Cleric class with fireball casting functionality.

    This function modifies the Cleric class to cast fireballs during
    special ability activation.

    Args:
        Cleric (class): The Cleric class to extend

    Returns:
        class: The modified Cleric class with projectile functionality
    """
    # Store the original special ability method
    original_special = Cleric.activate_special_ability

    def new_special_ability(self):
        """
        Override special ability to cast fireballs.

        Calls the original special ability and then creates and fires
        a fireball projectile.
        """
        # First call the original special ability
        original_special(self)

        # Get a reference to the game's projectile manager
        projectile_manager = self.projectile_manager

        # Calculate fireball starting position
        if self.direction == Direction.RIGHT:
            start_x = self.x + 50
        else:
            start_x = self.x - 20

        start_y = self.y + 10

        # Create and cast fireball
        fireball = Projectile(
            x=start_x,
            y=start_y,
            direction=self.direction,
            projectile_type=ProjectileType.FIREBALL,
            owner=self,
            damage=self.damage * 2,  # Fireballs deal double damage
            speed=10,
            range=300
        )

        # Add to projectile manager
        projectile_manager.add_projectile(fireball)

    # Replace the special ability method
    Cleric.activate_special_ability = new_special_ability

    return Cleric