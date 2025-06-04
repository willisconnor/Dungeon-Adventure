import pygame


class Platform:
    """Class representing a platform that the player can stand on"""

    def __init__(self, x, y, width, height, platform_type="normal"):
        self.__x = x
        self.__y = y
        self.__width = width
        self.__height = height
        self.__platform_type = platform_type  # normal, moving, breakable, one-way
        self.__rect = pygame.Rect(x, y, width, height)

        # For moving platforms
        self.__is_moving = platform_type == "moving"
        self.__move_speed = 2
        self.__move_distance = 100
        self.__move_direction = 1  # 1 for right/down, -1 for left/up
        self.__start_x = x
        self.__start_y = y
        self.__move_axis = "x"  # "x" or "y"

        # For breakable platforms
        self.__is_breakable = platform_type == "breakable"
        self.__health = 3  # Number of hits before breaking
        self.__broken = False

        # For one-way platforms (can jump up through them)
        self.__is_one_way = platform_type == "one-way"

    def update(self, dt):
        """Update platform state"""
        if self.__is_moving and not self.__broken:
            # Update position for moving platforms
            if self.__move_axis == "x":
                self.__x += self.__move_speed * self.__move_direction * dt * 60

                # Check if reached movement limits
                if abs(self.__x - self.__start_x) >= self.__move_distance:
                    self.__move_direction *= -1  # Reverse direction
            else:  # move_axis == "y"
                self.__y += self.__move_speed * self.__move_direction * dt * 60

                # Check if reached movement limits
                if abs(self.__y - self.__start_y) >= self.__move_distance:
                    self.__move_direction *= -1  # Reverse direction

            # Update rect
            self.__rect.x = self.__x
            self.__rect.y = self.__y

    def take_damage(self):
        """Damage a breakable platform"""
        if self.__is_breakable and not self.__broken:
            self.__health -= 1
            if self.__health <= 0:
                self.__broken = True
                # Disable collisions when broken
                self.__rect.width = 0
                self.__rect.height = 0
            return True
        return False

    def render(self, surface, camera_x=0):
        """Render the platform to the surface"""
        if not self.__broken:
            # Calculate position relative to camera
            render_x = self.__x - camera_x

            # Only render if at least partially visible on screen
            if render_x + self.__width > 0 and render_x < surface.get_width():
                # Draw platform (could be replaced with sprite rendering)
                platform_color = (100, 70, 30)  # Brown for normal platforms

                if self.__is_breakable:
                    # Darken color based on remaining health
                    health_factor = self.__health / 3
                    platform_color = (
                        int(150 * health_factor),
                        int(100 * health_factor),
                        int(50 * health_factor)
                    )
                elif self.__is_moving:
                    platform_color = (80, 80, 150)  # Bluish for moving platforms
                elif self.__is_one_way:
                    platform_color = (50, 150, 50)  # Greenish for one-way platforms

                pygame.draw.rect(surface, platform_color,
                                 (render_x, self.__y, self.__width, self.__height))

    # Getters
    def get_x(self):
        """Get platform x position"""
        return self.__x

    def get_y(self):
        """Get platform y position"""
        return self.__y

    def get_width(self):
        """Get platform width"""
        return self.__width

    def get_height(self):
        """Get platform height"""
        return self.__height

    def get_rect(self):
        """Get platform collision rectangle"""
        return self.__rect

    def get_platform_type(self):
        """Get platform type"""
        return self.__platform_type

    def is_moving_platform(self):
        """Check if this is a moving platform"""
        return self.__is_moving

    def is_breakable_platform(self):
        """Check if this is a breakable platform"""
        return self.__is_breakable

    def is_one_way_platform(self):
        """Check if this is a one-way platform"""
        return self.__is_one_way

    def is_broken(self):
        """Check if platform is broken"""
        return self.__broken

    def get_move_speed(self):
        """Get movement speed"""
        return self.__move_speed

    def get_move_direction(self):
        """Get current movement direction"""
        return self.__move_direction

    def get_health(self):
        """Get platform health (for breakable platforms)"""
        return self.__health

    # Setters
    def set_move_speed(self, speed):
        """Set platform movement speed"""
        self.__move_speed = speed

    def set_move_distance(self, distance):
        """Set platform movement distance"""
        self.__move_distance = distance

    def set_move_axis(self, axis):
        """Set platform movement axis (x or y)"""
        if axis in ["x", "y"]:
            self.__move_axis = axis

    def set_move_direction(self, direction):
        """Set platform movement direction"""
        self.__move_direction = direction


class PlatformManager:
    """Class to manage a collection of platforms"""

    def __init__(self):
        self.__platforms = []

    def add_platform(self, platform):
        """Add a platform to the manager"""
        self.__platforms.append(platform)

    def update(self, dt):
        """Update all platforms"""
        for platform in self.__platforms:
            platform.update(dt)

    def check_collisions(self, hero):
        """Check and resolve collisions between hero and platforms"""
        if hero.is_alive():
            self.__check_vertical_collisions(hero)
            self.__check_horizontal_collisions(hero)

    def __check_vertical_collisions(self, hero):
        """Check for vertical collisions (landing on platforms)"""
        # Create a rect for the hero's feet
        feet_rect = pygame.Rect(
            hero.get_x() + hero.get_width() / 4,
            hero.get_y() + hero.get_height() - 5,
            hero.get_width() / 2,
            10
        )

        # Only check while falling
        if hero.is_falling():
            for platform in self.__platforms:
                if platform.is_broken():
                    continue

                # Skip one-way platforms if hero is moving upward
                if platform.is_one_way_platform() and hero.get_y_velocity() < 0:
                    continue

                # Check if feet collide with platform
                if feet_rect.colliderect(platform.get_rect()):
                    # Land on the platform
                    hero.set_y(platform.get_y() - hero.get_height())
                    hero.land()

                    # If it's a moving platform, attach hero to it
                    if platform.is_moving_platform():
                        if platform.get_move_axis() == "x":
                            hero.set_x(hero.get_x() + platform.get_move_speed() * platform.get_move_direction())

    def __check_horizontal_collisions(self, hero):
        """Check for horizontal collisions with platforms"""
        # Create left and right side collision rects
        left_rect = pygame.Rect(
            hero.get_x(),
            hero.get_y() + 10,
            10,
            hero.get_height() - 20
        )

        right_rect = pygame.Rect(
            hero.get_x() + hero.get_width() - 10,
            hero.get_y() + 10,
            10,
            hero.get_height() - 20
        )

        # Check left side collisions
        for platform in self.__platforms:
            if platform.is_broken() or platform.is_one_way_platform():
                continue

            if left_rect.colliderect(platform.get_rect()):
                # Push hero right
                hero.set_x(platform.get_rect().right)

            if right_rect.colliderect(platform.get_rect()):
                # Push hero left
                hero.set_x(platform.get_rect().left - hero.get_width())

    def get_platforms(self):
        """Get all platforms (return copy to prevent external modification)"""
        return self.__platforms.copy()

    def get_platform_count(self):
        """Get the number of platforms"""
        return len(self.__platforms)

    def clear_platforms(self):
        """Remove all platforms"""
        self.__platforms.clear()


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