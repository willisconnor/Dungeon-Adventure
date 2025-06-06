import pygame
import random
import json
import xml.etree.ElementTree as ET
import os
from enum import Enum
from abc import ABC, abstractmethod
from typing import List, Tuple, Optional, Dict

class Room:
    """Room class - contains platforms, items, and room logic"""
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

