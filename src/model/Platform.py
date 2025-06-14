import pygame


class Platform:
    """
    Class representing a platform that the player can stand on.

    This class handles different types of platforms including normal, moving,
    breakable, and one-way platforms. Each platform type has specific behaviors
    and collision properties.

    Attributes:
        x (float): X coordinate of the platform
        y (float): Y coordinate of the platform
        width (int): Width of the platform in pixels
        height (int): Height of the platform in pixels
        platform_type (str): Type of platform ("normal", "moving", "breakable", "one-way")
        rect (pygame.Rect): Collision rectangle for the platform
        is_moving (bool): True if platform moves
        move_speed (int): Speed of movement for moving platforms
        move_distance (int): Maximum distance platform can move
        move_direction (int): Direction of movement (1 or -1)
        start_x (float): Initial X position
        start_y (float): Initial Y position
        move_axis (str): Axis of movement ("x" or "y")
        is_breakable (bool): True if platform can be broken
        health (int): Number of hits before platform breaks
        broken (bool): True if platform is broken
        is_one_way (bool): True if platform allows jumping up through it
    """

    def __init__(self, x, y, width, height, platform_type="normal"):
        """
        Initialize a new Platform instance.

        Args:
            x (float): X coordinate of the platform
            y (float): Y coordinate of the platform
            width (int): Width of the platform in pixels
            height (int): Height of the platform in pixels
            platform_type (str, optional): Type of platform. Defaults to "normal".
                Valid types: "normal", "moving", "breakable", "one-way"
        """
        self.x = x
        self.y = y
        self.width = width
        self.height = height
        self.platform_type = platform_type
        self.rect = pygame.Rect(x, y, width, height)

        # For moving platforms
        self.is_moving = platform_type == "moving"
        self.move_speed = 2
        self.move_distance = 100
        self.move_direction = 1  # 1 for right/down, -1 for left/up
        self.start_x = x
        self.start_y = y
        self.move_axis = "x"  # "x" or "y"

        # For breakable platforms
        self.is_breakable = platform_type == "breakable"
        self.health = 3  # Number of hits before breaking
        self.broken = False

        # For one-way platforms (can jump up through them)
        self.is_one_way = platform_type == "one-way"

    def update(self, dt):
        """
        Update platform state for each frame.

        Handles movement for moving platforms and updates collision rectangle.
        Platform will reverse direction when reaching movement limits.

        Args:
            dt (float): Delta time since last frame in seconds
        """
        if self.is_moving and not self.broken:
            # Update position for moving platforms
            if self.move_axis == "x":
                self.x += self.move_speed * self.move_direction * dt * 60

                # Check if reached movement limits
                if abs(self.x - self.start_x) >= self.move_distance:
                    self.move_direction *= -1  # Reverse direction
            else:  # move_axis == "y"
                self.y += self.move_speed * self.move_direction * dt * 60

                # Check if reached movement limits
                if abs(self.y - self.start_y) >= self.move_distance:
                    self.move_direction *= -1  # Reverse direction

            # Update rect
            self.rect.x = self.x
            self.rect.y = self.y

    def take_damage(self):
        """
        Apply damage to a breakable platform.

        Reduces platform health by 1. If health reaches 0, the platform
        is marked as broken and collisions are disabled.

        Returns:
            bool: True if damage was applied (platform is breakable and not broken),
                  False otherwise
        """
        if self.is_breakable and not self.broken:
            self.health -= 1
            if self.health <= 0:
                self.broken = True
                # Add animation or particle effect for breaking

                # Disable collisions when broken
                self.rect.width = 0
                self.rect.height = 0
            return True
        return False


class PlatformManager:
    """
    Class to manage a collection of platforms and handle collision detection.

    This class maintains a list of platforms and provides methods to update
    all platforms and check collisions with game entities like the hero.

    Attributes:
        platforms (list): List of Platform objects managed by this instance
    """

    def __init__(self):
        """
        Initialize a new PlatformManager instance.

        Creates an empty list to store platforms.
        """
        self.platforms = []

    def add_platform(self, platform):
        """
        Add a platform to the manager.

        Args:
            platform (Platform): Platform instance to add to the collection
        """
        self.platforms.append(platform)

    def update(self, dt):
        """
        Update all platforms managed by this instance.

        Calls the update method on each platform in the collection.

        Args:
            dt (float): Delta time since last frame in seconds
        """
        for platform in self.platforms:
            platform.update(dt)

    def check_collisions(self, hero):
        """
        Check and resolve collisions between hero and all platforms.

        Performs both vertical and horizontal collision checks if the hero
        is alive. Vertical collisions handle landing on platforms, while
        horizontal collisions prevent movement through solid platforms.

        Args:
            hero: Hero object to check collisions for (must have is_alive attribute)
        """
        if hero.is_alive:
            self._check_vertical_collisions(hero)
            self._check_horizontal_collisions(hero)

    def _check_vertical_collisions(self, hero):
        """
        Check for vertical collisions (landing on platforms).

        Creates a collision rectangle at the hero's feet and checks for
        collisions with platforms. Handles landing mechanics and moving
        platform attachment.

        Args:
            hero: Hero object with position, size, and movement properties
        """
        # Create a rect for the hero's feet
        feet_rect = pygame.Rect(
            hero.x + hero.width / 4,
            hero.y + hero.height - 5,
            hero.width / 2,
            10
        )

        # Only check while falling
        if hero.is_falling:
            for platform in self.platforms:
                if platform.broken:
                    continue

                # Skip one-way platforms if hero is moving upward
                if platform.is_one_way and hero.y_velocity < 0:
                    continue

                # Check if feet collide with platform
                if feet_rect.colliderect(platform.rect):
                    # Land on the platform
                    hero.y = platform.rect.y - hero.height
                    hero.land()

                    # If it's a moving platform, attach hero to it
                    if platform.is_moving:
                        if platform.move_axis == "x":
                            hero.x += platform.move_speed * platform.move_direction

    def _check_horizontal_collisions(self, hero):
        """
        Check for horizontal collisions with platforms.

        Creates collision rectangles on the left and right sides of the hero
        and pushes the hero away from solid platforms to prevent clipping.
        One-way platforms are ignored for horizontal collisions.

        Args:
            hero: Hero object with position and size properties
        """
        # Create left and right side collision rects
        left_rect = pygame.Rect(
            hero.x,
            hero.y + 10,
            10,
            hero.height - 20
        )

        right_rect = pygame.Rect(
            hero.x + hero.width - 10,
            hero.y + 10,
            10,
            hero.height - 20
        )

        # Check left side collisions
        for platform in self.platforms:
            if platform.broken or platform.is_one_way:
                continue

            if left_rect.colliderect(platform.rect):
                # Push hero right
                hero.x = platform.rect.right

            if right_rect.colliderect(platform.rect):
                # Push hero left
                hero.x = platform.rect.left - hero.width