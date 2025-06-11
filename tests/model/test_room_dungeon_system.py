import unittest
from unittest.mock import MagicMock, patch
import pygame
import os
import tempfile
from src.model.RoomDungeonSystem import (
    FloorRenderer, Door, Room, DungeonManager, 
    DoorType, Direction, DoorInteractionState
)


class TestFloorRenderer(unittest.TestCase):
    """Tests for the FloorRenderer class"""

    def setUp(self):
        """Set up test environment"""
        pygame.init()
        
        # Create a temporary CSV file for testing
        self.temp_dir = tempfile.mkdtemp()
        self.csv_path = os.path.join(self.temp_dir, "test_pattern.csv")
        
        # Write a simple pattern to the CSV
        with open(self.csv_path, "w") as f:
            f.write("1,2\n3,4\n")
        
        # Create a floor renderer
        self.tile_size = 32
        self.renderer = FloorRenderer(self.csv_path, self.tile_size)

    def tearDown(self):
        """Clean up temporary files"""
        os.remove(self.csv_path)
        os.rmdir(self.temp_dir)
        pygame.quit()

    def test_initialization(self):
        """Test floor renderer initialization"""
        # Check that the pattern was loaded correctly
        expected_pattern = [[1, 2], [3, 4]]
        self.assertEqual(self.renderer._FloorRenderer__floor_pattern, expected_pattern)
        
        # Check tile size was set correctly
        self.assertEqual(self.renderer._FloorRenderer__tile_size, self.tile_size)

    def test_generate_floor_surface(self):
        """Test generating a floor surface"""
        # Generate a floor surface
        width, height = 100, 100
        surface = self.renderer.generate_floor_surface(width, height)
        
        # Check that a surface was created with the right dimensions
        self.assertIsInstance(surface, pygame.Surface)
        self.assertEqual(surface.get_width(), width)
        self.assertEqual(surface.get_height(), height)

    def test_load_nonexistent_pattern(self):
        """Test loading a pattern from a nonexistent file"""
        # Create a renderer with a nonexistent file
        nonexistent_path = os.path.join(self.temp_dir, "nonexistent.csv")
        renderer = FloorRenderer(nonexistent_path, self.tile_size)
        
        # Should use default pattern
        expected_pattern = [[1, 2], [3, 4]]
        self.assertEqual(renderer._FloorRenderer__floor_pattern, expected_pattern)


class TestDoor(unittest.TestCase):
    """Tests for the Door class"""

    def setUp(self):
        """Set up test environment"""
        pygame.init()
        
        # Door parameters
        self.direction = Direction.UP
        self.dest_room = (1, 2)  # Grid coordinates
        self.width = 80
        self.height = 16
        self.room_width = 800
        self.room_height = 600
        
        # Create a door
        self.door = Door(
            direction=self.direction,
            dest_room=self.dest_room,
            width=self.width,
            height=self.height,
            door_type=DoorType.INTERACTIVE,
            is_locked=False
        )
        
        # Calculate position for the door in a room
        self.door._Door__calculate_door_position(self.room_width, self.room_height)

    def tearDown(self):
        """Clean up pygame"""
        pygame.quit()

    def test_initialization(self):
        """Test door initialization"""
        self.assertEqual(self.door.direction, self.direction)
        self.assertEqual(self.door.dest_room, self.dest_room)
        self.assertEqual(self.door.is_locked(), False)
        self.assertEqual(self.door.door_type(), DoorType.INTERACTIVE)

    def test_collision_detection(self):
        """Test door collision detection"""
        # Position inside door
        inside_pos = (self.door.x() + 5, self.door.y() + 5)
        self.assertTrue(self.door.check_collision(inside_pos))
        
        # Position outside door
        outside_pos = (0, 0)
        self.assertFalse(self.door.check_collision(outside_pos))

    def test_door_locking(self):
        """Test locking and unlocking the door"""
        # Initially unlocked
        self.assertFalse(self.door.is_locked())
        
        # Lock the door
        self.door.lock()
        self.assertTrue(self.door.is_locked())
        
        # Unlock the door
        self.door.unlock()
        self.assertFalse(self.door.is_locked())

    def test_spawn_position_calculation(self):
        """Test calculating spawn position for entity entering door"""
        # Get spawn position for an entity entering through this door
        entity_width, entity_height = 32, 64
        spawn_pos = self.door.get_spawn_position_for_entering_entity(
            entity_width, entity_height, self.room_width, self.room_height
        )
        
        # Should return a valid position (x, y)
        self.assertIsInstance(spawn_pos, tuple)
        self.assertEqual(len(spawn_pos), 2)
        x, y = spawn_pos
        
        # Position should be within room bounds
        self.assertGreaterEqual(x, 0)
        self.assertLess(x, self.room_width)
        self.assertGreaterEqual(y, 0)
        self.assertLess(y, self.room_height)

    def test_automatic_door_entry(self):
        """Test checking if door can be entered automatically"""
        # Interactive doors require interaction
        self.door._Door__door_type = DoorType.INTERACTIVE
        self.assertFalse(self.door.can_enter_automatically())
        
        # Walk-through doors can be entered automatically
        self.door._Door__door_type = DoorType.WALK_THROUGH
        self.assertTrue(self.door.can_enter_automatically())

    def test_interactive_door_entry(self):
        """Test checking if door can be entered with interaction"""
        # Interactive doors can be entered with interaction if unlocked
        self.door._Door__door_type = DoorType.INTERACTIVE
        self.door._Door__is_locked = False
        self.assertTrue(self.door.can_enter_with_interaction())
        
        # Locked doors cannot be entered
        self.door._Door__is_locked = True
        self.assertFalse(self.door.can_enter_with_interaction())
        
        # Walk-through doors don't need interaction
        self.door._Door__door_type = DoorType.WALK_THROUGH
        self.assertFalse(self.door.can_enter_with_interaction())


class TestRoom(unittest.TestCase):
    """Tests for the Room class"""

    def setUp(self):
        """Set up test environment"""
        pygame.init()
        
        # Room parameters
        self.grid_pos = (0, 0)
        self.width = 800
        self.height = 600
        self.tile_size = 32
        
        # Create a room
        self.room = Room(self.grid_pos, self.width, self.height, self.tile_size)

    def tearDown(self):
        """Clean up pygame"""
        pygame.quit()

    def test_initialization(self):
        """Test room initialization"""
        self.assertEqual(self.room.grid_pos(), self.grid_pos)
        self.assertEqual(self.room.width(), self.width)
        self.assertEqual(self.room.height(), self.height)
        self.assertFalse(self.room.is_boss_room())
        self.assertFalse(self.room.is_start_room())
        self.assertEqual(len(self.room.doors()), 0)

    def test_add_door(self):
        """Test adding a door to the room"""
        # Add a door
        direction = Direction.UP
        dest_room = (0, 1)
        door_type = DoorType.INTERACTIVE
        
        self.room.add_door(direction, dest_room, door_type)
        
        # Should now have one door
        self.assertEqual(len(self.room.doors()), 1)
        
        # Door should have correct properties
        door = self.room.get_door_in_direction(direction)
        self.assertIsNotNone(door)
        self.assertEqual(door.direction, direction)
        self.assertEqual(door.dest_room, dest_room)
        self.assertEqual(door.door_type(), door_type)

    def test_get_door_at_position(self):
        """Test getting a door at a specific position"""
        # Add a door
        direction = Direction.UP
        dest_room = (0, 1)
        door_type = DoorType.INTERACTIVE
        
        self.room.add_door(direction, dest_room, door_type)
        
        # Get the door
        door = self.room.get_door_in_direction(direction)
        
        # Get position inside the door
        door_pos = (door.x() + 5, door.y() + 5)
        
        # Should find the door at this position
        found_door = self.room.get_door_at_position(door_pos)
        self.assertEqual(found_door, door)
        
        # Should not find a door at a different position
        not_door_pos = (0, 0)
        not_found_door = self.room.get_door_at_position(not_door_pos)
        self.assertIsNone(not_found_door)

    def test_spawn_position_from_direction(self):
        """Test getting spawn position when entering from a direction"""
        # Get spawn position when entering from UP
        entity_width, entity_height = 32, 64
        spawn_pos = self.room.get_spawn_position_from_direction(
            Direction.UP, entity_width, entity_height
        )
        
        # Should return a valid position
        self.assertIsInstance(spawn_pos, tuple)
        self.assertEqual(len(spawn_pos), 2)
        
        # Position should be within room bounds
        x, y = spawn_pos
        self.assertGreaterEqual(x, 0)
        self.assertLess(x, self.width)
        self.assertGreaterEqual(y, 0)
        self.assertLess(y, self.height)

    def test_room_type_flags(self):
        """Test setting and checking room type flags"""
        # Initially not a boss or start room
        self.assertFalse(self.room.is_boss_room())
        self.assertFalse(self.room.is_start_room())
        
        # Set as boss room
        self.room.set_as_boss_room()
        self.assertTrue(self.room.is_boss_room())
        
        # Set as start room
        self.room.set_as_start_room()
        self.assertTrue(self.room.is_start_room())

    def test_get_opposite_direction(self):
        """Test getting the opposite direction"""
        # Test all directions
        opposite_up = self.room._Room__get_opposite_direction(Direction.UP)
        self.assertEqual(opposite_up, Direction.DOWN)
        
        opposite_down = self.room._Room__get_opposite_direction(Direction.DOWN)
        self.assertEqual(opposite_down, Direction.UP)
        
        opposite_left = self.room._Room__get_opposite_direction(Direction.LEFT)
        self.assertEqual(opposite_left, Direction.RIGHT)
        
        opposite_right = self.room._Room__get_opposite_direction(Direction.RIGHT)
        self.assertEqual(opposite_right, Direction.LEFT)


class TestDungeonManager(unittest.TestCase):
    """Tests for the DungeonManager class"""

    def setUp(self):
        """Set up test environment"""
        pygame.init()
        
        # Create a dungeon manager
        self.grid_width = 3
        self.grid_height = 3
        self.room_width = 800
        self.room_height = 600
        self.tile_size = 32
        
        # Mock the tileset loading
        with patch('pygame.image.load', return_value=pygame.Surface((128, 128))):
            self.manager = DungeonManager(
                self.grid_width, self.grid_height,
                self.room_width, self.room_height,
                self.tile_size
            )

    def tearDown(self):
        """Clean up pygame"""
        pygame.quit()

    def test_initialization(self):
        """Test dungeon manager initialization"""
        # Should create a grid of rooms
        self.assertEqual(self.manager.get_dungeon_width(), self.grid_width)
        self.assertEqual(self.manager.get_dungeon_height(), self.grid_height)
        
        # Should have a current room
        self.assertIsNotNone(self.manager.get_current_room())
        
        # Current room should be in a valid position
        current_pos = self.manager.get_current_room_position()
        self.assertGreaterEqual(current_pos[0], 0)
        self.assertLess(current_pos[0], self.grid_width)
        self.assertGreaterEqual(current_pos[1], 0)
        self.assertLess(current_pos[1], self.grid_height)

    def test_room_transitions(self):
        """Test moving between rooms"""
        # Get current room position
        initial_pos = self.manager.get_current_room_position()
        
        # Find a door in the current room
        current_room = self.manager.get_current_room()
        
        # If the room has doors, try to enter one
        if current_room.doors():
            door = current_room.doors()[0]  # Take the first door
            
            # Try to enter the door
            success = self.manager.try_enter_door(door)
            
            if success:
                # Should now be in a different room
                new_pos = self.manager.get_current_room_position()
                self.assertNotEqual(initial_pos, new_pos)
                
                # Previous room position should be the initial position
                prev_pos = self.manager.get_previous_room_position()
                self.assertEqual(prev_pos, initial_pos)

    def test_get_room_at_position(self):
        """Test getting a room at a specific grid position"""
        # Get current room and its position
        current_room = self.manager.get_current_room()
        current_pos = self.manager.get_current_room_position()
        
        # Get room at current position
        room_at_pos = self.manager.get_room_at_position(current_pos[0], current_pos[1])
        
        # Should be the same room
        self.assertEqual(room_at_pos, current_room)
        
        # Test with invalid position
        invalid_room = self.manager.get_room_at_position(-1, -1)
        self.assertIsNone(invalid_room)

    def test_player_spawn_position(self):
        """Test getting player spawn position for current room"""
        # Get spawn position
        player_width, player_height = 32, 64
        spawn_pos = self.manager.get_player_spawn_position_for_current_room(
            player_width, player_height
        )
        
        # Should return a valid position
        self.assertIsInstance(spawn_pos, tuple)
        self.assertEqual(len(spawn_pos), 2)
        
        # Position should be within room bounds
        x, y = spawn_pos
        self.assertGreaterEqual(x, 0)
        self.assertLess(x, self.room_width)
        self.assertGreaterEqual(y, 0)
        self.assertLess(y, self.room_height)


if __name__ == '__main__':
    unittest.main()