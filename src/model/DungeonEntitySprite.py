"""
Enhanced Game.py with Sprite Groups implementation
This shows how to refactor the Game class to use pygame sprite groups
"""
import pygame
from Game import Game, GameState  # Import the original Game class


# First, we need to modify your entity classes to inherit from pygame.sprite.Sprite
# Here's an example of how to modify the DungeonEntity base class:

class DungeonEntitySprite(pygame.sprite.Sprite):
    """Modified DungeonEntity that inherits from pygame.sprite.Sprite"""

    def __init__(self, x, y, width, height, name, max_health, health, speed, animation_state):
        super().__init__()

        # Original DungeonEntity attributes
        self.x = x
        self.y = y
        self.width = width
        self.height = height
        self.name = name
        self.health = health
        self.max_health = max_health
        self.speed = speed
        # ... other attributes ...

        # Sprite-specific attributes
        self.image = pygame.Surface((width, height))
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y

    def update(self, dt):
        """Update method that pygame sprite groups will call"""
        # Call original update logic
        super().update(dt)

        # Sync rect with position
        self.rect.x = self.x
        self.rect.y = self.y


class GameWithSpriteGroups(Game):
    """Enhanced Game class using pygame sprite groups"""

    def __init__(self, screen, width, height):
        super().__init__(screen, width, height)

        # Create sprite groups
        self.all_sprites = pygame.sprite.Group()
        self.hero_sprites = pygame.sprite.Group()
        self.enemy_sprites = pygame.sprite.Group()
        self.projectile_sprites = pygame.sprite.Group()
        self.platform_sprites = pygame.sprite.Group()

        # Layers for rendering order
        self.background_sprites = pygame.sprite.Group()  # Platforms, background elements
        self.midground_sprites = pygame.sprite.Group()  # Heroes, enemies
        self.foreground_sprites = pygame.sprite.Group()  # Projectiles, effects

        # Collision groups
        self.damageable_sprites = pygame.sprite.Group()  # Everything that can take damage
        self.solid_sprites = pygame.sprite.Group()  # Platforms and walls

    def _initialize_game(self):
        """Override to use sprite groups"""
        # Clear all sprite groups
        self.all_sprites.empty()
        self.hero_sprites.empty()
        self.enemy_sprites.empty()
        self.projectile_sprites.empty()
        self.platform_sprites.empty()

        # Call parent initialization
        super()._initialize_game()

        # Add heroes to sprite groups
        for hero in self.heroes:
            self.all_sprites.add(hero)
            self.hero_sprites.add(hero)
            self.midground_sprites.add(hero)
            self.damageable_sprites.add(hero)

        # Add enemies to sprite groups
        for enemy in self.enemies:
            self.all_sprites.add(enemy)
            self.enemy_sprites.add(enemy)
            self.midground_sprites.add(enemy)
            self.damageable_sprites.add(enemy)

    def update(self, dt, keys):
        """Update using sprite groups"""
        if self.state == GameState.PLAYING:
            # Update active hero input
            if self.active_hero and self.active_hero.is_alive:
                self.active_hero.handle_input(keys, self.space_pressed)

            # Update all sprites at once
            self.all_sprites.update(dt)

            # Handle collisions using sprite groups
            self._handle_collisions()

            # Update camera
            self._update_camera()

            # Check win/lose conditions
            self._check_game_state()

        self.space_pressed = False

    def _handle_collisions(self):
        """Handle all collisions using sprite groups"""
        # Hero attacks vs enemies
        for hero in self.hero_sprites:
            if hero.is_attacking:
                attack_hitbox = hero.get_attack_hitbox()
                if attack_hitbox:
                    # Check collision with all enemies
                    for enemy in self.enemy_sprites:
                        if enemy.is_alive and attack_hitbox.colliderect(enemy.hitbox):
                            if enemy not in hero.hit_targets:
                                damage = hero.calculate_damage(enemy)
                                if enemy.take_damage(damage):
                                    hero.hit_targets.add(enemy)

        # Projectile collisions
        for projectile in self.projectile_sprites:
            if projectile.active:
                # Determine which group to check based on projectile owner
                if projectile.owner in self.hero_sprites:
                    targets = self.enemy_sprites
                else:
                    targets = self.hero_sprites

                # Use sprite collision detection
                hit_list = pygame.sprite.spritecollide(
                    projectile, targets, False,
                    collided=lambda p, t: p.hitbox.colliderect(t.hitbox) and t.is_alive
                )

                for target in hit_list:
                    if target not in projectile.hit_targets:
                        if target.take_damage(projectile.damage):
                            projectile.hit_targets.add(target)
                            if projectile.projectile_type == ProjectileType.ARROW:
                                projectile.active = False
                                break

        # Platform collisions for heroes
        for hero in self.hero_sprites:
            if hasattr(hero, 'is_falling') and hero.is_falling:
                # Check platform collisions
                platform_hits = pygame.sprite.spritecollide(
                    hero, self.platform_sprites, False,
                    collided=lambda h, p: h.rect.bottom >= p.rect.top and h.rect.bottom <= p.rect.top + 20
                )

                for platform in platform_hits:
                    if not platform.broken:
                        hero.y = platform.rect.top - hero.height
                        hero.land()

                        # Move with moving platforms
                        if platform.is_moving and platform.move_axis == "x":
                            hero.x += platform.move_speed * platform.move_direction

    def draw(self):
        """Draw using sprite groups with camera offset"""
        self.screen.fill(self.background_color)

        if self.state == GameState.MENU:
            self._draw_menu()

        elif self.state == GameState.PLAYING:
            # Create a temporary group for camera-adjusted drawing
            visible_sprites = pygame.sprite.Group()

            # Draw layers in order
            for layer in [self.background_sprites, self.midground_sprites, self.foreground_sprites]:
                for sprite in layer:
                    # Check if sprite is visible on screen
                    if (sprite.rect.right > self.camera_x and
                            sprite.rect.left < self.camera_x + self.width and
                            sprite.rect.bottom > self.camera_y and
                            sprite.rect.top < self.camera_y + self.height):
                        # Draw with camera offset
                        self.screen.blit(
                            sprite.image,
                            (sprite.rect.x - self.camera_x, sprite.rect.y - self.camera_y)
                        )

            self._draw_ui()

        elif self.state == GameState.PAUSED:
            self._draw_game()
            self._draw_pause_overlay()

        elif self.state == GameState.GAME_OVER:
            self._draw_game_over()

        elif self.state == GameState.VICTORY:
            self._draw_victory()


# Custom sprite group for handling camera offsets
class CameraGroup(pygame.sprite.Group):
    """Custom sprite group that handles camera offset when drawing"""

    def __init__(self, camera_x=0, camera_y=0):
        super().__init__()
        self.camera_x = camera_x
        self.camera_y = camera_y
        self.screen_width = 0
        self.screen_height = 0

    def set_camera(self, x, y):
        """Update camera position"""
        self.camera_x = x
        self.camera_y = y

    def draw(self, surface):
        """Draw all sprites with camera offset"""
        for sprite in self.sprites():
            # Calculate screen position
            screen_x = sprite.rect.x - self.camera_x
            screen_y = sprite.rect.y - self.camera_y

            # Only draw if visible on screen
            if (-sprite.rect.width < screen_x < surface.get_width() and
                    -sprite.rect.height < screen_y < surface.get_height()):
                surface.blit(sprite.image, (screen_x, screen_y))


# Example modifications to your entity classes to work with sprite groups:

class HeroSprite(pygame.sprite.Sprite):
    """Wrapper to make Hero classes work with sprite groups"""

    def __init__(self, hero):
        super().__init__()
        self.hero = hero  # Reference to the actual hero object

        # Create sprite image (placeholder - replace with actual sprite loading)
        self.image = pygame.Surface((hero.width, hero.height), pygame.SRCALPHA)
        self.rect = self.image.get_rect()
        self.rect.x = hero.x
        self.rect.y = hero.y

        # Sync attributes
        self._sync_attributes()

    def _sync_attributes(self):
        """Sync sprite attributes with hero attributes"""
        # Pass through important attributes
        self.x = self.hero.x
        self.y = self.hero.y
        self.is_alive = self.hero.is_alive
        self.is_attacking = self.hero.is_attacking
        self.hitbox = self.hero.hitbox
        self.hit_targets = self.hero.hit_targets

    def update(self, dt):
        """Update the hero and sync sprite position"""
        self.hero.update(dt)
        self.rect.x = self.hero.x
        self.rect.y = self.hero.y
        self._sync_attributes()

        # Update sprite image based on hero state
        self._update_image()

    def _update_image(self):
        """Update sprite image based on hero animation state"""
        # This is where you'd load the actual sprite from your sprite manager
        # For now, just change color based on state
        if not self.hero.is_alive:
            self.image.fill((100, 100, 100))
        elif self.hero.is_invulnerable:
            # Flash effect
            if int(self.hero.invulnerable_timer * 10) % 2:
                self.image.set_alpha(128)
            else:
                self.image.set_alpha(255)
        else:
            self.image.set_alpha(255)

            # Different colors for different hero types
            if self.hero.hero_type == "knight":
                color = (150, 150, 200)
            elif self.hero.hero_type == "archer":
                color = (150, 200, 150)
            else:  # cleric
                color = (200, 150, 150)

            self.image.fill(color)

    # Delegate method calls to the hero object
    def __getattr__(self, name):
        """Delegate attribute access to the hero object"""
        return getattr(self.hero, name)


# Benefits of using Sprite Groups:

"""
1. COLLISION DETECTION:
   - pygame.sprite.spritecollide() is optimized and faster than manual collision checking
   - pygame.sprite.groupcollide() can check collisions between entire groups
   - Support for custom collision detection functions

2. BATCH OPERATIONS:
   - Update all sprites at once with group.update()
   - Draw all sprites at once with group.draw()
   - Clear/remove sprites easily with group.empty() or sprite.kill()

3. ORGANIZATION:
   - Separate sprites into logical groups (heroes, enemies, projectiles)
   - Layer groups for proper draw order
   - Easy to iterate over specific types of objects

4. PERFORMANCE:
   - Dirty sprite optimization with pygame.sprite.DirtySprite
   - Spatial hashing for large numbers of sprites
   - Built-in culling for off-screen sprites

5. BUILT-IN FEATURES:
   - Sprite.kill() removes from all groups
   - Group.sprites() returns list of all sprites
   - Group.has() checks if sprite is in group
"""


# Example usage in your game loop:
def example_game_loop():
    # Initialize
    game = GameWithSpriteGroups(screen, width, height)

    # In update:
    game.all_sprites.update(dt)  # Updates everything at once

    # Collision detection examples:
    # Check if any hero collides with any enemy
    collisions = pygame.sprite.groupcollide(
        game.hero_sprites,
        game.enemy_sprites,
        False,  # Don't remove heroes
        False  # Don't remove enemies
    )

    # Check if specific sprite hits any in a group
    hits = pygame.sprite.spritecollide(
        game.active_hero,
        game.enemy_sprites,
        False  # Don't remove enemies
    )

    # Custom collision using masks for pixel-perfect collision
    hits = pygame.sprite.spritecollide(
        projectile,
        game.enemy_sprites,
        False,
        pygame.sprite.collide_mask  # Pixel-perfect collision
    )


# Advanced sprite group features:

class LayeredSpriteGroup(pygame.sprite.LayeredUpdates):
    """Example of using layered sprites for proper draw order"""

    def __init__(self):
        super().__init__()
        self.layers = {
            'background': 0,
            'platforms': 1,
            'items': 2,
            'enemies': 3,
            'heroes': 4,
            'projectiles': 5,
            'ui': 6
        }

    def add(self, sprite, layer_name='enemies'):
        """Add sprite to specific layer"""
        layer = self.layers.get(layer_name, 3)
        super().add(sprite, layer=layer)


# Refactored ProjectileManager using sprite groups:
class ProjectileManagerWithSprites(pygame.sprite.Group):
    """Projectile manager that inherits from sprite.Group"""

    def __init__(self):
        super().__init__()

    def add_projectile(self, projectile):
        """Add a projectile to the group"""
        # Convert projectile to sprite if needed
        if not isinstance(projectile, pygame.sprite.Sprite):
            projectile = ProjectileSprite(projectile)
        self.add(projectile)

    def check_collisions(self, target_group):
        """Check collisions between projectiles and targets"""
        hit_dict = {}

        for projectile in self.sprites():
            if projectile.active:
                hits = pygame.sprite.spritecollide(
                    projectile,
                    target_group,
                    False,
                    collided=lambda p, t: p.hitbox.colliderect(t.hitbox) and t.is_alive
                )

                if hits:
                    hit_dict[projectile] = hits

                    # Handle hit logic
                    for target in hits:
                        if target not in projectile.hit_targets:
                            target.take_damage(projectile.damage)
                            projectile.hit_targets.add(target)

                            # Deactivate arrow after hit
                            if projectile.projectile_type == ProjectileType.ARROW:
                                projectile.kill()  # Remove from all groups
                                break

        return hit_dict