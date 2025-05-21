import pygame
import os
import sqlite3


class SpriteSheet:
    """Class to handle loading and splitting spritesheets into individual sprites"""

    def __init__(self, filename):
        """Initialize the spritesheet

        Args:
            filename: The path to the spritesheet image file
        """
        # Load the spritesheet image
        try:
            self.sheet = pygame.image.load(filename).convert_alpha()
        except pygame.error as e:
            print(f"Unable to load spritesheet image: {filename}")
            raise SystemExit(e)

        # Get the dimensions of the spritesheet
        self.sheet_width = self.sheet.get_width()
        self.sheet_height = self.sheet.get_height()

        # Calculate how many sprites fit in each dimension
        self.cols = self.sheet_width // 128
        self.rows = self.sheet_height // 128

        # Create a list to store all sprites
        self.sprites = []

        # Extract all 128x128 sprites from the sheet
        self._extract_sprites()

    def _extract_sprites(self):
        """Extract all 128x128 sprites from the spritesheet"""
        for row in range(self.rows):
            for col in range(self.cols):
                # Calculate the position of the sprite in the sheet
                x = col * 128
                y = row * 128

                # Create a new surface for the sprite
                sprite = pygame.Surface((128, 128), pygame.SRCALPHA)

                # Copy the sprite from the sheet to the new surface
                sprite.blit(self.sheet, (0, 0), (x, y, 128, 128))

                # Add the sprite to our list
                self.sprites.append(sprite)

    def get_sprite(self, index):
        """Get a specific sprite by index

        Args:
            index: The index of the sprite to retrieve

        Returns:
            A pygame Surface containing the requested sprite
        """
        if 0 <= index < len(self.sprites):
            return self.sprites[index]
        else:
            print(f"Sprite index {index} out of range")
            return None

    def get_all_sprites(self):
        """Get all sprites as a list

        Returns:
            A list of all sprites from the spritesheet
        """
        return self.sprites

    def save_sprites(self, directory, base_name="sprite"):
        """Save all sprites as individual PNG files

        Args:
            directory: Directory where sprites will be saved
            base_name: Base name for sprite files
        """
        # Create directory if it doesn't exist
        os.makedirs(directory, exist_ok=True)

        # Save each sprite as an individual file
        for i, sprite in enumerate(self.sprites):
            filename = os.path.join(directory, f"{base_name}_{i}.png")
            pygame.image.save(sprite, filename)

        print(f"Saved {len(self.sprites)} sprites to {directory}")


class SpriteManager:
    """Class to manage loading and caching sprites from the database"""

    def __init__(self):
        self.sprite_sheets = {}  # Cache for loaded spritesheets
        self.sprites = {}  # Cache for individual sprites

    def get_sprite_sheet(self, hero_type, animation_state):
        """Get a spritesheet for a specific hero and animation state

        Args:
            hero_type: The type of hero (knight, archer, cleric)
            animation_state: The animation state to load

        Returns:
            A SpriteSheet object
        """
        key = f"{hero_type}_{animation_state}"

        # Return cached spritesheet if available
        if key in self.sprite_sheets:
            return self.sprite_sheets[key]

        # Get path from database
        path = self._get_sprite_path_from_db(hero_type, animation_state)

        # Load new spritesheet
        sprite_sheet = SpriteSheet(path)
        self.sprite_sheets[key] = sprite_sheet

        return sprite_sheet

    def get_sprite(self, hero_type, animation_state, frame_index):
        """Get a specific sprite frame

        Args:
            hero_type: The type of hero (knight, archer, cleric)
            animation_state: The animation state
            frame_index: The frame index to retrieve

        Returns:
            A pygame Surface containing the requested sprite
        """
        sprite_key = f"{hero_type}_{animation_state}_{frame_index}"

        # Return cached sprite if available
        if sprite_key in self.sprites:
            return self.sprites[sprite_key]

        # Get the spritesheet and extract the sprite
        sprite_sheet = self.get_sprite_sheet(hero_type, animation_state)
        sprite = sprite_sheet.get_sprite(frame_index)

        # Cache the sprite
        self.sprites[sprite_key] = sprite

        return sprite

    def _get_sprite_path_from_db(self, hero_type, animation_state):
        """Get the sprite path from the database

        Args:
            hero_type: The type of hero
            animation_state: The animation state

        Returns:
            The path to the spritesheet
        """
        conn = sqlite3.connect('game_data.db')
        c = conn.cursor()

        c.execute('''
                  SELECT sprite_path
                  FROM hero_sprites
                  WHERE hero_type = ?
                    AND animation_state = ?
                  ''', (hero_type, animation_state.value))

        result = c.fetchone()
        conn.close()

        if result:
            return result[0]
        else:
            # Default path if not found in database
            return f"assets/sprites/{hero_type}/{animation_state.name.lower()}.png"