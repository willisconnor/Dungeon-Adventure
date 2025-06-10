"""
Game.py - Main game class that manages the game state
"""
import pygame
import os
from enum import Enum, auto
from src.model.knight import Knight
from src.model.archer import Archer
from src.model.cleric import Cleric
from src.model.DemonBoss import DemonBoss
from src.model.ProjectileManager import ProjectileManager, ProjectileType
from src.model.Platform import PlatformManager, Platform
from src.utils.RoomTransitionManager import RoomTransitionManager, DoorInteractionManager
from src.utils.SpriteSheetHandler import SpriteManager
from src.model.DungeonEntity import Direction, AnimationState
from src.model.RoomDungeonSystem import DungeonManager, Room, Direction
from src.utils.RoomTransitionManager import RoomTransitionManager, DoorInteractionManager, TransitionType
import random

class HeroType(Enum):
    """Available hero types"""
    KNIGHT = "knight"
    ARCHER = "archer"
    CLERIC = "cleric"

class GameState(Enum):
    """Enum for different game states"""
    MENU = auto()
    PLAYING = auto()
    PAUSED = auto()
    GAME_OVER = auto()
    VICTORY = auto()
    HERO_SELECT = auto()

class Game:
    """Main game class that manages all game systems"""

    def __init__(self, screen, width, height):
        # Public attributes needed by other components
        self.screen = screen
        self.width = width
        self.height = height
        self.state = GameState.PLAYING  # Changed from HERO_SELECT to PLAYING
        self.running = False

        # Sprite groups needed for collision detection and rendering
        self.all_sprites = pygame.sprite.Group()
        self.hero_sprites = pygame.sprite.Group()
        self.enemy_sprites = pygame.sprite.Group()
        self.projectile_sprites = pygame.sprite.Group()
        self.platform_sprites = pygame.sprite.Group()
        self.background_sprites = pygame.sprite.Group()
        self.midground_sprites = pygame.sprite.Group()
        self.foreground_sprites = pygame.sprite.Group()
        self.damageable_sprites = pygame.sprite.Group()
        self.solid_sprites = pygame.sprite.Group()

        # Game managers needed by other components
        self.sprite_manager = SpriteManager()
        self.projectile_manager = ProjectileManager()
        self.platform_manager = PlatformManager()
        self._transition_manager = RoomTransitionManager(self.width, self.height)
        self._door_manager = DoorInteractionManager()

        #Room transition state
        self._pending_door = None
        self._transition_in_progress = False

        self._floor_csv_path = "assets/levels/flat-tileset.csv"
        self._tileset_path = "assets/environment/old-dark-castle-interior-tileset.png"

        # Private implementation details
        self._clock = pygame.time.Clock()
        self._heroes = {}
        self._enemies = []
        self._active_hero = None
        self._camera_x = 0
        self._camera_y = 0
        self._selected_hero_type = None
        self._hero_selection_made = False
        self._space_pressed = False

        self._dungeon_manager = None
        self._current_room = None

        # Private UI elements
        self._font = pygame.font.Font(None, 36)
        self._ui_font = pygame.font.Font(None, 24)
        self._selection_font = pygame.font.Font(None, 48)
        self._description_font = pygame.font.Font(None, 24)
        self._background_color = (50, 50, 80)

        # Load assets
        #self._tileset = self._load_tileset()

    def _load_tileset(self):
        """Load the game tileset"""
        tileset_path = os.path.join("assets", "environment", "old-dark-castle-interior-tileset.png")
        return pygame.image.load(tileset_path).convert_alpha()

    @property
    def active_hero(self):
        """Get the currently active hero"""
        return self._active_hero

    @property
    def current_room(self):
        """Get the current dungeon room"""
        return self._current_room

    @property
    def heroes(self):
        """Get dictionary of heroes (read-only)"""
        return self._heroes.copy()

    def set_game_state(self, new_state):
        """Safely change game state"""
        if not isinstance(new_state, GameState):
            raise ValueError("Invalid game state")
        self.state = new_state

    def select_hero(self, hero_type):
        """Select a hero type"""
        if not isinstance(hero_type, HeroType):
            raise ValueError("Invalid hero type")
        self._selected_hero_type = hero_type
        self._hero_selection_made = True
        self.set_game_state(GameState.PLAYING)
        self._initialize_game()

    def _create_hero(self, hero_type: HeroType, x: int, y: int):
        """Create hero with validation"""
        if not isinstance(hero_type, HeroType):
            raise ValueError("Invalid hero type")
        if not isinstance(x, (int, float)) or not isinstance(y, (int, float)):
            raise ValueError("Invalid position coordinates")

        hero = None
        if hero_type == HeroType.KNIGHT:
            hero = Knight(x, y)
        elif hero_type == HeroType.ARCHER:
            hero = Archer(x, y)
            hero.projectile_manager = self.projectile_manager
        elif hero_type == HeroType.CLERIC:
            hero = Cleric(x, y)
            hero.projectile_manager = self.projectile_manager

        if hero:
            self._initialize_hero(hero)
        return hero

    def _initialize_hero(self, hero):
        """Initialize hero with proper sprite groups"""
        self.all_sprites.add(hero)
        self.hero_sprites.add(hero)
        self.midground_sprites.add(hero)
        self.damageable_sprites.add(hero)

    def _initialize_game(self):
        """Initialize or reset the game state"""
        self.cleanup()
        self._initialize_dungeon()
        
        if self._current_room:
            start_x, start_y = self._dungeon_manager.get_player_spawn_position_for_current_room()

            hero = self._create_hero(self._selected_hero_type, start_x, start_y)
            if hero:
                self._heroes[self._selected_hero_type] = hero
                self._active_hero = hero

    def _initialize_dungeon(self):
        """Initialize dungeon with validation"""
        if not self._selected_hero_type:
            raise ValueError("Hero must be selected before initializing dungeon")


        self._dungeon_manager = DungeonManager((3,3), "assets/levels/flat-tileset.csv","assets/environment/old-dark-castle-interior-tileset.png")

        self._current_room = self._dungeon_manager.get_current_room()
        
        if not self._current_room:
            raise RuntimeError("Failed to initialize dungeon room")

        self._setup_door_requirements()

    def _setup_door_requirements(self):
        """setup door lock requirements for boss room"""
        for row in range(self._dungeon_manager.get_dungeon_width()): #assuming 3x3 dingeon size
            for col in range(self._dungeon_manager.get_dungeon_height()):
                pass

    def cleanup(self):
        """Cleanup game resources properly"""
        self._heroes.clear()
        self._enemies.clear()
        self.all_sprites.empty()
        self.hero_sprites.empty()
        self.enemy_sprites.empty()
        self.projectile_sprites.empty()
        self.platform_sprites.empty()
        self.background_sprites.empty()
        self.midground_sprites.empty()
        self.foreground_sprites.empty()
        self.damageable_sprites.empty()
        self.solid_sprites.empty()

    def handle_event(self, event):
        """Handle events with validation"""
        if not event:
            return
            
        if event.type == pygame.QUIT:
            self.running = False
            return
            
        if event.type == pygame.KEYDOWN:
            if self.state == GameState.HERO_SELECT:
                self._handle_hero_select_input(event.key)
            elif self.state == GameState.PLAYING:
                self._handle_playing_input(event.key)
            elif self.state == GameState.PAUSED:
                self._handle_paused_input(event.key)
            elif self.state in (GameState.GAME_OVER, GameState.VICTORY):
                self._handle_end_state_input(event.key)
        elif event.type == pygame.KEYUP:
            if event.key == pygame.K_SPACE:
                self._space_pressed = False

    def _handle_hero_select_input(self, key):
        """Handle input during hero selection"""
        if key == pygame.K_1:
            self.select_hero(HeroType.KNIGHT)
        elif key == pygame.K_2:
            self.select_hero(HeroType.ARCHER)
        elif key == pygame.K_3:
            self.select_hero(HeroType.CLERIC)
        elif key == pygame.K_ESCAPE:
            self.running = False

    def _handle_playing_input(self, key):
        """Handle input during gameplay"""
        if key == pygame.K_ESCAPE:
            self.set_game_state(GameState.PAUSED)
        elif key == pygame.K_SPACE:
            self._space_pressed = True

    def _handle_paused_input(self, key):
        """Handle input while game is paused"""
        if key == pygame.K_ESCAPE:
            self.set_game_state(GameState.PLAYING)
        elif key == pygame.K_q:
            self.running = False

    def _handle_end_state_input(self, key):
        """Handle input in end game states"""
        if key == pygame.K_SPACE:
            self._reset_game()
        elif key == pygame.K_ESCAPE:
            self.running = False

    def _reset_game(self):
        """Reset the game to initial state"""
        self._hero_selection_made = False
        self._selected_hero_type = None
        self._active_hero = None
        self.cleanup()
        self.set_game_state(GameState.HERO_SELECT)

    def update(self, dt, keys):
        """Update game state"""
        if self.state != GameState.PLAYING:
            return

        self._transition_manager.update(dt)

        #enforce room bounds
        self._enforce_room_bounds()

        #only process input and movement when not transitioning
        if not self._transition_manager.is_transitioning:
            if self._active_hero and self._active_hero.is_alive:

                #store previous position for door colission detection
                prev_x = self._active_hero.x
                prev_y = self._active_hero.y

                #handle hero input
                self._active_hero.handle_input(keys, self._space_pressed)

                #check for door traversal
                self._check_door_traversal(prev_x, prev_y)


            self.all_sprites.update(dt)
            self._handle_collisions()
            self._update_game_objects(dt)
            self._update_camera()
            self._check_game_state()

    def _check_door_traversal(self, prev_x: int, prev_y: int):
        """Check if hero has moved into a door and handle traversal"""
        if not self._current_room or not self._active_hero:
            return

        # Update door interactions first (this handles the UI prompts)
        self._dungeon_manager.update_current_room_interactions(
            self._active_hero.x, self._active_hero.y,
            self._active_hero.width, self._active_hero.height
        )

        # Check for walk-through doors (LEFT/RIGHT) - automatic entry
        if self._dungeon_manager.try_enter_walkthrough_door(
                self._active_hero.x, self._active_hero.y
        ):
            self._start_room_transition(None)
            return

        # Check for interactive doors (UP/DOWN) with E key press
        keys = pygame.key.get_pressed()
        if keys[pygame.K_e]:  # Press E to interact
            if self._dungeon_manager.try_enter_interactive_door(
                    self._active_hero.x, self._active_hero.y, True
            ):
                self._start_room_transition(None)

    def _start_room_transition(self, door):
        """Start a room transition through the given door"""
        if self._transition_manager.is_transitioning:
            return  # Already transitioning

        # Store door for use in transition callback
        self._pending_door = door

        # Start fade transition
        self._transition_manager.start_transition(
            transition_type=TransitionType.FADE,
            duration=0.8,  # 0.8 seconds total
            callback=self._complete_room_transition
        )

    def _complete_room_transition(self):
        """Called at the midpoint of room transition to actually change rooms"""
        # The room transition was already handled by the dungeon manager
        # Just update the current room reference
        self._current_room = self._dungeon_manager.get_current_room()

        # Reposition hero in the new room
        self._reposition_hero_after_door_traversal()

        # Clear any room-specific enemies/items if needed
        self._handle_room_change()

        # Clear pending door
        self._pending_door = None

    def _reposition_hero_after_door_traversal(self):
        """Reposition hero after entering a door using dungeon manager"""
        if not self._active_hero or not self._current_room:
            return

        # Get the proper spawn position from dungeon manager
        spawn_x, spawn_y = self._dungeon_manager.get_player_spawn_position_for_current_room(
            self._active_hero.width,
            self._active_hero.height
        )

        self._active_hero.x = spawn_x
        self._active_hero.y = spawn_y
    def _handle_room_change(self):
        """Handle any room-specific changes when entering a new room"""
        # Clear projectiles from previous room
        self.projectile_manager.projectiles.clear()

        # Spawn enemies for new room if needed
        self._spawn_room_enemies()

        # Handle any room-specific items or events
        if self._current_room.is_boss_room():
            self._handle_boss_room_entry()

    def _spawn_room_enemies(self):
        """Spawn enemies appropriate for the current room"""
        if not self._current_room:
            return

        # Clear existing enemies
        self._enemies.clear()
        self.enemy_sprites.empty()

        # Example enemy spawning logic
        if self._current_room.is_boss_room():
            # Spawn boss
            boss = DemonBoss(self._current_room.width // 2, self._current_room.floor_y - 100)
            self._enemies.append(boss)
            self.enemy_sprites.add(boss)
            self.all_sprites.add(boss)
        elif not self._current_room.is_start_room():
            # Spawn regular enemies
            import random
            num_enemies = random.randint(1, 3)
            for i in range(num_enemies):
                # Use your monster factory here
                enemy_x = random.randint(100, self._current_room.width - 100)
                enemy_y = self._current_room.floor_y - 60
                # Create enemy using your existing system
                # enemy = create_random_enemy(enemy_x, enemy_y)
                # self._enemies.append(enemy)

    def _show_door_locked_message(self, room_pos, direction):
        """Show a message when a door is locked"""
        message = self._door_manager.get_door_requirement_message(room_pos, direction)
        if message:
            print(f"Door locked: {message}")  # Replace with your UI system
            # You could also show this in your game's UI

    def _handle_boss_room_entry(self):
        """Handle special logic when entering boss room"""
        print("Entered boss chamber!")
        # Add dramatic music, special effects, etc.

    def _update_game_objects(self, dt):
        """Update all game objects"""
        for hero in self._heroes.values():
            hero.update(dt)

        for enemy in self._enemies:
            if enemy.is_alive and self._active_hero:
                enemy.update(dt)
                enemy.move_towards_target(self._active_hero.x, self._active_hero.y, dt)
                enemy.attack(self._active_hero)

        self.projectile_manager.update(dt)
        self.platform_manager.update(dt)

    def _update_camera(self):
        """Update camera position to follow active hero with room bounds"""
        if not self._active_hero or not self._current_room:
            return

        target_x = self._active_hero.x - self.width // 2
        target_y = self._active_hero.y - self.height // 2

        # Smooth camera following
        new_x = self._camera_x + (target_x - self._camera_x) * 0.1
        new_y = self._camera_y + (target_y - self._camera_y) * 0.1

        # Constrain camera to room bounds
        max_x = max(0, self._current_room.width - self.width)
        max_y = max(0, self._current_room.height - self.height)

        self._camera_x = max(0, min(new_x, max_x))
        self._camera_y = max(0, min(new_y, max_y))

    def _set_camera_position(self, x, y):
        """Safely set camera position within bounds"""
        if not self._current_room:
            return
            
        self._camera_x = max(0, min(x, self._current_room.width - self.width))
        self._camera_y = max(0, min(y, self._current_room.height - self.height))

    def _handle_hero_floor_collision(self):
        """Ensure heroes stay on the floor"""
        if not self._current_room:
            return

        floor_y = self._current_room.floor_y

        for hero in self._heroes.values():
            if hero.get_is_alive():
                # Keep hero above floor
                if hero.get_y() + hero.height > floor_y:
                    hero.y = floor_y - hero.height
                    # Reset vertical velocity if hero has physics
                    if hasattr(hero, 'velocity_y'):
                        hero.velocity_y = 0

    def _handle_collisions(self):
        """Handle all collisions"""
        self._handle_hero_enemy_collisions()
        self._handle_projectile_collisions()
        self._handle_platform_collisions()
        self._handle_hero_floor_collision()

    def _handle_hero_enemy_collisions(self):
        """Handle hero and enemy collisions"""
        for hero in self.hero_sprites:
            if not hero.is_alive or not hero.is_attacking:
                continue
                
            attack_hitbox = hero.get_attack_hitbox()
            if not attack_hitbox:
                continue
                
            for enemy in self.enemy_sprites:
                if not enemy.is_alive or enemy in hero.hit_targets:
                    continue
                    
                if hasattr(enemy, 'hitbox') and attack_hitbox.colliderect(enemy.hitbox):
                    damage = hero.calculate_damage(enemy)
                    if enemy.take_damage(damage):
                        hero.hit_targets.add(enemy)

    def _handle_projectile_collisions(self):
        """Handle projectile collisions"""
        self.projectile_manager.check_collisions(self._enemies)

    def _handle_platform_collisions(self):
        """Handle platform collisions"""
        for hero in self.hero_sprites:
            self.platform_manager.check_collisions(hero)

    def _check_game_state(self):
        """Check for win/lose conditions"""
        if all(not hero.is_alive for hero in self._heroes.values()):
            self.set_game_state(GameState.GAME_OVER)
        elif self._enemies and all(not enemy.is_alive for enemy in self._enemies):
            self.set_game_state(GameState.VICTORY)

    def __del__(self):
        """Ensure proper cleanup when game object is destroyed"""
        self.cleanup()

    # The rest of the drawing methods remain unchanged as they mainly deal with UI
    # and don't need additional encapsulation
    def run(self):
        """main game loop"""
        self.running = True

        while self.running:
            #calc delta time
            dt = self._clock.tick(60)/1000.0 #60 fps, dt in seconds

            #handle events
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.running = False
                else:
                    self.handle_event(event)

            #update game state
            if self.state == GameState.PLAYING:
                keys = pygame.key.get_pressed()
                self.update(dt, keys)

            #draw it all
            self.draw()

            #update display
            pygame.display.flip()

    def draw(self):
        """Draw everything to the screen"""
        # Clear screen
        self.screen.fill(self._background_color)

        if self.state == GameState.MENU:
            self._draw_menu()
        elif self.state == GameState.PLAYING:
            # Create a temporary group for camera-adjusted drawing

            self._draw_game_world()
            self._draw_ui()
            self._transition_manager.draw_transition(self.screen)

        elif self.state == GameState.PAUSED:
            self._draw_game_world()  # Draw game in background
            self._draw_pause_overlay()

        elif self.state == GameState.GAME_OVER:
            self._draw_game_over()

        elif self.state == GameState.VICTORY:
            self._draw_victory()

    def _draw_game_world(self):
        """Draw game world"""
        if self._current_room:
            self._current_room.draw(self.screen, (self._camera_x, self._camera_y))

        self._draw_enemies()
        self._draw_heroes()
        self._draw_projectiles()

    def _draw_platforms(self):
        """Draw platforms with camera offset"""
        for platform in self.platform_manager.platforms:
            if not platform.broken:
                rect = pygame.Rect(
                    platform.rect.x - self._camera_x,
                    platform.rect.y - self._camera_y,
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

    def _draw_enemies(self):
        """Draw enemies with camera offset"""
        for enemy in self._enemies:
            if enemy.is_alive:
                # Draw enemy body
                enemy_rect = pygame.Rect(
                    enemy.x - self._camera_x,
                    enemy.y - self._camera_y,
                    enemy.width,
                    enemy.height
                )
                color = (200, 50, 50) if not enemy.is_invulnerable else (255, 150, 150)
                pygame.draw.rect(self.screen, color, enemy_rect)

                # Draw health bar
                health_percent = enemy.health / enemy.max_health
                bar_width = enemy.width
                bar_height = 5
                bar_x = enemy.x - self._camera_x
                bar_y = enemy.y - self._camera_y - 10

                pygame.draw.rect(self.screen, (100, 0, 0), (bar_x, bar_y, bar_width, bar_height))
                pygame.draw.rect(self.screen, (0, 200, 0), (bar_x, bar_y, bar_width * health_percent, bar_height))

    def _draw_heroes(self):
        """Draw heroes with camera offset"""
        for hero in self._heroes.values():
            if hero.get_is_alive():
                # Calculate screen position
                screen_x = hero.get_x() - self._camera_x
                screen_y = hero.get_y() - self._camera_y

                # Draw sprite if available
                current_sprite = hero.get_current_sprite()
                if current_sprite:
                    self.screen.blit(current_sprite, (screen_x, screen_y))
                else:
                    # Fallback: colored rectangle
                    hero_rect = pygame.Rect(screen_x, screen_y, hero.width, hero.height)
                    hero_type = hero.get_hero_type()

                    if hero_type == "knight":
                        color = (100, 100, 200)
                    elif hero_type == "archer":
                        color = (100, 200, 100)
                    elif hero_type == "cleric":
                        color = (200, 100, 100)
                    else:
                        color = (150, 150, 150)

                    pygame.draw.rect(self.screen, color, hero_rect)

                # Highlight active hero
                if hero == self._active_hero:
                    highlight_rect = pygame.Rect(screen_x, screen_y, hero.width, hero.height)
                    pygame.draw.rect(self.screen, (255, 255, 0), highlight_rect, 3)

                # Draw attack hitbox for debugging
                if hero.is_attacking:
                    attack_hitbox = hero.get_attack_hitbox()
                    if attack_hitbox:
                        debug_rect = pygame.Rect(
                            attack_hitbox.x - self._camera_x,
                            attack_hitbox.y - self._camera_y,
                            attack_hitbox.width,
                            attack_hitbox.height
                        )
                        pygame.draw.rect(self.screen, (255, 255, 0), debug_rect, 1)

    def _draw_projectiles(self):
        """Draw projectiles with camera offset"""
        for projectile in self.projectile_manager.projectiles:
            if projectile.active:
                proj_rect = pygame.Rect(
                    projectile.x - self._camera_x,
                    projectile.y - self._camera_y,
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

    def _draw_room_objects(self):
        """Draw room-specific objects like pillars, chests, etc."""
        if not self._current_room:
            return

        # Draw pillars if present (example from your original room system)
        # You'd need to adapt this to your pillar system
        pass

    def _draw_hero_select(self):
        """Draw hero selection screen"""
        # Background
        self.screen.fill((20, 20, 40))

        # Title
        title_text = self._font.render("SELECT YOUR HERO", True, (255, 255, 255))
        title_rect = title_text.get_rect(center=(self.width // 2, 80))
        self.screen.blit(title_text, title_rect)

        # Hero options
        hero_data = [
            {
                'name': '1. KNIGHT',
                'stats': 'Health: 150 | Damage: 10 | Speed: 6',
                'special': 'Special: Shield Bash',
                'description': 'Tank with high defense',
                'color': (150, 150, 200),
                'y_pos': 200
            },
            {
                'name': '2. ARCHER',
                'stats': 'Health: 100 | Damage: 8 | Speed: 8',
                'special': 'Special: Powerful Shot',
                'description': 'Ranged attacker',
                'color': (150, 200, 150),
                'y_pos': 320
            },
            {
                'name': '3. CLERIC',
                'stats': 'Health: 120 | Damage: 7 | Speed: 7',
                'special': 'Special: Heal + Fireball',
                'description': 'Support with magic',
                'color': (200, 150, 150),
                'y_pos': 440
            }
        ]

        # Draw each hero option
        for hero_info in hero_data:
            y = hero_info['y_pos']

            # Hero name
            name_text = self._selection_font.render(hero_info['name'], True, hero_info['color'])
            name_rect = name_text.get_rect(center=(self.width // 2, y))
            self.screen.blit(name_text, name_rect)

            # Stats
            stats_text = self._description_font.render(hero_info['stats'], True, (200, 200, 200))
            stats_rect = stats_text.get_rect(center=(self.width // 2, y + 35))
            self.screen.blit(stats_text, stats_rect)

            # Special
            special_text = self._description_font.render(hero_info['special'], True, (255, 200, 100))
            special_rect = special_text.get_rect(center=(self.width // 2, y + 60))
            self.screen.blit(special_text, special_rect)

            # Description
            desc_text = self._description_font.render(hero_info['description'], True, (150, 150, 150))
            desc_rect = desc_text.get_rect(center=(self.width // 2, y + 85))
            self.screen.blit(desc_text, desc_rect)

        # Instructions
        instruction_text = self._ui_font.render("Press 1, 2, or 3 to select", True, (255, 255, 0))
        instruction_rect = instruction_text.get_rect(center=(self.width // 2, self.height - 40))
        self.screen.blit(instruction_text, instruction_rect)

    #not used?
    def _draw_menu(self):
        """Draw the main menu"""
        title_text = self._font.render("DUNGEON HEROES", True, (255, 255, 255))
        title_rect = title_text.get_rect(center=(self.width // 2, 200))
        self.screen.blit(title_text, title_rect)

        start_text = self._ui_font.render("Press SPACE to Start", True, (200, 200, 200))
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
            text = self._ui_font.render(line, True, (180, 180, 180))
            text_rect = text.get_rect(center=(self.width // 2, y_offset))
            self.screen.blit(text, text_rect)
            y_offset += 30

        """def _draw_game(self):
        Draw the game world
        if self._current_room:
            self._current_room.draw(self.screen, (self._camera_x, self._camera_y))"""

        # Draw platforms
        for platform in self.platform_manager.platforms:
            if not platform.broken:
                # Adjust for camera
                rect = pygame.Rect(
                    platform.rect.x - self._camera_x,
                    platform.rect.y - self._camera_y,
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

        #DRAW FLOOR TILED

        # Draw enemies
        for enemy in self._enemies:
            if enemy.is_alive:
                # Simple rectangle representation for now
                # In a full game, you'd use the sprite manager here
                enemy_rect = pygame.Rect(
                    enemy.x - self._camera_x,
                    enemy.y - self._camera_y,
                    enemy.width,
                    enemy.height
                )
                color = (200, 50, 50) if not enemy.is_invulnerable else (255, 150, 150)
                pygame.draw.rect(self.screen, color, enemy_rect)

                # Draw enemy health bar
                health_percent = enemy.health / enemy.max_health
                bar_width = enemy.width
                bar_height = 5
                bar_x = enemy.x - self._camera_x
                bar_y = enemy.y - self._camera_y - 10

                pygame.draw.rect(self.screen, (100, 0, 0), (bar_x, bar_y, bar_width, bar_height))
                pygame.draw.rect(self.screen, (0, 200, 0), (bar_x, bar_y, bar_width * health_percent, bar_height))

        # Draw heroes, stopped here
        for hero in self._heroes.values():
            if hero.get_is_alive():  # Use getter method
                # Create hero rect for positioning
                hero_rect = pygame.Rect(
                    hero.get_x() - self._camera_x,  # Use getter
                    hero.get_y() - self._camera_y,  # Use getter
                    hero.width,
                    hero.height
                )

                # Use the hero's current sprite
                current_sprite = hero.get_current_sprite()
                if current_sprite:
                    screen_x = hero.get_x() - self._camera_x
                    screen_y = hero.get_y() - self._camera_y
                    self.screen.blit(current_sprite, (screen_x, screen_y))
                else:
                    # Fallback: draw colored rectangle based on hero type
                    hero_type = hero.get_hero_type()
                    if hero_type == "knight":
                        color = (100, 100, 200)  # Blue for knight
                    elif hero_type == "archer":
                        color = (100, 200, 100)  # Green for archer
                    elif hero_type == "cleric":
                        color = (200, 100, 100)  # Red for cleric
                    else:
                        color = (150, 150, 150)  # Gray for default

                    pygame.draw.rect(self.screen, color, hero_rect)



                # Highlight active hero
                if hero == self._active_hero:
                    pygame.draw.rect(self.screen, (255, 255, 0), hero_rect, 3)

                # Flash if invulnerable
                if not hero.is_invulnerable or int(hero.invulnerable_timer * 10) % 2:
                    # Only draw the rectangle if we didn't draw a sprite
                    if not current_sprite:
                        pass  # Rectangle already drawn above

                # Draw attack hitbox for debugging
                if hero.is_attacking:
                    attack_hitbox = hero.get_attack_hitbox()
                    if attack_hitbox:
                        debug_rect = pygame.Rect(
                            attack_hitbox.x - self._camera_x,
                            attack_hitbox.y - self._camera_y,
                            attack_hitbox.width,
                            attack_hitbox.height
                        )
                        pygame.draw.rect(self.screen, (255, 255, 0), debug_rect, 1)

        # Draw projectiles
        for projectile in self.projectile_manager.projectiles:
            if projectile.active:
                proj_rect = pygame.Rect(
                    projectile.x - self._camera_x,
                    projectile.y - self._camera_y,
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
        """Simplified UI for single hero"""
        if not self._active_hero:
            return

        # Hero info
        hero_name = self._active_hero.__class__.__name__
        name_text = self._ui_font.render(f"{hero_name}", True, (255, 255, 255))
        self.screen.blit(name_text, (10, 10))

        # Health bar
        bar_x = 10
        bar_y = 40
        bar_width = 200
        bar_height = 20

        # Background
        pygame.draw.rect(self.screen, (60, 60, 60), (bar_x, bar_y, bar_width, bar_height))

        # Health
        if self._active_hero.is_alive:
            health_percent = self._active_hero.health / self._active_hero.max_health
            health_color = (0, 200, 0) if health_percent > 0.5 else (200, 200, 0) if health_percent > 0.25 else (200, 0, 0)
            pygame.draw.rect(self.screen, health_color, (bar_x, bar_y, bar_width * health_percent, bar_height))

        # Border
        pygame.draw.rect(self.screen, (255, 255, 255), (bar_x, bar_y, bar_width, bar_height), 2)

        # Health text
        health_text = self._ui_font.render(f"{self._active_hero.health}/{self._active_hero.max_health}", True, (255, 255, 255))
        self.screen.blit(health_text, (bar_x + bar_width + 10, bar_y))

        # Special cooldown
        if self._active_hero.special_cooldown_remaining > 0:
            cd_text = self._ui_font.render(f"Special (Q): {self._active_hero.special_cooldown_remaining:.1f}s", True, (200, 200, 200))
            self.screen.blit(cd_text, (10, 70))
        else:
            cd_text = self._ui_font.render("Special (Q): Ready!", True, (0, 255, 0))
            self.screen.blit(cd_text, (10, 70))

        # Controls reminder (bottom right)
        controls = [
            "A/D - Move",
            "SPACE - Attack",
            "Q - Special",
            "E - Defend"
        ]

        y_offset = self.height - 100
        for control in controls:
            text = self._ui_font.render(control, True, (150, 150, 150))
            text_rect = text.get_rect(right=self.width - 10, top=y_offset)
            self.screen.blit(text, text_rect)
            y_offset += 20

        # Display room position
        if self._dungeon_manager:
            room_pos = self._dungeon_manager.get_current_room_position()
            pos_text = self._ui_font.render(f"Room: ({room_pos[0]}, {room_pos[1]})", True, (255, 255, 255))
            self.screen.blit(pos_text, (10, self.height - 30))

    def _draw_pause_overlay(self):
        """Draw pause screen overlay"""
        # Semi-transparent overlay
        overlay = pygame.Surface((self.width, self.height))
        overlay.set_alpha(128)
        overlay.fill((0, 0, 0))
        self.screen.blit(overlay, (0, 0))

        # Pause text
        pause_text = self._font.render("PAUSED", True, (255, 255, 255))
        pause_rect = pause_text.get_rect(center=(self.width // 2, self.height // 2))
        self.screen.blit(pause_text, pause_rect)

        resume_text = self._ui_font.render("Press ESC to Resume", True, (200, 200, 200))
        resume_rect = resume_text.get_rect(center=(self.width // 2, self.height // 2 + 50))
        self.screen.blit(resume_text, resume_rect)

    def _draw_game_over(self):
        """Draw game over screen"""
        self.screen.fill((20, 20, 20))

        game_over_text = self._font.render("GAME OVER", True, (200, 0, 0))
        game_over_rect = game_over_text.get_rect(center=(self.width // 2, self.height // 2))
        self.screen.blit(game_over_text, game_over_rect)

        retry_text = self._ui_font.render("Press SPACE to Try Again", True, (150, 150, 150))
        retry_rect = retry_text.get_rect(center=(self.width // 2, self.height // 2 + 50))
        self.screen.blit(retry_text, retry_rect)

        quit_text = self._ui_font.render("Press ESC to Quit", True, (150, 150, 150))
        quit_rect = quit_text.get_rect(center=(self.width // 2, self.height // 2 + 80))
        self.screen.blit(quit_text, quit_rect)

    def _draw_victory(self):
        """Draw victory screen"""
        self.screen.fill((20, 50, 20))

        victory_text = self._font.render("VICTORY!", True, (0, 255, 0))
        victory_rect = victory_text.get_rect(center=(self.width // 2, self.height // 2))
        self.screen.blit(victory_text, victory_rect)

        continue_text = self._ui_font.render("Press SPACE for New Game", True, (150, 200, 150))
        continue_rect = continue_text.get_rect(center=(self.width // 2, self.height // 2 + 50))
        self.screen.blit(continue_text, continue_rect)

        quit_text = self._ui_font.render("Press ESC to Quit", True, (150, 200, 150))
        quit_rect = quit_text.get_rect(center=(self.width // 2, self.height // 2 + 80))
        self.screen.blit(quit_text, quit_rect)

    #ADD PILLAR COLLECTION
    def _check_pillar_collection(self):
        """Check if hero collects pillars in current room"""
        if not self._current_room or not self._active_hero:
            return

        # This is pseudocode
        # if self._current_room.try_collect_pillar(self._active_hero.x, self._active_hero.y):
        #     self._door_manager.add_to_inventory("pillar")
        #     print("Pillar collected!")

    # ADDITIONAL HELPER METHODS

    def unlock_boss_doors(self):
        """Unlock boss room doors when requirements are met"""
        # Remove door requirements for boss rooms
        pass

    def get_transition_progress(self) -> float:
        """Get current transition progress for UI effects"""
        return self._transition_manager.transition_progress

    def is_transitioning(self) -> bool:
        """Check if currently transitioning between rooms"""
        return self._transition_manager.is_transitioning

    def _enforce_room_bounds(self):
        """Keep hero within room boundaries"""
        if not self._active_hero or not self._current_room:
            return

        # Left boundary
        if self._active_hero.x < 0:
            self._active_hero.x = 0

        # Right boundary
        if self._active_hero.x + self._active_hero.width > self._current_room.width:
            self._active_hero.x = self._current_room.width - self._active_hero.width

        # Floor boundary
        if self._active_hero.y + self._active_hero.height > self._current_room.floor_y:
            self._active_hero.y = self._current_room.floor_y - self._active_hero.height