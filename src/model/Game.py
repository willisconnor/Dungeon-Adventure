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
from src.utils.SpriteSheetHandler import SpriteManager
from src.model.DungeonEntity import Direction, AnimationState
import random
from src.model.RoomDungeonSystem import DungeonManager, Room, Direction, DoorPosition
from src.model.tiles import *

class HeroType(Enum):
    """available hero types"""
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
        self.screen = screen
        self.width = width
        self.height = height
        self.state = GameState.HERO_SELECT

        #game loop properties
        self.clock = pygame.time.Clock()
        self.running = False

        # Initialize sprite manager
        self.sprite_manager = SpriteManager()

        # Initialize game systems
        self.projectile_manager = ProjectileManager()
        self.platform_manager = PlatformManager()

        #initialize dungeon system
        self.dungeon_manager = None
        self.current_room = None

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
        self.selection_font = pygame.font.Font(None, 48)
        self.description_font = pygame.font.Font(None, 24)

        #tileset

        #debug
        if not self.font:
            print("ERROR! Fonts failed to initialize")

        # Input handling
        self.space_pressed = False
        self.e_pressed = False

        # Level properties
        self.level_width = 2048  # Wider than screen for scrolling
        self.level_height = height

        # Background
        self.background_color = (50, 50, 80)  # Dark blue-ish

        #hero selection
        self.selected_hero_type = None
        self.hero_selection_mode = False
        self.hero_selection_made = False

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

        #load tileset
        tileset_path = "assets/environment/old-dark-castle-interior-tileset.png"
        self.tileset = pygame.image.load(tileset_path).convert_alpha()

    def run(self):
        """main game loop"""
        self.running = True

        while self.running:
            #calc delta time
            dt = self.clock.tick(60)/1000.0 #60 fps, dt in seconds

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



    def _initialize_game(self):
        """Initialize or reset the game state"""
        #get direcotyr where game.py is lcoated
        game_dir = os.path.dirname(os.path.abspath(__file__))
        #go up two levels
        project_root = os.path.dirname(os.path.dirname(game_dir))
        #built the full path to tmx file
        tmx_path = os.path.join(project_root, "assets", "environment", "flat-tileset.tmx")


        # Clear existing objects
        self.heroes.clear()
        self.enemies.clear()
        self.projectile_manager.clear()
        # Clear all sprite groups
        self.all_sprites.empty()
        self.hero_sprites.empty()
        self.enemy_sprites.empty()
        self.projectile_sprites.empty()
        self.platform_sprites.empty()

        #initialize dungeon manager
        self.dungeon_manager = DungeonManager((5,5), tmx_path)
        self.current_room = self.dungeon_manager.get_current_room()

        #only proceed if hero has been selected
        '''if not self.hero_selection_mode:
            return'''

        #create only the selected hero
        if self.current_room:
            start_x = self.current_room.width //4 # center of screen
            #start_y = self.current_room.height - 150
            tiles_high = self.current_room.height//self.current_room.tile_height
            floor_y_pixels = (tiles_high -4) * self.current_room.tile_height
            start_y = floor_y_pixels -140


        if self.selected_hero_type == HeroType.KNIGHT:
            print("Key 1 pressed - selecting KNIGHT") #debug
            hero = Knight(start_x, start_y)
        elif self.selected_hero_type == HeroType.ARCHER:
            hero = Archer(start_x, start_y)
            hero.projectile_manager = self.projectile_manager
        elif self.selected_hero_type == HeroType.CLERIC:
            hero = Cleric(start_x, start_y)
            hero.projectile_manager = self.projectile_manager
        else:
            return  # No hero selected

        # Add heroes to sprite groups
        self.all_sprites.add(hero)
        self.hero_sprites.add(hero)
        self.midground_sprites.add(hero)
        self.damageable_sprites.add(hero)




            # Add enemies to sprite groups
        #for enemy in self.enemies:
            #self.all_sprites.add(enemy)
            #self.enemy_sprites.add(enemy)
            #self.midground_sprites.add(enemy)
            #self.damageable_sprites.add(enemy)

        self.heroes = [hero]
        self.active_hero = hero
        self.current_hero_index = 0

        #create enemies
        #self._spawn_enemies()

        #set the game state
        self.state = GameState.PLAYING


    def _spawn_enemies_for_room(self, room: Room):
        """spawn enemies for a specific room"""
        #clear existing enemies
        for enemy in self.enemies:
            self.all_sprites.remove(enemy)
            self.enemy_sprites.remove(enemy)
            self.midground_sprites.remove(enemy)
            self.damageable_sprites.remove(enemy)
        self.enemies.clear()

        if room.is_boss_room:
            #spawn boss in center of room
            boss = DemonBoss(room.width //2, room.height //2)
            self.enemies.append(boss)
            self.all_sprites.add(boss)
            self.enemy_sprites.add(boss)
            self.midground_sprites.add(boss)
            self.damageable_sprites.add(boss)
        elif not room.is_start_room:
            #spawn 1-3 regular enemies
            num_enemies = random.randint(1,3)
            for i in range(num_enemies):
                x = random.randint(100, room.width - 100)
                y = random.randint(100, room.height - 100)
                #create weaker enemies using demonboss as a palceholder
                enemy = DemonBoss(x,y)
                enemy.health = 50
                enemy.max_health = 50
                enemy.attack_damage = 5
                self.enemies.append(enemy)
                self.all_sprites.add(enemy)
                self.enemy_sprites.add(enemy)
                self.midground_sprites.add(enemy)
                self.damageable_sprites.add(enemy)


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



        # You could add more enemies here based on level design
        # Example: spawn some skeleton enemies when you implement them

    def handle_event(self, event):
        """Handle pygame events"""
        if event.type == pygame.KEYDOWN:
            print(f"Current game state: {self.state}")
            if self.state == GameState.HERO_SELECT:
                # Hero selection
                if event.key == pygame.K_1:
                    print("Key 1 pressed - selecting KNIGHT") #debug
                    self.selected_hero_type = HeroType.KNIGHT
                    self.hero_selection_made = True
                    self._initialize_game()
                    #state is set to playing inside the init game

                elif event.key == pygame.K_2:
                    self.selected_hero_type = HeroType.ARCHER
                    self.hero_selection_made = True
                    self._initialize_game()
                elif event.key == pygame.K_3:
                    self.selected_hero_type = HeroType.CLERIC
                    self.hero_selection_made = True
                    self._initialize_game()
                elif event.key == pygame.K_ESCAPE:
                    self.running = False

            elif self.state == GameState.PLAYING:
                # Game controls (no hero switching)
                if event.key == pygame.K_ESCAPE:
                    self.state = GameState.PAUSED
                elif event.key == pygame.K_SPACE:
                    self.space_pressed = True
                elif event.key == pygame.K_e:
                    self.e_pressed = True

            elif self.state == GameState.PAUSED:
                if event.key == pygame.K_ESCAPE:
                    self.state = GameState.PLAYING
                elif event.key == pygame.K_q:
                    self.running = False  # Quit from pause menu

            elif self.state == GameState.GAME_OVER or self.state == GameState.VICTORY:
                if event.key == pygame.K_SPACE:
                    # Reset for new game
                    self.hero_selection_made = False
                    self.selected_hero_type = None
                    self.state = GameState.HERO_SELECT
                elif event.key == pygame.K_ESCAPE:
                    self.running = False

        elif event.type == pygame.KEYUP:
            if event.key == pygame.K_SPACE:
                self.space_pressed = False

    def update(self, dt, keys):
       """update game state"""
       if self.state == GameState.PLAYING:
           #make sure the dungeon manager exists
           if not self.dungeon_manager:
               return

           #get current room
           self.current_room = self.dungeon_manager.get_current_room()

           #spawn enemies for new room if needed
       if not hasattr(self.current_room, '_enemies_spawned'):
            self.current_room._enemies_spawned = True
            self._spawn_enemies_for_room(self.current_room)

            #update active hero input
            if self.active_hero and self.active_hero.is_alive:
                self.active_hero.handle_input(keys, self.space_pressed)
                self.active_hero.update(dt)

                #check for door interaction with E key
                if self.e_pressed:
                    #try to eneter door
                    if self.dungeon_manager.try_enter_door(self.active_hero.x, self.active_hero.y):
                        #get door we just went thru
                        for door in self.current_room.doors.values():
                            if door.dest_room == self.dungeon_manager.current_room_pos:
                                direction = door.direction
                                break
                        #position hero at opposite side of new room
                        new_room = self.dungeon_manager.get_current_room()
                        if direction == Direction.UP:
                            self.active_hero.x = new_room.width // 2
                            self.active_hero.y = new_room.height - 150
                        elif direction == Direction.DOWN:
                            self.active_hero.x = new_room.width // 2
                            self.active_hero.y = 150
                        elif direction == Direction.LEFT:
                            self.active_hero.x = new_room.width - 150
                            self.active_hero.y = new_room.height // 2
                        elif direction == Direction.RIGHT:
                            self.active_hero.x = 150
                            self.active_hero.y = new_room.height // 2

                        #mark that we need to spawn eenmies for new room
                        new_room._enemies_spawned = False
                    #try to collect pillar
                    if self.dungeon_manager.try_collect_pillar(self.active_hero.x, self.active_hero.y):
                        print(f"Pillar collected! {self.dungeon_manager.pillars_collected}/5")

            # Update all sprites at once
            self.all_sprites.update(dt)

            #handle collisions using sprite groups
            self._handle_collisions()
            # Update all heroes
            #for hero in self.heroes:
             #  hero.update(dt)

            # Check platform collisions for heroes
            #if hasattr(self.hero, 'is_falling'):
               # self.platform_manager.check_collisions(hero)

            # Update enemies
            for enemy in self.enemies:
                if enemy.is_alive:
                    enemy.update(dt)
                    #basic ai
                    if self.active_hero:
                        enemy.move_towards_target(self.active_hero.x, self.active_hero.y, dt)
                        enemy.attack(self.active_hero)

            #Update projectiles
            self.projectile_manager.update(dt)

            # Check projectile collisions
            hero_projectile_hits = self.projectile_manager.check_collisions(self.enemies)
            # later: check enemy hits vs heros

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
            self.e_pressed = False

    def _handle_collisions(self):
        """Handle all collisions using sprite groups"""
        # Hero attacks vs enemies
        if self.active_hero and self.active_hero.is_attacking:
            attack_hitbox = self.active_hero.get_attack_hitbox()
            if attack_hitbox:
                for enemy in self.enemies:
                    if enemy.is_alive and attack_hitbox.colliderect(enemy.hitbox):
                        if enemy not in self.active_hero.hit_targets:
                            damage = self.active_hero.calculate_damage(enemy)
                            if enemy.take_damage(damage):
                                self.active_hero.hit_targets.add(enemy)

        # Projectile collisions
        hero_projectile_hits = self.projectile_manager.check_collisions(self.enemies)

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

    def _update_camera(self):
        """Update camera position to follow active hero"""
        if self.active_hero and self.current_room:
            # Center camera on hero with some boundaries
            target_x = self.active_hero.x - self.width // 2
            #target_y = self.active_hero.y - self.height // 2

            # Smooth camera movement
            self.camera_x += (target_x - self.camera_x) * 0.1
            #self.camera_y += (target_y - self.camera_y) * 0.1

            # Clamp camera to level boundaries
            self.camera_x = max(0, min(self.camera_x, self.current_room.width - self.width))
            #self.camera_y = max(0, min(self.camera_y, self.current_room.height - self.height))
            self.camera_y = 0

    def _check_game_state(self):
        """Check for win/lose conditions"""
        # Check if hero is dead
        if self.active_hero and not self.active_hero.is_alive:
            self.state = GameState.GAME_OVER

        # Check if boss is defeated in boss room
        current_room = self.dungeon_manager.get_current_room()
        if current_room.is_boss_room:
            all_enemies_dead = all(not enemy.is_alive for enemy in self.enemies)
            if all_enemies_dead and self.enemies:
                self.dungeon_manager.defeat_boss()
                if self.dungeon_manager.is_game_won():
                    self.state = GameState.VICTORY

    def draw(self):
        """Draw everything to the screen"""
        print(f"Draw method Called! State: {self.state.name}") #debug
        # Clear screen
        self.screen.fill(self.background_color)

        #test: draw white rectangle
        #pygame.draw.rect(self.screen, (255,255,255), (100,100,200,200))

        if self.state == GameState.HERO_SELECT:
            self._draw_hero_select()
        elif self.state == GameState.MENU:
            self._draw_menu()
        elif self.state == GameState.PLAYING:
            self._draw_game()
            self._draw_ui()
        elif self.state == GameState.PAUSED:
            self._draw_game() #in background
            self._draw_pause_overlay()
        elif self.state == GameState.GAME_OVER:
            self._draw_game_over()
        elif self.state == GameState.VICTORY:
            self._draw_victory()


    def _draw_hero_select(self):
        """Draw hero selection screen"""
        # Background
        self.screen.fill((20, 20, 40)) #make this a cool image mayhaps?

        # Title
        title_text = self.font.render("SELECT YOUR HERO", True, (255, 255, 255))
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
            name_text = self.selection_font.render(hero_info['name'], True, hero_info['color'])
            name_rect = name_text.get_rect(center=(self.width // 2, y))
            self.screen.blit(name_text, name_rect)

            # Stats
            stats_text = self.description_font.render(hero_info['stats'], True, (200, 200, 200))
            stats_rect = stats_text.get_rect(center=(self.width // 2, y + 35))
            self.screen.blit(stats_text, stats_rect)

            # Special
            special_text = self.description_font.render(hero_info['special'], True, (255, 200, 100))
            special_rect = special_text.get_rect(center=(self.width // 2, y + 60))
            self.screen.blit(special_text, special_rect)

            # Description
            desc_text = self.description_font.render(hero_info['description'], True, (150, 150, 150))
            desc_rect = desc_text.get_rect(center=(self.width // 2, y + 85))
            self.screen.blit(desc_text, desc_rect)

        # Instructions
        instruction_text = self.ui_font.render("Press 1, 2, or 3 to select", True, (255, 255, 0))
        instruction_rect = instruction_text.get_rect(center=(self.width // 2, self.height - 40))
        self.screen.blit(instruction_text, instruction_rect)

    #not used?
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
        #tileset = pygame.image.load("assets\environment\old-dark-castle-interior-tileset.png").convert_alpha()
        print("_draw_game called!")

        if not self.current_room:
            print("ERROR! No current room!")
            return
        #draw the current room
        self.current_room.draw(self.screen, self.tileset, (self.camera_x, self.camera_y))

        #draw enemies me muellerie enmieeeeee
        for enemy in self.enemies:
            if enemy.is_alive:
                enemy_rect = pygame.Rect(
                    enemy.x - self.camera_x,
                    enemy.y - self.camera_y,
                    enemy.width,
                    enemy.height
                )
                #making enemies sqaures and not sprites
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

        #draw heroes
        for i, hero in enumerate(self.heroes):
            if hero.is_alive:
                # Get the current sprite based on animation state
                current_sprite = self.sprite_manager.get_sprite(
                    hero.hero_type,
                    hero.animation_state,
                    hero.frame_index
                )
                if current_sprite:
                    # Calculate position
                    screen_x = hero.x - self.camera_x
                    screen_y = hero.y - self.camera_y

                    # Draw sprite at hero position
                    self.screen.blit(current_sprite, (screen_x, screen_y))
                else:
                    # Fallback to rect
                    hero_rect = pygame.Rect(
                        hero.x - self.camera_x,
                        hero.y - self.camera_y,
                        hero.width,
                        hero.height
                    )
                    # Different colors for different heroes
                    color = (50, 50, 200)  # Default blue
                    if isinstance(hero, Knight):
                        color = (150, 150, 200)
                    elif isinstance(hero, Archer):
                        color = (50, 200, 50)
                    elif isinstance(hero, Cleric):
                        color = (200, 50, 200)

                    # Flash if invulnerable
                    if not hero.is_invulnerable or int(hero.invulnerable_timer * 10) % 2:
                        pygame.draw.rect(self.screen, color, hero_rect)

                # Highlight active hero
                if hero == self.active_hero:
                    hero_rect = pygame.Rect(
                        hero.x - self.camera_x,
                        hero.y - self.camera_y,
                        hero.width,
                        hero.height
                    )
                    pygame.draw.rect(self.screen, (255, 255, 0), hero_rect, 3)

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
                if projectile.projectile_type == ProjectileType.ARROW:
                    color = (200, 200, 100)
                else:  # Fireball
                    color = (255, 100, 0)

                pygame.draw.rect(self.screen, color, proj_rect)
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

        #DRAW FLOOR TILED

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
                if projectile.projectile_type == ProjectileType.ARROW:
                    color = (200, 200, 100)
                else:  # Fireball
                    color = (255, 100, 0)

                pygame.draw.rect(self.screen, color, proj_rect)

    def _draw_ui(self):
        """Simplified UI for single hero"""
        if not self.active_hero:
            return

        # Hero info
        hero_name = self.active_hero.__class__.__name__
        name_text = self.ui_font.render(f"{hero_name}", True, (255, 255, 255))
        self.screen.blit(name_text, (10, 10))

        # Health bar
        bar_x = 10
        bar_y = 40
        bar_width = 200
        bar_height = 20

        # Background FLAG
        pygame.draw.rect(self.screen, (60, 60, 60), (bar_x, bar_y, bar_width, bar_height))

        # Health
        if self.active_hero.is_alive:
            health_percent = self.active_hero.health / self.active_hero.max_health
            health_color = (0, 200, 0) if health_percent > 0.5 else (200, 200, 0) if health_percent > 0.25 else (200, 0, 0)
            pygame.draw.rect(self.screen, health_color, (bar_x, bar_y, bar_width * health_percent, bar_height))

        # Border
        pygame.draw.rect(self.screen, (255, 255, 255), (bar_x, bar_y, bar_width, bar_height), 2)

        # Health text
        health_text = self.ui_font.render(f"{self.active_hero.health}/{self.active_hero.max_health}", True, (255, 255, 255))
        self.screen.blit(health_text, (bar_x + bar_width + 10, bar_y))

        # Special cooldown
        if self.active_hero.special_cooldown_remaining > 0:
            cd_text = self.ui_font.render(f"Special (Q): {self.active_hero.special_cooldown_remaining:.1f}s", True, (200, 200, 200))
            self.screen.blit(cd_text, (10, 70))
        else:
            cd_text = self.ui_font.render("Special (Q): Ready!", True, (0, 255, 0))
            self.screen.blit(cd_text, (10, 70))

        #pillar counter
        pillar_text = self.font.render(f"Pillars: {self.dungeon_manager.pillars_collected}/5", True, (255, 255, 0))
        self.screen.blit(pillar_text, (self.width -200, 10))

        #room status
        current_room = self.dungeon_manager.get_current_room()
        if current_room.is_boss_room:
            boss_text = self.font.render("BOSS ROOM", True, (255, 0, 0))
            boss_rect = boss_text.get_rect(center = (self.width //2, 50))
            self.screen.blit(boss_text, boss_rect)

        #check for boss door
        for door in current_room.doors.values():
            if door.dest_room:
                dest_room = self.dungeon_manager.dungeon_grid[door.dest_room[0]][door.dest_room[1]]
                if dest_room and dest_room.is_boss_room:
                    if self.dungeon_manager.pillars_collected <5:
                        lock_text = self.ui_font.render("Boss door locked - Collect all pillars!", True, (255, 100, 100))
                    else:
                        lock_text = self.ui_font.render("Boss door unlocked!", True, (100, 255, 100))
                    lock_rect = lock_text.get_rect(center = (self.width //2, 80))
                    self.screen.blit(lock_text, lock_rect)
                    break

        # Controls reminder (bottom right)
        controls = [
            "A/D - Move",
            "SPACE - Attack",
            "Q - Special",
            "E - Defend"
        ]

        y_offset = self.height - 100
        for control in controls:
            text = self.ui_font.render(control, True, (150, 150, 150))
            text_rect = text.get_rect(right=self.width - 10, top=y_offset)
            self.screen.blit(text, text_rect)
            y_offset += 20

        #debug info - room position
        room_text = self.ui_font.render(f"Room: {current_room.grid_pos}", True, (100,100,100))
        self.screen.blit(room_text, (10, self.height - 30))

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

        retry_text = self.ui_font.render("Press SPACE to Try Again", True, (150, 150, 150))
        retry_rect = retry_text.get_rect(center=(self.width // 2, self.height // 2 + 50))
        self.screen.blit(retry_text, retry_rect)

        quit_text = self.ui_font.render("Press ESC to Quit", True, (150, 150, 150))
        quit_rect = quit_text.get_rect(center=(self.width // 2, self.height // 2 + 80))
        self.screen.blit(quit_text, quit_rect)

    def _draw_victory(self):
        """Draw victory screen"""
        self.screen.fill((20, 50, 20))

        victory_text = self.font.render("VICTORY!", True, (0, 255, 0))
        victory_rect = victory_text.get_rect(center=(self.width // 2, self.height // 2))
        self.screen.blit(victory_text, victory_rect)

        continue_text = self.ui_font.render("Press SPACE for New Game", True, (150, 200, 150))
        continue_rect = continue_text.get_rect(center=(self.width // 2, self.height // 2 + 50))
        self.screen.blit(continue_text, continue_rect)

        quit_text = self.ui_font.render("Press ESC to Quit", True, (150, 200, 150))
        quit_rect = quit_text.get_rect(center=(self.width // 2, self.height // 2 + 80))
        self.screen.blit(quit_text, quit_rect)