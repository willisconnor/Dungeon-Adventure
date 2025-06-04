import pygame
import random
import os
from src.model.Dungeon import Dungeon #We need to name the dungeon generation class
from src.model.Room import Room



class DungeonAdventure:
    def __init__(self):
        # Initialize pygame components
        pygame.init()
        self.__screen_width = 800
        self.__screen_height = 600
        self.__screen = pygame.display.set_mode((self.__screen_width, self.__screen_height))
        pygame.display.set_caption("Dungeon Adventure")
        self.__clock = pygame.time.Clock()

        # Create game elements
        self.__dungeon = Dungeon()
        self.__adventurer = Adventurer("Player")
        self.__rooms = self.__create_rooms()
        self.__current_room_id = 0

        # Game state
        self.__game_active = False
        self.__debug_mode = False

    def __create_rooms(self, num_rooms=5):
        """Create multiple interconnected rooms for the dungeon"""
        rooms = []

        # Create rooms with random connections
        for i in range(num_rooms):
            # Position rooms in a somewhat logical layout
            row = i // 2  # Simple grid arrangement
            col = i % 2
            new_room = Room(row, col)

            # Set up doors between rooms
            if i > 0:  # Skip for the first room
                # Connect to at least one previous room
                prev_room_idx = random.randint(0, i - 1)

                # Determine direction based on relative position
                if row > rooms[prev_room_idx].get_row():
                    # Current room is below previous room
                    new_room.set_north_door(True)
                    rooms[prev_room_idx].set_south_door(True)
                elif row < rooms[prev_room_idx].get_row():
                    # Current room is above previous room
                    new_room.set_south_door(True)
                    rooms[prev_room_idx].set_north_door(True)
                elif col > rooms[prev_room_idx].get_column():
                    # Current room is to the right of previous room
                    new_room.set_west_door(True)
                    rooms[prev_room_idx].set_east_door(True)
                else:
                    # Current room is to the left of previous room
                    new_room.set_east_door(True)
                    rooms[prev_room_idx].set_west_door(True)

            # Add random loot to some rooms
            if random.random() < 0.7:  # 70% chance for loot
                new_room.set_has_loot(True)
                new_room.set_possible_loot(["Health Potion", "Gold", "Weapon"])

            rooms.append(new_room)

        return rooms

    def start_game(self) -> bool:
        """Start the game and enter the main game loop"""
        self.__game_active = True
        self.__game_loop()
        return self.__game_active

    def end_game(self) -> bool:
        """End the game"""
        self.__game_active = False
        return self.__game_active

    def print_current_room(self) -> None:
        """Display information about the current room"""
        if 0 <= self.__current_room_id < len(self.__rooms):
            current_room = self.__rooms[self.__current_room_id]
            print(f"Current Room: {self.__current_room_id}")
            print(f"Doors: N={current_room.has_north_door()}, E={current_room.has_east_door()}, "
                  f"S={current_room.has_south_door()}, W={current_room.has_west_door()}")
            if current_room.has_loot():
                print(f"Loot available: {', '.join(current_room.get_possible_loot())}")

    def move_to_room(self, direction):
        """Move to an adjacent room if a door exists in that direction"""
        current_room = self.__rooms[self.__current_room_id]

        # Check if door exists in the requested direction
        if direction == "north" and current_room.has_north_door():
            # Find room to the north
            for i, room in enumerate(self.__rooms):
                if room.get_row() == current_room.get_row() - 1 and room.get_column() == current_room.get_column():
                    self.__current_room_id = i
                    return True
        elif direction == "south" and current_room.has_south_door():
            # Find room to the south
            for i, room in enumerate(self.__rooms):
                if room.get_row() == current_room.get_row() + 1 and room.get_column() == current_room.get_column():
                    self.__current_room_id = i
                    return True
        elif direction == "east" and current_room.has_east_door():
            # Find room to the east
            for i, room in enumerate(self.__rooms):
                if room.get_row() == current_room.get_row() and room.get_column() == current_room.get_column() + 1:
                    self.__current_room_id = i
                    return True
        elif direction == "west" and current_room.has_west_door():
            # Find room to the west
            for i, room in enumerate(self.__rooms):
                if room.get_row() == current_room.get_row() and room.get_column() == current_room.get_column() - 1:
                    self.__current_room_id = i
                    return True

        return False  # No valid move made

    def __game_loop(self) -> None:
        """Main game loop"""
        while self.__game_active:
            # Handle events
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.__game_active = False
                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE:
                        self.__game_active = False
                    # Room navigation with arrow keys
                    elif event.key == pygame.K_UP:
                        self.move_to_room("north")
                    elif event.key == pygame.K_DOWN:
                        self.move_to_room("south")
                    elif event.key == pygame.K_LEFT:
                        self.move_to_room("west")
                    elif event.key == pygame.K_RIGHT:
                        self.move_to_room("east")
                    # Toggle debug mode
                    elif event.key == pygame.K_d:
                        self.__debug_mode = not self.__debug_mode

            # Update game state
            self.__update()

            # Render
            self.__render()

            # Cap the frame rate
            self.__clock.tick(60)

    def __update(self):
        """Update game state"""
        # Update current room
        current_room = self.__rooms[self.__current_room_id]

        # Handle adventurer updates if needed

    def __render(self):
        """Render the game"""
        # Clear the screen
        self.__screen.fill((0, 0, 0))

        # Render the current room
        current_room = self.__rooms[self.__current_room_id]
        current_room.render(self.__screen)

        # Render the adventurer
        # self.__adventurer.render(self.__screen)

        # Debug information
        if self.__debug_mode:
            self.__render_debug_info()

        # Update the display
        pygame.display.flip()

    def __render_debug_info(self):
        """Render debug information"""
        font = pygame.font.Font(None, 24)
        current_room = self.__rooms[self.__current_room_id]

        # Room information
        room_info = f"Room: {self.__current_room_id} ({current_room.get_row()}, {current_room.get_column()})"
        debug_text = font.render(room_info, True, (255, 255, 255))
        self.__screen.blit(debug_text, (10, 10))

        # Door information
        door_info = f"Doors: N={current_room.has_north_door()}, E={current_room.has_east_door()}, S={current_room.has_south_door()}, W={current_room.has_west_door()}"
        debug_text = font.render(door_info, True, (255, 255, 255))
        self.__screen.blit(debug_text, (10, 40))

        # Loot information
        if current_room.has_loot():
            loot_info = f"Loot: {', '.join(current_room.get_possible_loot())}"
            debug_text = font.render(loot_info, True, (255, 255, 0))
            self.__screen.blit(debug_text, (10, 70))

    # Public getters and limited setters for external access
    def get_screen_dimensions(self):
        """Get screen dimensions as (width, height)"""
        return (self.__screen_width, self.__screen_height)

    def get_current_room_id(self):
        """Get current room ID"""
        return self.__current_room_id

    def get_current_room(self):
        """Get current room object"""
        return self.__rooms[self.__current_room_id]

    def is_debug_mode(self):
        """Check if debug mode is enabled"""
        return self.__debug_mode

    def toggle_debug_mode(self):
        """Toggle debug mode"""
        self.__debug_mode = not self.__debug_mode
        return self.__debug_mode

    def __str__(self) -> str:
        return "DungeonAdventure Game"
