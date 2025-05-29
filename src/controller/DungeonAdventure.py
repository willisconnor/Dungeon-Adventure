import pygame
import random
import os
from src.model.Adventurer import Adventurer
from src.View.Dungeon import Dungeon
from src.View.Room import Room


class DungeonAdventure:
    def __init__(self):
        # Initialize pygame components
        pygame.init()
        self.screen_width = 800
        self.screen_height = 600
        self.screen = pygame.display.set_mode((self.screen_width, self.screen_height))
        pygame.display.set_caption("Dungeon Adventure")
        self.clock = pygame.time.Clock()

        # Create game elements
        self.dungeon = Dungeon()
        self.adventurer = Adventurer("Player")
        self.rooms = self.create_rooms()
        self.current_room_id = 0

        # Game state
        self.gameActive = False
        self.debugMode = False

    def create_rooms(self, num_rooms=5):
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
                if row > rooms[prev_room_idx].rows:
                    # Current room is below previous room
                    new_room.northDoor = True
                    rooms[prev_room_idx].southDoor = True
                elif row < rooms[prev_room_idx].rows:
                    # Current room is above previous room
                    new_room.southDoor = True
                    rooms[prev_room_idx].northDoor = True
                elif col > rooms[prev_room_idx].cols:
                    # Current room is to the right of previous room
                    new_room.westDoor = True
                    rooms[prev_room_idx].eastDoor = True
                else:
                    # Current room is to the left of previous room
                    new_room.eastDoor = True
                    rooms[prev_room_idx].westDoor = True

            # Add random loot to some rooms
            if random.random() < 0.7:  # 70% chance for loot
                new_room.hasLoot = True
                new_room.possibleLoot = ["Health Potion", "Gold", "Weapon"]

            rooms.append(new_room)

        return rooms

    def startGame(self) -> bool:
        """Start the game and enter the main game loop"""
        self.gameActive = True
        self.gameLoop()
        return self.gameActive

    def endGame(self) -> bool:
        """End the game"""
        self.gameActive = False
        return self.gameActive

    def printCurrentRoom(self) -> None:
        """Display information about the current room"""
        if 0 <= self.current_room_id < len(self.rooms):
            current_room = self.rooms[self.current_room_id]
            print(f"Current Room: {self.current_room_id}")
            print(f"Doors: N={current_room.northDoor}, E={current_room.eastDoor}, "
                  f"S={current_room.southDoor}, W={current_room.westDoor}")
            if current_room.hasLoot:
                print(f"Loot available: {', '.join(current_room.possibleLoot)}")

    def move_to_room(self, direction):
        """Move to an adjacent room if a door exists in that direction"""
        current_room = self.rooms[self.current_room_id]

        # Check if door exists in the requested direction
        if direction == "north" and current_room.northDoor:
            # Find room to the north
            for i, room in enumerate(self.rooms):
                if room.rows == current_room.rows - 1 and room.cols == current_room.cols:
                    self.current_room_id = i
                    return True
        elif direction == "south" and current_room.southDoor:
            # Find room to the south
            for i, room in enumerate(self.rooms):
                if room.rows == current_room.rows + 1 and room.cols == current_room.cols:
                    self.current_room_id = i
                    return True
        elif direction == "east" and current_room.eastDoor:
            # Find room to the east
            for i, room in enumerate(self.rooms):
                if room.rows == current_room.rows and room.cols == current_room.cols + 1:
                    self.current_room_id = i
                    return True
        elif direction == "west" and current_room.westDoor:
            # Find room to the west
            for i, room in enumerate(self.rooms):
                if room.rows == current_room.rows and room.cols == current_room.cols - 1:
                    self.current_room_id = i
                    return True

        return False  # No valid move made

    def gameLoop(self) -> None:
        """Main game loop"""
        while self.gameActive:
            # Handle events
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.gameActive = False
                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE:
                        self.gameActive = False
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
                        self.debugMode = not self.debugMode

            # Update game state
            self.update()

            # Render
            self.render()

            # Cap the frame rate
            self.clock.tick(60)

    def update(self):
        """Update game state"""
        # Update current room
        current_room = self.rooms[self.current_room_id]

        # Handle adventurer updates if needed

    def render(self):
        """Render the game"""
        # Clear the screen
        self.screen.fill((0, 0, 0))

        # Render the current room
        current_room = self.rooms[self.current_room_id]
        current_room.render(self.screen)

        # Render the adventurer
        # self.adventurer.render(self.screen)

        # Debug information
        if self.debugMode:
            self.render_debug_info()

        # Update the display
        pygame.display.flip()

    def render_debug_info(self):
        """Render debug information"""
        font = pygame.font.Font(None, 24)
        current_room = self.rooms[self.current_room_id]

        # Room information
        room_info = f"Room: {self.current_room_id} ({current_room.rows}, {current_room.cols})"
        debug_text = font.render(room_info, True, (255, 255, 255))
        self.screen.blit(debug_text, (10, 10))

        # Door information
        door_info = f"Doors: N={current_room.northDoor}, E={current_room.eastDoor}, S={current_room.southDoor}, W={current_room.westDoor}"
        debug_text = font.render(door_info, True, (255, 255, 255))
        self.screen.blit(debug_text, (10, 40))

        # Loot information
        if current_room.hasLoot:
            loot_info = f"Loot: {', '.join(current_room.possibleLoot)}"
            debug_text = font.render(loot_info, True, (255, 255, 0))
            self.screen.blit(debug_text, (10, 70))

    def __str__(self) -> str:
        return "DungeonAdventure Game"
