import pygame
import random
import json
import xml.etree.ElementTree as ET
import os
from enum import Enum
from abc import ABC, abstractmethod
from typing import List, Tuple, Optional, Dict

# Initialize Pygame
pygame.init()

# Constants
SCREEN_WIDTH = 1200
SCREEN_HEIGHT = 800
TILE_SIZE = 32
GRAVITY = 0.8
JUMP_FORCE = -15
PLAYER_SPEED = 5

# Colors
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
RED = (255, 0, 0)
GREEN = (0, 255, 0)
BLUE = (0, 0, 255)
YELLOW = (255, 255, 0)
PURPLE = (128, 0, 128)
ORANGE = (255, 165, 0)
CYAN = (0, 255, 255)


class ItemType(Enum):
    HEALING_POTION = "healing"
    VISION_POTION = "vision"
    PIT = "pit"
    PILLAR_ABSTRACTION = "abstraction"
    PILLAR_ENCAPSULATION = "encapsulation"
    PILLAR_INHERITANCE = "inheritance"
    PILLAR_POLYMORPHISM = "polymorphism"
    ENTRANCE = "entrance"
    EXIT = "exit"


class Direction(Enum):
    NORTH = "north"
    SOUTH = "south"
    EAST = "east"
    WEST = "west"


class TileMapLoader:
    """Utility class to load TMX tile maps and extract platform data"""

    @staticmethod
    def load_tmx(file_path: str) -> List[Tuple[int, int]]:
        """Load platform positions from TMX file"""
        platforms = []
        try:
            tree = ET.parse(file_path)
            root = tree.getroot()

            # Get map dimensions
            map_width = int(root.get('width', 0))
            map_height = int(root.get('height', 0))
            tile_width = int(root.get('tilewidth', TILE_SIZE))
            tile_height = int(root.get('tileheight', TILE_SIZE))

            # Find layer with platform data
            for layer in root.findall('layer'):
                data_element = layer.find('data')
                if data_element is not None:
                    # Parse CSV data
                    csv_data = data_element.text.strip().replace('\n', '').replace(' ', '')
                    tile_ids = [int(x) for x in csv_data.split(',') if x]

                    # Convert tile IDs to platform positions
                    for i, tile_id in enumerate(tile_ids):
                        if tile_id > 0:  # Non-zero tile ID means there's a platform
                            x = (i % map_width) * tile_width
                            y = (i // map_width) * tile_height
                            platforms.append((x, y))

        except Exception as e:
            print(f"Error loading TMX file: {e}")
            # Fallback to procedural generation if TMX loading fails
            return TileMapLoader._generate_fallback_platforms()

        return platforms

    @staticmethod
    def _generate_fallback_platforms() -> List[Tuple[int, int]]:
        """Generate fallback platforms if TMX loading fails"""
        platforms = []

        # Generate floor platforms
        for x in range(0, SCREEN_WIDTH * 2, TILE_SIZE):
            if random.random() > 0.2:  # Some gaps in the floor
                platforms.append((x, SCREEN_HEIGHT - TILE_SIZE))

        # Generate floating platforms
        for _ in range(random.randint(5, 12)):
            x = random.randint(0, SCREEN_WIDTH * 2 - TILE_SIZE)
            y = random.randint(TILE_SIZE * 3, SCREEN_HEIGHT - TILE_SIZE * 3)
            # Create platform clusters
            cluster_size = random.randint(1, 4)
            for i in range(cluster_size):
                if x + i * TILE_SIZE < SCREEN_WIDTH * 2:
                    platforms.append((x + i * TILE_SIZE, y))

        return platforms


# MODEL CLASSES

class GameObject(ABC):
    """Abstract base class for all game objects"""

    def __init__(self, x: int, y: int, width: int, height: int):
        self.x = x
        self.y = y
        self.width = width
        self.height = height
        self.rect = pygame.Rect(x, y, width, height)

    @abstractmethod
    def update(self):
        pass

    @abstractmethod
    def render(self, surface: pygame.Surface, camera_x: int = 0):
        pass


class Item(GameObject):
    """Base class for all collectible items"""

    def __init__(self, x: int, y: int, item_type: ItemType, value: int = 0):
        super().__init__(x, y, TILE_SIZE, TILE_SIZE)
        self.item_type = item_type
        self.value = value
        self.collected = False
        self.color = self._get_color()

    def _get_color(self) -> Tuple[int, int, int]:
        color_map = {
            ItemType.HEALING_POTION: GREEN,
            ItemType.VISION_POTION: CYAN,
            ItemType.PIT: BLACK,
            ItemType.PILLAR_ABSTRACTION: RED,
            ItemType.PILLAR_ENCAPSULATION: BLUE,
            ItemType.PILLAR_INHERITANCE: YELLOW,
            ItemType.PILLAR_POLYMORPHISM: PURPLE,
            ItemType.ENTRANCE: WHITE,
            ItemType.EXIT: ORANGE
        }
        return color_map.get(self.item_type, WHITE)

    def update(self):
        pass

    def render(self, surface: pygame.Surface, camera_x: int = 0):
        if not self.collected:
            pygame.draw.rect(surface, self.color,
                             (self.x - camera_x, self.y, self.width, self.height))
            # Add item type indicator
            font = pygame.font.Font(None, 24)
            text = font.render(self.item_type.value[0].upper(), True, WHITE)
            text_rect = text.get_rect(center=(self.x - camera_x + self.width // 2,
                                              self.y + self.height // 2))
            surface.blit(text, text_rect)


class Platform(GameObject):
    """Platform/tile object"""

    def __init__(self, x: int, y: int):
        super().__init__(x, y, TILE_SIZE, TILE_SIZE)
        self.color = (139, 69, 19)  # Brown color

    def update(self):
        pass

    def render(self, surface: pygame.Surface, camera_x: int = 0):
        pygame.draw.rect(surface, self.color,
                         (self.x - camera_x, self.y, self.width, self.height))
        pygame.draw.rect(surface, BLACK,
                         (self.x - camera_x, self.y, self.width, self.height), 2)


class Player(GameObject):
    """Player character"""

    def __init__(self, x: int, y: int):
        super().__init__(x, y, TILE_SIZE, TILE_SIZE)
        self.vel_x = 0
        self.vel_y = 0
        self.on_ground = False
        self.health = 100
        self.max_health = 100
        self.inventory = []
        self.pillars_collected = []
        self.has_vision = False
        self.vision_timer = 0

    def update(self):
        # Handle input
        keys = pygame.key.get_pressed()
        self.vel_x = 0

        if keys[pygame.K_LEFT] or keys[pygame.K_a]:
            self.vel_x = -PLAYER_SPEED
        if keys[pygame.K_RIGHT] or keys[pygame.K_d]:
            self.vel_x = PLAYER_SPEED
        if (keys[pygame.K_SPACE] or keys[pygame.K_UP] or keys[pygame.K_w]) and self.on_ground:
            self.vel_y = JUMP_FORCE
            self.on_ground = False

        # Apply gravity
        if not self.on_ground:
            self.vel_y += GRAVITY

        # Update position
        self.x += self.vel_x
        self.y += self.vel_y

        # Update rect after position change
        self.rect.x = self.x
        self.rect.y = self.y

        # Update vision timer
        if self.vision_timer > 0:
            self.vision_timer -= 1
            if self.vision_timer <= 0:
                self.has_vision = False

    def render(self, surface: pygame.Surface, camera_x: int = 0):
        pygame.draw.rect(surface, BLUE,
                         (self.x - camera_x, self.y, self.width, self.height))
        pygame.draw.rect(surface, WHITE,
                         (self.x - camera_x, self.y, self.width, self.height), 2)

    def collect_item(self, item: Item):
        """Handle item collection"""
        if item.item_type == ItemType.HEALING_POTION:
            self.health = min(self.max_health, self.health + item.value)
        elif item.item_type == ItemType.VISION_POTION:
            self.has_vision = True
            self.vision_timer = 600  # 10 seconds at 60 FPS
        elif item.item_type in [ItemType.PILLAR_ABSTRACTION, ItemType.PILLAR_ENCAPSULATION,
                                ItemType.PILLAR_INHERITANCE, ItemType.PILLAR_POLYMORPHISM]:
            if item.item_type not in self.pillars_collected:
                self.pillars_collected.append(item.item_type)
        elif item.item_type == ItemType.PIT:
            self.health = max(0, self.health - item.value)

        item.collected = True
        self.inventory.append(item)


class Room:
    """Room class with proper encapsulation - contains platforms, items, and room logic"""

    def __init__(self, room_id: int, width: int = SCREEN_WIDTH * 2, height: int = SCREEN_HEIGHT):
        self.__room_id = room_id
        self.__width = width
        self.__height = height
        self.__platforms: List[Platform] = []
        self.__items: List[Item] = []
        self.__doors: Dict[Direction, bool] = {
            Direction.NORTH: False,
            Direction.SOUTH: False,
            Direction.EAST: False,
            Direction.WEST: False
        }
        self.__room_type = None
        self.__background_image = None
        self.__background_color = (50, 50, 100)  # Dark blue background fallback

        # Load background image
        self.__load_background()

        # Generate room content
        self.__generate_room_content()

    def __load_background(self):
        """Load background image from assets folder"""
        try:
            background_path = os.path.join("assets", "background.png")
            if os.path.exists(background_path):
                self.__background_image = pygame.image.load(background_path)
                # Scale background to fit room dimensions
                self.__background_image = pygame.transform.scale(self.__background_image, (self.__width, self.__height))
            else:
                print(f"Background image not found at {background_path}")
        except Exception as e:
            print(f"Error loading background image: {e}")
            self.__background_image = None

    # Private methods for encapsulation
    def __generate_room_content(self):
        """Generate platforms and items for the room"""
        # Generate platforms (basic floor and some floating platforms)
        self.__generate_platforms()

        # Determine room type and generate items
        self.__determine_room_type()
        self.__generate_items()

        # Generate doors
        self.__generate_doors()

    def __generate_platforms(self):
        """Generate platforms for the room using TMX data or fallback"""
        try:
            # Try to load platforms from TMX file
            tmx_path = os.path.join("assets", "platforms.tmx")
            if os.path.exists(tmx_path):
                platform_positions = TileMapLoader.load_tmx(tmx_path)
                for x, y in platform_positions:
                    # Only add platforms within room bounds
                    if x < self.__width and y < self.__height:
                        self.__platforms.append(Platform(x, y))
            else:
                print(f"TMX file not found at {tmx_path}, using fallback generation")
                platform_positions = TileMapLoader._generate_fallback_platforms()
                for x, y in platform_positions:
                    if x < self.__width and y < self.__height:
                        self.__platforms.append(Platform(x, y))
        except Exception as e:
            print(f"Error loading platforms: {e}")
            # Fallback platform generation
            platform_positions = TileMapLoader._generate_fallback_platforms()
            for x, y in platform_positions:
                if x < self.__width and y < self.__height:
                    self.__platforms.append(Platform(x, y))

    def __determine_room_type(self):
        """Determine what type of room this is"""
        # Special rooms (entrance, exit, pillar rooms)
        special_chance = random.random()
        if special_chance < 0.05:  # 5% chance for entrance
            self.__room_type = ItemType.ENTRANCE
        elif special_chance < 0.1:  # 5% chance for exit
            self.__room_type = ItemType.EXIT
        elif special_chance < 0.3:  # 20% chance for pillar room
            pillars = [ItemType.PILLAR_ABSTRACTION, ItemType.PILLAR_ENCAPSULATION,
                       ItemType.PILLAR_INHERITANCE, ItemType.PILLAR_POLYMORPHISM]
            self.__room_type = random.choice(pillars)

    def __generate_items(self):
        """Generate items based on room type and random chance"""
        if self.__room_type == ItemType.ENTRANCE:
            # Entrance room - only entrance marker, nothing else
            x = self.__width // 2
            y = self.__height // 2
            self.__items.append(Item(x, y, ItemType.ENTRANCE))
            return

        if self.__room_type == ItemType.EXIT:
            # Exit room - only exit marker, nothing else
            x = self.__width // 2
            y = self.__height // 2
            self.__items.append(Item(x, y, ItemType.EXIT))
            return

        if self.__room_type in [ItemType.PILLAR_ABSTRACTION, ItemType.PILLAR_ENCAPSULATION,
                                ItemType.PILLAR_INHERITANCE, ItemType.PILLAR_POLYMORPHISM]:
            # Pillar room - only the specific pillar
            x = random.randint(TILE_SIZE, self.__width - TILE_SIZE)
            y = random.randint(TILE_SIZE, self.__height - TILE_SIZE * 2)
            self.__items.append(Item(x, y, self.__room_type))
            return

        # Regular room - 10% chance for each item type
        if random.random() < 0.1:  # Healing potion
            x = random.randint(TILE_SIZE, self.__width - TILE_SIZE)
            y = random.randint(TILE_SIZE, self.__height - TILE_SIZE * 2)
            healing_value = random.randint(5, 15)
            self.__items.append(Item(x, y, ItemType.HEALING_POTION, healing_value))

        if random.random() < 0.1:  # Vision potion
            x = random.randint(TILE_SIZE, self.__width - TILE_SIZE)
            y = random.randint(TILE_SIZE, self.__height - TILE_SIZE * 2)
            self.__items.append(Item(x, y, ItemType.VISION_POTION))

        if random.random() < 0.1:  # Pit
            x = random.randint(TILE_SIZE, self.__width - TILE_SIZE)
            y = self.__height - TILE_SIZE  # Pits are on the ground
            pit_damage = random.randint(1, 20)
            self.__items.append(Item(x, y, ItemType.PIT, pit_damage))

    def __generate_doors(self):
        """Generate doors for the room"""
        # Random chance for each door
        for direction in Direction:
            self.__doors[direction] = random.random() < 0.7  # 70% chance for each door

    # Public interface methods (proper encapsulation)
    def get_room_id(self) -> int:
        return self.__room_id

    def get_platforms(self) -> List[Platform]:
        return self.__platforms.copy()  # Return copy to prevent external modification

    def get_items(self) -> List[Item]:
        return [item for item in self.__items if not item.collected]

    def get_all_items(self) -> List[Item]:
        return self.__items.copy()

    def has_door(self, direction: Direction) -> bool:
        return self.__doors[direction]

    def get_room_type(self) -> Optional[ItemType]:
        return self.__room_type

    def get_dimensions(self) -> Tuple[int, int]:
        return (self.__width, self.__height)

    def update(self):
        """Update room state"""
        for item in self.__items:
            item.update()
        for platform in self.__platforms:
            platform.update()

    def render(self, surface: pygame.Surface, camera_x: int = 0):
        """Render the room"""
        # Fill background
        if self.__background_image:
            # Render tiled background
            bg_width = self.__background_image.get_width()
            bg_height = self.__background_image.get_height()

            # Calculate how many times to tile the background
            start_x = int(camera_x // bg_width) * bg_width
            end_x = start_x + SCREEN_WIDTH + bg_width

            for x in range(start_x, end_x, bg_width):
                for y in range(0, self.__height, bg_height):
                    surface.blit(self.__background_image, (x - camera_x, y))
        else:
            surface.fill(self.__background_color)

        # Render platforms
        for platform in self.__platforms:
            platform.render(surface, camera_x)

        # Render items
        for item in self.__items:
            item.render(surface, camera_x)

        # Render door indicators
        self.__render_doors(surface)

    def __render_doors(self, surface: pygame.Surface):
        """Render door indicators"""
        font = pygame.font.Font(None, 36)

        if self.__doors[Direction.NORTH]:
            text = font.render("↑", True, WHITE)
            surface.blit(text, (self.__width // 2 - 10, 10))

        if self.__doors[Direction.SOUTH]:
            text = font.render("↓", True, WHITE)
            surface.blit(text, (self.__width // 2 - 10, self.__height - 40))

        if self.__doors[Direction.EAST]:
            text = font.render("→", True, WHITE)
            surface.blit(text, (self.__width - 40, self.__height // 2 - 10))

        if self.__doors[Direction.WEST]:
            text = font.render("←", True, WHITE)
            surface.blit(text, (10, self.__height // 2 - 10))

    def check_item_collisions(self, player: Player) -> List[Item]:
        """Check for collisions between player and items"""
        collected_items = []
        for item in self.__items:
            if not item.collected and player.rect.colliderect(item.rect):
                collected_items.append(item)
        return collected_items

    def check_platform_collisions(self, player: Player):
        """Handle platform collisions with improved collision detection"""
        player.on_ground = False

        for platform in self.__platforms:
            if player.rect.colliderect(platform.rect):
                # Calculate overlap
                overlap_x = min(player.rect.right - platform.rect.left,
                                platform.rect.right - player.rect.left)
                overlap_y = min(player.rect.bottom - platform.rect.top,
                                platform.rect.bottom - player.rect.top)

                # Resolve collision based on smallest overlap
                if overlap_x < overlap_y:
                    # Horizontal collision
                    if player.rect.centerx < platform.rect.centerx:
                        # Player is to the left of platform
                        player.rect.right = platform.rect.left
                        player.x = player.rect.x
                    else:
                        # Player is to the right of platform
                        player.rect.left = platform.rect.right
                        player.x = player.rect.x
                else:
                    # Vertical collision
                    if player.rect.centery < platform.rect.centery:
                        # Player is above platform (landing on top)
                        player.rect.bottom = platform.rect.top
                        player.y = player.rect.y
                        player.vel_y = 0
                        player.on_ground = True
                    else:
                        # Player is below platform (hitting from below)
                        player.rect.top = platform.rect.bottom
                        player.y = player.rect.y
                        player.vel_y = 0

    def __str__(self) -> str:
        """String representation of the room"""
        room_content = "Empty"
        if self.__room_type:
            room_content = self.__room_type.value.title()
        elif len(self.__items) > 1:
            room_content = "Multiple Items"
        elif len(self.__items) == 1:
            room_content = self.__items[0].item_type.value.title()

        doors_str = ""
        for direction, has_door in self.__doors.items():
            if has_door:
                doors_str += f"{direction.value[0].upper()} "

        return f"Room {self.__room_id}: {room_content} | Doors: {doors_str.strip()}"


# CONTROLLER CLASS

class GameController:
    """Game controller - handles game logic and coordinates between model and view"""

    def __init__(self):
        self.current_room = Room(1)
        self.player = Player(100, 100)
        self.camera_x = 0
        self.game_over = False
        self.victory = False
        self.room_transition_timer = 0

    def update(self):
        """Update game state"""
        if self.game_over or self.victory:
            return

        # Update player
        old_x = self.player.x
        self.player.update()

        # Update room
        self.current_room.update()

        # Handle collisions
        self.current_room.check_platform_collisions(self.player)

        # Check item collisions
        collected_items = self.current_room.check_item_collisions(self.player)
        for item in collected_items:
            self.player.collect_item(item)

        # Update camera to follow player
        self.camera_x = self.player.x - SCREEN_WIDTH // 2
        self.camera_x = max(0, min(self.camera_x, self.current_room.get_dimensions()[0] - SCREEN_WIDTH))

        # Check for room transitions
        self._check_room_transitions()

        # Check win/lose conditions
        self._check_game_conditions()

        # Keep player in bounds
        room_width, room_height = self.current_room.get_dimensions()
        if self.player.x < 0:
            self.player.x = 0
        elif self.player.x > room_width - self.player.width:
            self.player.x = room_width - self.player.width

        if self.player.y > room_height:
            self.player.health -= 10  # Fall damage
            self.player.y = 100  # Respawn
            self.player.x = 100

    def _check_room_transitions(self):
        """Check if player should transition to a new room"""
        room_width, room_height = self.current_room.get_dimensions()

        # Check boundaries for room transitions
        if (self.player.x <= 0 and self.current_room.has_door(Direction.WEST)) or \
                (self.player.x >= room_width - self.player.width and self.current_room.has_door(Direction.EAST)):
            self._transition_to_new_room()

    def _transition_to_new_room(self):
        """Transition to a new room"""
        new_room_id = self.current_room.get_room_id() + 1
        self.current_room = Room(new_room_id)

        # Reset player position
        if self.player.x <= 0:  # Came from west
            self.player.x = self.current_room.get_dimensions()[0] - 100
        else:  # Came from east
            self.player.x = 100

        self.player.y = 100
        self.camera_x = 0

    def _check_game_conditions(self):
        """Check for win/lose conditions"""
        if self.player.health <= 0:
            self.game_over = True

        # Check if player has all pillars and reached exit
        required_pillars = {ItemType.PILLAR_ABSTRACTION, ItemType.PILLAR_ENCAPSULATION,
                            ItemType.PILLAR_INHERITANCE, ItemType.PILLAR_POLYMORPHISM}
        collected_pillars = set(self.player.pillars_collected)

        if required_pillars.issubset(collected_pillars):
            # Check if player is at exit
            for item in self.current_room.get_items():
                if (item.item_type == ItemType.EXIT and
                        self.player.rect.colliderect(item.rect)):
                    self.victory = True

    def get_game_state(self) -> Dict:
        """Get current game state for the view"""
        return {
            'player': self.player,
            'room': self.current_room,
            'camera_x': self.camera_x,
            'game_over': self.game_over,
            'victory': self.victory
        }


# VIEW CLASS

class GameView:
    """Game view - handles rendering and display"""

    def __init__(self):
        self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
        pygame.display.set_caption("Pillars of OO Platformer")
        self.clock = pygame.time.Clock()
        self.font = pygame.font.Font(None, 36)
        self.small_font = pygame.font.Font(None, 24)

    def render(self, game_state: Dict):
        """Render the current game state"""
        player = game_state['player']
        room = game_state['room']
        camera_x = game_state['camera_x']

        # Clear screen
        self.screen.fill(BLACK)

        # Render room
        room.render(self.screen, camera_x)

        # Render player
        player.render(self.screen, camera_x)

        # Render UI
        self._render_ui(player)

        # Render game over/victory screens
        if game_state['game_over']:
            self._render_game_over()
        elif game_state['victory']:
            self._render_victory()

        pygame.display.flip()

    def _render_ui(self, player: Player):
        """Render user interface elements"""
        # Health bar
        health_width = 200
        health_height = 20
        health_percent = player.health / player.max_health

        pygame.draw.rect(self.screen, RED, (10, 10, health_width, health_height))
        pygame.draw.rect(self.screen, GREEN, (10, 10, health_width * health_percent, health_height))
        pygame.draw.rect(self.screen, WHITE, (10, 10, health_width, health_height), 2)

        health_text = self.small_font.render(f"Health: {player.health}/{player.max_health}", True, WHITE)
        self.screen.blit(health_text, (10, 35))

        # Pillars collected
        pillars_text = self.small_font.render(f"Pillars: {len(player.pillars_collected)}/4", True, WHITE)
        self.screen.blit(pillars_text, (10, 60))

        # List collected pillars
        y_offset = 85
        for i, pillar in enumerate(player.pillars_collected):
            pillar_text = self.small_font.render(f"• {pillar.value.title()}", True, WHITE)
            self.screen.blit(pillar_text, (10, y_offset + i * 20))

        # Vision potion indicator
        if player.has_vision:
            vision_text = self.small_font.render("VISION ACTIVE", True, CYAN)
            self.screen.blit(vision_text, (SCREEN_WIDTH - 150, 10))

        # Instructions
        instructions = [
            "Arrow Keys/WASD: Move",
            "Space/Up: Jump",
            "Collect all 4 Pillars of OO",
            "Find the Exit to win!"
        ]

        for i, instruction in enumerate(instructions):
            text = self.small_font.render(instruction, True, WHITE)
            self.screen.blit(text, (SCREEN_WIDTH - 250, SCREEN_HEIGHT - 100 + i * 20))

    def _render_game_over(self):
        """Render game over screen"""
        overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))
        overlay.set_alpha(128)
        overlay.fill(BLACK)
        self.screen.blit(overlay, (0, 0))

        game_over_text = self.font.render("GAME OVER", True, RED)
        text_rect = game_over_text.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2))
        self.screen.blit(game_over_text, text_rect)

        restart_text = self.small_font.render("Press R to restart or ESC to quit", True, WHITE)
        restart_rect = restart_text.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 + 50))
        self.screen.blit(restart_text, restart_rect)

    def _render_victory(self):
        """Render victory screen"""
        overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))
        overlay.set_alpha(128)
        overlay.fill(BLACK)
        self.screen.blit(overlay, (0, 0))

        victory_text = self.font.render("VICTORY!", True, GREEN)
        text_rect = victory_text.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2))
        self.screen.blit(victory_text, text_rect)

        success_text = self.small_font.render("You collected all Pillars of OO!", True, WHITE)
        success_rect = success_text.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 + 30))
        self.screen.blit(success_text, success_rect)

        restart_text = self.small_font.render("Press R to restart or ESC to quit", True, WHITE)
        restart_rect = restart_text.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 + 60))
        self.screen.blit(restart_text, restart_rect)

    def get_clock(self):
        return self.clock


# MAIN GAME CLASS

class PlatformerGame:
    """Main game class that coordinates MVC components"""

    def __init__(self):
        self.controller = GameController()
        self.view = GameView()
        self.running = True

    def handle_events(self):
        """Handle pygame events"""
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    self.running = False
                elif event.key == pygame.K_r:
                    # Restart game
                    self.controller = GameController()

    def run(self):
        """Main game loop"""
        while self.running:
            self.handle_events()
            self.controller.update()
            game_state = self.controller.get_game_state()
            self.view.render(game_state)
            self.view.get_clock().tick(60)  # 60 FPS

        pygame.quit()


# Run the game
if __name__ == "__main__":
    game = PlatformerGame()
    game.run()