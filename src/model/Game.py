"""
Game.py - Main game class that manages the game state
"""
import pygame
from enum import Enum, auto
from src.model.knight import Knight
from src.model.archer import Archer
from src.model.cleric import Cleric
from src.model.DemonBoss import DemonBoss
from src.model.ProjectileManager import ProjectileManager
from src.model.Platform import PlatformManager, Platform
from src.utils.SpriteSheetHandler import SpriteManager
from src.model.DungeonEntity import Direction, AnimationState
import random


class GameState(Enum):
    """Enum for different game states"""
    MENU = auto()
    PLAYING = auto()
    PAUSED = auto()
    GAME_OVER = auto()
    VICTORY = auto()


class Game:
    """Main game class that manages all game systems"""

    def __init__(self, screen, width, height):
        self.screen = screen
        self.width = width
        self.height = height
        self.state = GameState.MENU

        # Initialize sprite manager
        self.sprite_manager = SpriteManager()

        # Initialize game systems
        self.projectile_manager = ProjectileManager()
        self.platform_manager = PlatformManager()

        # Game objects
        self.heroes = []
        self.enemies = []
        self.current_hero_index = 0
        self.active_hero = None

        # Camera/viewport
        self.camera_x = 0
        self.camera_y = 0

        # UI elements
        self.font = pygame.font.Font(None, 36)
        self.ui_font = pygame.font.Font(None, 24)

        # Input handling
        self.space_pressed = False

        # Level properties
        self.level_width = 2048  # Wider than screen for scrolling
        self.level_height = height

        # Background
        self.background_color = (50, 50, 80)  # Dark blue-ish

        # Initialize game
        self._initialize_game()

    def _initialize_game(self):
        """Initialize or reset the game state"""
        # Clear existing objects
        self.heroes.clear()
        self.enemies.clear()
        self.projectile_manager.clear()

        # Create heroes at starting position
        start_x = 100
        start_y = 500

        knight = Knight(start_x, start_y)
        archer = Archer(start_x + 150, start_y)
        cleric = Cleric(start_x + 300, start_y)

        # Set projectile manager for heroes that need it
        archer.projectile_manager = self.projectile_manager
        cleric.projectile_manager = self.projectile_manager

        self.heroes = [knight, archer, cleric]
        self.active_hero = self.heroes[0]

        # Create platforms
        self._create_level_platforms()

        # Create enemies
        self._spawn_enemies()

        # Set game state
        self.state = GameState.PLAYING

    def _create_level_platforms(self):
        """Create platforms for the level"""
        # Clear existing platforms
        self.platform_manager.platforms.clear()

        # Ground platform
        ground = Platform(0, 600, self.level_width, 200)
        self.platform_manager.add_platform(ground)

        # Floating platforms
        self.platform_manager.add_platform(Platform(300, 450, 200, 20))
        self.platform_manager.add_platform(Platform(600, 350, 150, 20))
        self.platform_manager.add_platform(Platform(900, 400, 200, 20))

        # Moving platform
        moving_platform = Platform(400, 300, 100, 20, platform_type="moving")
        moving_platform.move_distance = 150
        moving_platform.move_axis = "x"
        self.platform_manager.add_platform(moving_platform)

        # One-way platform
        one_way = Platform(700, 250, 150, 15, platform_type="one-way")
        self.platform_manager.add_platform(one_way)

    def _spawn_enemies(self):
        """Spawn enemies in the level"""
        # For now, just spawn the demon boss
        # In a full game, you'd load enemy data and spawn various types
        boss = DemonBoss(1200, 400)
        self.enemies.append(boss)

        # You could add more enemies here based on level design
        # Example: spawn some skeleton enemies when you implement them

    def handle_event(self, event):
        """Handle pygame events"""
        if event.type == pygame.KEYDOWN:
            if self.state == GameState.MENU:
                if event.key == pygame.K_SPACE:
                    self._initialize_game()

            elif self.state == GameState.PLAYING:
                # Switch heroes with number keys
                if event.key == pygame.K_1 and len(self.heroes) > 0:
                    self.current_hero_index = 0
                    self.active_hero = self.heroes[0]
                elif event.key == pygame.K_2 and len(self.heroes) > 1:
                    self.current_hero_index = 1
                    self.active_hero = self.heroes[1]
                elif event.key == pygame.K_3 and len(self.heroes) > 2:
                    self.current_hero_index = 2
                    self.active_hero = self.heroes[2]

                # Pause game
                elif event.key == pygame.K_ESCAPE:
                    self.state = GameState.PAUSED

                # Attack
                elif event.key == pygame.K_SPACE:
                    self.space_pressed = True

            elif self.state == GameState.PAUSED:
                if event.key == pygame.K_ESCAPE:
                    self.state = GameState.PLAYING

            elif self.state == GameState.GAME_OVER or self.state == GameState.VICTORY:
                if event.key == pygame.K_SPACE:
                    self.state = GameState.MENU

        elif event.type == pygame.KEYUP:
            if event.key == pygame.K_SPACE:
                self.space_pressed = False

    def update(self, dt, keys):
        """Update game state"""
        if self.state == GameState.PLAYING:
            # Update active hero input
            if self.active_hero and self.active_hero.is_alive:
                self.active_hero.handle_input(keys, self.space_pressed)

            # Update all heroes
            for hero in self.heroes:
                hero.update(dt)

                # Check platform collisions for heroes
                if hasattr(hero, 'is_falling'):  # If using movement extension
                    self.platform_manager.check_collisions(hero)

            # Update enemies
            for enemy in self.enemies:
                enemy.update(dt)

                # Basic AI - move towards nearest hero
                if enemy.is_alive and self.active_hero:
                    enemy.move_towards_target(self.active_hero.x, self.active_hero.y, dt)

                    # Try to attack if in range
                    enemy.attack(self.active_hero)

            # Update projectiles
            self.projectile_manager.update(dt)

            # Check projectile collisions
            hero_projectile_hits = self.projectile_manager.check_collisions(self.enemies)
            # In a full implementation, you'd also check enemy projectiles vs heroes

            # Update platforms
            self.platform_manager.update(dt)

            # Handle hero attacks on enemies
            if self.active_hero and self.active_hero.is_attacking:
                hit_enemies = self.active_hero.attack(self.enemies)

            # Update camera to follow active hero
            self._update_camera()

            # Check win/lose conditions
            self._check_game_state()

        # Reset space pressed state
        self.space_pressed = False

    def _update_camera(self):
        """Update camera position to follow active hero"""
        if self.active_hero:
            # Center camera on hero with some boundaries
            target_x = self.active_hero.x - self.width // 2
            target_y = self.active_hero.y - self.height // 2

            # Smooth camera movement
            self.camera_x += (target_x - self.camera_x) * 0.1
            self.camera_y += (target_y - self.camera_y) * 0.1

            # Clamp camera to level boundaries
            self.camera_x = max(0, min(self.camera_x, self.level_width - self.width))
            self.camera_y = max(0, min(self.camera_y, self.level_height - self.height))

    def _check_game_state(self):
        """Check for win/lose conditions"""
        # Check if all heroes are dead
        all_heroes_dead = all(not hero.is_alive for hero in self.heroes)
        if all_heroes_dead:
            self.state = GameState.GAME_OVER

        # Check if all enemies are dead
        all_enemies_dead = all(not enemy.is_alive for enemy in self.enemies)
        if all_enemies_dead and self.enemies:  # Make sure we had enemies
            self.state = GameState.VICTORY

    def draw(self):
        """Draw everything to the screen"""
        # Clear screen
        self.screen.fill(self.background_color)

        if self.state == GameState.MENU:
            self._draw_menu()

        elif self.state == GameState.PLAYING:
            self._draw_game()
            self._draw_ui()

        elif self.state == GameState.PAUSED:
            self._draw_game()  # Draw game in background
            self._draw_pause_overlay()

        elif self.state == GameState.GAME_OVER:
            self._draw_game_over()

        elif self.state == GameState.VICTORY:
            self._draw_victory()

    def _draw_menu(self):
        """Draw the main menu"""
        title_text = self.font.render("DUNGEON HEROES", True, (255, 255, 255))
        title_rect = title_text.get_rect(center=(self.width // 2, 200))
        self.screen.blit(title_text, title_rect)

        start_text = self.ui_font.render("Press SPACE to Start", True, (200, 200, 200))
        start_rect = start_text.get_rect(center=(self.width // 2, 400))
        self.screen.blit(start_text, start_rect)

        controls_text = [
            "Controls:",
            "A/D - Move Left/Right",
            "SPACE - Attack",
            "Q - Special Ability",
            "E - Defend",
            "1/2/3 - Switch Heroes"
        ]

        y_offset = 500
        for line in controls_text:
            text = self.ui_font.render(line, True, (180, 180, 180))
            text_rect = text.get_rect(center=(self.width // 2, y_offset))
            self.screen.blit(text, text_rect)
            y_offset += 30

    def _draw_game(self):
        """Draw the game world"""
        # Draw platforms
        for platform in self.platform_manager.platforms:
            if not platform.broken:
                # Adjust for camera
                rect = pygame.Rect(
                    platform.rect.x - self.camera_x,
                    platform.rect.y - self.camera_y,
                    platform.rect.width,
                    platform.rect.height
                )

                # Different colors for different platform types
                if platform.is_one_way:
                    color = (100, 100, 200)
                elif platform.is_moving:
                    color = (200, 100, 100)
                elif platform.is_breakable:
                    color = (150, 150, 100)
                else:
                    color = (100, 100, 100)

                pygame.draw.rect(self.screen, color, rect)

        # Draw enemies
        for enemy in self.enemies:
            if enemy.is_alive:
                # Simple rectangle representation for now
                # In a full game, you'd use the sprite manager here
                enemy_rect = pygame.Rect(
                    enemy.x - self.camera_x,
                    enemy.y - self.camera_y,
                    enemy.width,
                    enemy.height
                )
                color = (200, 50, 50) if not enemy.is_invulnerable else (255, 150, 150)
                pygame.draw.rect(self.screen, color, enemy_rect)

                # Draw enemy health bar
                health_percent = enemy.health / enemy.max_health
                bar_width = enemy.width
                bar_height = 5
                bar_x = enemy.x - self.camera_x
                bar_y = enemy.y - self.camera_y - 10

                pygame.draw.rect(self.screen, (100, 0, 0), (bar_x, bar_y, bar_width, bar_height))
                pygame.draw.rect(self.screen, (0, 200, 0), (bar_x, bar_y, bar_width * health_percent, bar_height))

        # Draw heroes
        for i, hero in enumerate(self.heroes):
            if hero.is_alive:
                # Simple rectangle representation
                # In a full game, you'd use the sprite manager here
                hero_rect = pygame.Rect(
                    hero.x - self.camera_x,
                    hero.y - self.camera_y,
                    hero.width,
                    hero.height
                )

                # Different colors for different heroes
                if isinstance(hero, Knight):
                    color = (150, 150, 200)
                elif isinstance(hero, Archer):
                    color = (150, 200, 150)
                else:  # Cleric
                    color = (200, 150, 150)

                # Highlight active hero
                if hero == self.active_hero:
                    pygame.draw.rect(self.screen, (255, 255, 0), hero_rect, 3)

                # Flash if invulnerable
                if not hero.is_invulnerable or int(hero.invulnerable_timer * 10) % 2:
                    pygame.draw.rect(self.screen, color, hero_rect)

                # Draw attack hitbox for debugging
                if hero.is_attacking:
                    attack_hitbox = hero.get_attack_hitbox()
                    if attack_hitbox:
                        debug_rect = pygame.Rect(
                            attack_hitbox.x - self.camera_x,
                            attack_hitbox.y - self.camera_y,
                            attack_hitbox.width,
                            attack_hitbox.height
                        )
                        pygame.draw.rect(self.screen, (255, 255, 0), debug_rect, 1)

        # Draw projectiles
        for projectile in self.projectile_manager.projectiles:
            if projectile.active:
                proj_rect = pygame.Rect(
                    projectile.x - self.camera_x,
                    projectile.y - self.camera_y,
                    projectile.width,
                    projectile.height
                )

                # Different colors for different projectile types
                from src.model.ProjectileManager import ProjectileType
                if projectile.projectile_type == ProjectileType.ARROW:
                    color = (200, 200, 100)
                else:  # Fireball
                    color = (255, 100, 0)

                pygame.draw.rect(self.screen, color, proj_rect)

    def _draw_ui(self):
        """Draw the game UI"""
        # Draw hero health bars and info
        y_offset = 10
        for i, hero in enumerate(self.heroes):
            # Hero name and number
            name = hero.__class__.__name__
            text = self.ui_font.render(f"{i + 1}. {name}", True, (255, 255, 255))
            self.screen.blit(text, (10, y_offset))

            # Health bar
            bar_x = 120
            bar_y = y_offset + 5
            bar_width = 150
            bar_height = 15

            # Background
            pygame.draw.rect(self.screen, (60, 60, 60), (bar_x, bar_y, bar_width, bar_height))

            # Health
            if hero.is_alive:
                health_percent = hero.health / hero.max_health
                health_color = (0, 200, 0) if health_percent > 0.5 else (200, 200, 0) if health_percent > 0.25 else (
                    200, 0, 0)
                pygame.draw.rect(self.screen, health_color, (bar_x, bar_y, bar_width * health_percent, bar_height))

            # Border
            border_color = (255, 255, 0) if hero == self.active_hero else (100, 100, 100)
            pygame.draw.rect(self.screen, border_color, (bar_x, bar_y, bar_width, bar_height), 2)

            # Special ability cooldown
            if hero.special_cooldown_remaining > 0:
                cd_text = self.ui_font.render(f"Q: {hero.special_cooldown_remaining:.1f}s", True, (200, 200, 200))
                self.screen.blit(cd_text, (bar_x + bar_width + 10, y_offset))
            else:
                cd_text = self.ui_font.render("Q: Ready!", True, (0, 255, 0))
                self.screen.blit(cd_text, (bar_x + bar_width + 10, y_offset))

            y_offset += 30

    def _draw_pause_overlay(self):
        """Draw pause screen overlay"""
        # Semi-transparent overlay
        overlay = pygame.Surface((self.width, self.height))
        overlay.set_alpha(128)
        overlay.fill((0, 0, 0))
        self.screen.blit(overlay, (0, 0))

        # Pause text
        pause_text = self.font.render("PAUSED", True, (255, 255, 255))
        pause_rect = pause_text.get_rect(center=(self.width // 2, self.height // 2))
        self.screen.blit(pause_text, pause_rect)

        resume_text = self.ui_font.render("Press ESC to Resume", True, (200, 200, 200))
        resume_rect = resume_text.get_rect(center=(self.width // 2, self.height // 2 + 50))
        self.screen.blit(resume_text, resume_rect)

    def _draw_game_over(self):
        """Draw game over screen"""
        self.screen.fill((20, 20, 20))

        game_over_text = self.font.render("GAME OVER", True, (200, 0, 0))
        game_over_rect = game_over_text.get_rect(center=(self.width // 2, self.height // 2))
        self.screen.blit(game_over_text, game_over_rect)

        retry_text = self.ui_font.render("Press SPACE to Return to Menu", True, (150, 150, 150))
        retry_rect = retry_text.get_rect(center=(self.width // 2, self.height // 2 + 50))
        self.screen.blit(retry_text, retry_rect)

    def _draw_victory(self):
        """Draw victory screen"""
        self.screen.fill((20, 50, 20))

        victory_text = self.font.render("VICTORY!", True, (0, 255, 0))
        victory_rect = victory_text.get_rect(center=(self.width // 2, self.height // 2))
        self.screen.blit(victory_text, victory_rect)

        continue_text = self.ui_font.render("Press SPACE to Return to Menu", True, (150, 200, 150))
        continue_rect = continue_text.get_rect(center=(self.width // 2, self.height // 2 + 50))
        self.screen.blit(continue_text, continue_rect)