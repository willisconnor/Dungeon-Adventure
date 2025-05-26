import pygame


class Platform:
    """Class representing a platform that the player can stand on"""

    def __init__(self, x, y, width, height, platform_type="normal"):
        self.x = x
        self.y = y
        self.width = width
        self.height = height
        self.platform_type = platform_type  # normal, moving, breakable, one-way
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
        """Update platform state"""
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
        """Damage a breakable platform"""
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
    """Class to manage a collection of platforms"""

    def __init__(self):
        self.platforms = []

    def add_platform(self, platform):
        """Add a platform to the manager"""
        self.platforms.append(platform)

    def update(self, dt):
        """Update all platforms"""
        for platform in self.platforms:
            platform.update(dt)

    def check_collisions(self, hero):
        """Check and resolve collisions between hero and platforms"""
        if hero.is_alive:
            self._check_vertical_collisions(hero)
            self._check_horizontal_collisions(hero)

    def _check_vertical_collisions(self, hero):
        """Check for vertical collisions (landing on platforms)"""
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
        """Check for horizontal collisions with platforms"""
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


# Example usage:
"""
# In your game initialization
platform_manager = PlatformManager()

# Add some platforms
ground = Platform(0, 550, 800, 50)
platform_manager.add_platform(ground)

floating_platform = Platform(300, 400, 200, 20)
platform_manager.add_platform(floating_platform)

moving_platform = Platform(100, 300, 100, 20, platform_type="moving")
moving_platform.move_distance = 150
platform_manager.add_platform(moving_platform)

# In your game loop
def update(dt):
    # Update hero
    hero.update(dt)

    # Update platforms
    platform_manager.update(dt)

    # Check collisions
    platform_manager.check_collisions(hero)
"""