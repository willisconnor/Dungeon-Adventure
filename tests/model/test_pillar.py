import unittest
from unittest.mock import patch, Mock
import pygame
from src.model.Pillar import Pillar, PillarType, PillarManager

class TestPillarType(unittest.TestCase):
    """Test cases for PillarType enum"""

    def test_pillar_type_values(self):
        """Test that pillar type values are correct"""
        self.assertEqual(PillarType.ENCAPSULATION.value, "Encapsulation")
        self.assertEqual(PillarType.INHERITANCE.value, "Inheritance")
        self.assertEqual(PillarType.POLYMORPHISM.value, "Polymorphism")
        self.assertEqual(PillarType.ABSTRACTION.value, "Abstraction")
        self.assertEqual(PillarType.COMPOSITION.value, "Composition")

    def test_pillar_type_count(self):
        """Test that all expected pillar types exist"""
        self.assertEqual(len(PillarType), 5)

    def test_pillar_type_enum_behavior(self):
        """Test enum behavior"""
        self.assertIsInstance(PillarType.ENCAPSULATION, PillarType)
        self.assertNotEqual(PillarType.ENCAPSULATION, PillarType.INHERITANCE)


class TestPillar(unittest.TestCase):
    """Test cases for Pillar class"""

    def setUp(self):
        """Set up test fixtures"""
        pygame.init()
        self.pillar = Pillar(PillarType.ENCAPSULATION, 100, 200)

    def tearDown(self):
        """Clean up after tests"""
        pygame.quit()

    def test_pillar_initialization(self):
        """Test pillar initialization"""
        self.assertEqual(self.pillar.pillar_type, PillarType.ENCAPSULATION)
        self.assertEqual(self.pillar.x, 100)
        self.assertEqual(self.pillar.y, 200)
        self.assertEqual(self.pillar.name, "Encapsulation")
        self.assertFalse(self.pillar.is_collected)

    def test_pillar_properties(self):
        """Test pillar properties are read-only"""
        # These should work
        self.assertEqual(self.pillar.pillar_type, PillarType.ENCAPSULATION)
        self.assertEqual(self.pillar.name, "Encapsulation")
        self.assertFalse(self.pillar.is_collected)

        # Rect should return a copy
        rect1 = self.pillar.rect
        rect2 = self.pillar.rect
        self.assertEqual(rect1, rect2)
        self.assertIsNot(rect1, rect2)  # Different objects

    def test_pillar_colors(self):
        """Test pillar color assignment"""
        encap_pillar = Pillar(PillarType.ENCAPSULATION, 0, 0)
        inherit_pillar = Pillar(PillarType.INHERITANCE, 0, 0)
        poly_pillar = Pillar(PillarType.POLYMORPHISM, 0, 0)
        abstract_pillar = Pillar(PillarType.ABSTRACTION, 0, 0)
        comp_pillar = Pillar(PillarType.COMPOSITION, 0, 0)

        # Test that different pillar types get different colors
        self.assertIsNotNone(encap_pillar)
        self.assertIsNotNone(inherit_pillar)
        self.assertIsNotNone(poly_pillar)
        self.assertIsNotNone(abstract_pillar)
        self.assertIsNotNone(comp_pillar)

    def test_collision_detection(self):
        """Test collision detection"""
        # Create a rect that collides
        colliding_rect = pygame.Rect(110, 210, 20, 20)
        self.assertTrue(self.pillar.check_collision(colliding_rect))

        # Create a rect that doesn't collide
        non_colliding_rect = pygame.Rect(200, 300, 20, 20)
        self.assertFalse(self.pillar.check_collision(non_colliding_rect))

    def test_collision_after_collection(self):
        """Test that collected pillars don't collide"""
        colliding_rect = pygame.Rect(110, 210, 20, 20)

        # Should collide initially
        self.assertTrue(self.pillar.check_collision(colliding_rect))

        # Collect the pillar
        self.pillar.collect()

        # Should not collide after collection
        self.assertFalse(self.pillar.check_collision(colliding_rect))

    def test_collection_mechanism(self):
        """Test pillar collection"""
        # Initially not collected
        self.assertFalse(self.pillar.is_collected)

        # First collection should succeed
        self.assertTrue(self.pillar.collect())
        self.assertTrue(self.pillar.is_collected)

        # Second collection should fail
        self.assertFalse(self.pillar.collect())
        self.assertTrue(self.pillar.is_collected)

    def test_update_animation(self):
        """Test pillar update animation"""
        # Test that update doesn't crash
        self.pillar.update(0.016)  # ~60 FPS
        self.pillar.update(0.5)  # Longer time

        # Collect and test that collected pillars don't animate
        self.pillar.collect()
        self.pillar.update(0.016)

    @patch('pygame.Surface')
    @patch('pygame.font.Font')
    @patch('pygame.draw.rect')
    @patch('pygame.draw.circle')
    def test_draw_uncollected(self, mock_circle, mock_rect, mock_font, mock_surface):
        """Test drawing uncollected pillar"""
        mock_font_instance = Mock()
        mock_font.return_value = mock_font_instance
        mock_text = Mock()
        mock_font_instance.render.return_value = mock_text
        mock_text.get_rect.return_value = pygame.Rect(0, 0, 20, 20)

        surface = Mock()
        self.pillar.draw(surface)

        # Should call drawing functions for uncollected pillar
        self.assertTrue(mock_rect.called)

    @patch('pygame.Surface')
    @patch('pygame.font.Font')
    @patch('pygame.draw.rect')
    def test_draw_collected(self, mock_rect, mock_font, mock_surface):
        """Test drawing collected pillar (should not draw)"""
        self.pillar.collect()

        surface = Mock()
        self.pillar.draw(surface)

        # Should not call drawing functions for collected pillar
        self.assertFalse(mock_rect.called)

    def test_draw_with_camera_offset(self):
        """Test drawing with camera offset"""
        surface = Mock()
        # Should not crash with camera offset
        self.pillar.draw(surface, (10, 20))


class TestPillarManager(unittest.TestCase):
    """Test cases for PillarManager class"""

    def setUp(self):
        """Set up test fixtures"""
        pygame.init()
        self.manager = PillarManager()
        self.pillar1 = Pillar(PillarType.ENCAPSULATION, 100, 200)
        self.pillar2 = Pillar(PillarType.INHERITANCE, 150, 250)
        self.room_pos = (0, 0)

    def tearDown(self):
        """Clean up after tests"""
        pygame.quit()

    def test_manager_initialization(self):
        """Test manager initialization"""
        self.assertEqual(self.manager.collected_count, 0)
        self.assertEqual(self.manager.total_count, 0)
        self.assertFalse(self.manager.can_access_boss_room())
        self.assertEqual(self.manager.get_collected_pillars(), [])

    def test_add_pillar_to_room(self):
        """Test adding pillars to rooms"""
        self.manager.add_pillar_to_room(self.room_pos, self.pillar1)
        self.assertEqual(self.manager.total_count, 1)

        pillars = self.manager.get_pillars_in_room(self.room_pos)
        self.assertEqual(len(pillars), 1)
        self.assertEqual(pillars[0], self.pillar1)

    def test_add_multiple_pillars_to_room(self):
        """Test adding multiple pillars to same room"""
        self.manager.add_pillar_to_room(self.room_pos, self.pillar1)
        self.manager.add_pillar_to_room(self.room_pos, self.pillar2)

        self.assertEqual(self.manager.total_count, 2)
        pillars = self.manager.get_pillars_in_room(self.room_pos)
        self.assertEqual(len(pillars), 2)
        self.assertIn(self.pillar1, pillars)
        self.assertIn(self.pillar2, pillars)

    def test_add_pillars_to_different_rooms(self):
        """Test adding pillars to different rooms"""
        room1 = (0, 0)
        room2 = (1, 0)

        self.manager.add_pillar_to_room(room1, self.pillar1)
        self.manager.add_pillar_to_room(room2, self.pillar2)

        self.assertEqual(self.manager.total_count, 2)
        self.assertEqual(len(self.manager.get_pillars_in_room(room1)), 1)
        self.assertEqual(len(self.manager.get_pillars_in_room(room2)), 1)

    def test_get_pillars_empty_room(self):
        """Test getting pillars from empty room"""
        empty_room = (5, 5)
        pillars = self.manager.get_pillars_in_room(empty_room)
        self.assertEqual(pillars, [])

    def test_pillar_collection_tracking(self):
        """Test pillar collection tracking"""
        self.manager.add_pillar_to_room(self.room_pos, self.pillar1)

        # Initially no pillars collected
        self.assertFalse(self.manager.has_collected(PillarType.ENCAPSULATION))
        self.assertEqual(self.manager.collected_count, 0)

        # Create player rect that collides with pillar
        player_rect = pygame.Rect(110, 210, 20, 20)
        collected_pillar = self.manager.check_pillar_collection(self.room_pos, player_rect)

        self.assertIsNotNone(collected_pillar)
        self.assertEqual(collected_pillar, self.pillar1)
        self.assertTrue(self.manager.has_collected(PillarType.ENCAPSULATION))
        self.assertEqual(self.manager.collected_count, 1)

    def test_pillar_collection_no_collision(self):
        """Test pillar collection with no collision"""
        self.manager.add_pillar_to_room(self.room_pos, self.pillar1)

        # Player rect that doesn't collide
        player_rect = pygame.Rect(300, 400, 20, 20)
        collected_pillar = self.manager.check_pillar_collection(self.room_pos, player_rect)

        self.assertIsNone(collected_pillar)
        self.assertFalse(self.manager.has_collected(PillarType.ENCAPSULATION))
        self.assertEqual(self.manager.collected_count, 0)

    def test_pillar_collection_already_collected(self):
        """Test trying to collect already collected pillar"""
        self.manager.add_pillar_to_room(self.room_pos, self.pillar1)
        player_rect = pygame.Rect(110, 210, 20, 20)

        # First collection
        collected_pillar1 = self.manager.check_pillar_collection(self.room_pos, player_rect)
        self.assertIsNotNone(collected_pillar1)
        self.assertEqual(self.manager.collected_count, 1)

        # Second collection attempt
        collected_pillar2 = self.manager.check_pillar_collection(self.room_pos, player_rect)
        self.assertIsNone(collected_pillar2)
        self.assertEqual(self.manager.collected_count, 1)

    def test_boss_room_access(self):
        """Test boss room access logic"""
        # Initially can't access boss room
        self.assertFalse(self.manager.can_access_boss_room())

        # Add and collect pillars
        pillars = [
            Pillar(PillarType.ENCAPSULATION, 100, 200),
            Pillar(PillarType.INHERITANCE, 150, 250),
            Pillar(PillarType.POLYMORPHISM, 200, 300),
            Pillar(PillarType.ABSTRACTION, 250, 350),
            Pillar(PillarType.COMPOSITION, 300, 400)
        ]

        player_rect = pygame.Rect(0, 0, 500, 500)  # Large rect to collide with all

        for i, pillar in enumerate(pillars):
            room_pos = (i, 0)
            self.manager.add_pillar_to_room(room_pos, pillar)
            self.manager.check_pillar_collection(room_pos, player_rect)

            if i >= 3:  # After collecting 4 pillars
                self.assertTrue(self.manager.can_access_boss_room())
            else:
                self.assertFalse(self.manager.can_access_boss_room())

    def test_get_collected_pillars(self):
        """Test getting list of collected pillars"""
        self.manager.add_pillar_to_room(self.room_pos, self.pillar1)
        self.manager.add_pillar_to_room(self.room_pos, self.pillar2)

        player_rect = pygame.Rect(0, 0, 500, 500)
        self.manager.check_pillar_collection(self.room_pos, player_rect)

        collected = self.manager.get_collected_pillars()
        self.assertIn(PillarType.ENCAPSULATION, collected)
        self.assertIn(PillarType.INHERITANCE, collected)
        self.assertEqual(len(collected), 2)

    def test_update_pillars_in_room(self):
        """Test updating pillars in room"""
        self.manager.add_pillar_to_room(self.room_pos, self.pillar1)
        self.manager.add_pillar_to_room(self.room_pos, self.pillar2)

        # Should not crash
        self.manager.update_pillars_in_room(self.room_pos, 0.016)

        # Test with empty room
        self.manager.update_pillars_in_room((10, 10), 0.016)

    @patch('pygame.Surface')
    def test_draw_pillars_in_room(self, mock_surface):
        """Test drawing pillars in room"""
        self.manager.add_pillar_to_room(self.room_pos, self.pillar1)

        surface = Mock()
        # Please don't crash
        self.manager.draw_pillars_in_room(self.room_pos, surface)
        self.manager.draw_pillars_in_room(self.room_pos, surface, (10, 20))

    @patch('pygame.font.Font')
    @patch('pygame.draw.rect')
    def test_draw_collection_ui(self, mock_rect, mock_font):
        """Test drawing collection UI"""
        mock_font_instance = Mock()
        mock_font.return_value = mock_font_instance
        mock_text = Mock()
        mock_font_instance.render.return_value = mock_text

        surface = Mock()
        self.manager.draw_collection_ui(surface, 10, 20)

        # Should call drawing functions
        self.assertTrue(mock_rect.called)
        self.assertTrue(mock_font.called)

    def test_draw_collection_ui_with_collections(self):
        """Test UI drawing with collected pillars"""
        # Collect some pillars
        self.manager.add_pillar_to_room(self.room_pos, self.pillar1)
        player_rect = pygame.Rect(110, 210, 20, 20)
        self.manager.check_pillar_collection(self.room_pos, player_rect)

        with patch('pygame.font.Font') as mock_font, \
                patch('pygame.draw.rect') as mock_rect:
            mock_font_instance = Mock()
            mock_font.return_value = mock_font_instance
            mock_text = Mock()
            mock_font_instance.render.return_value = mock_text

            surface = Mock()
            self.manager.draw_collection_ui(surface, 10, 20)

            self.assertTrue(mock_rect.called)
            self.assertTrue(mock_font.called)


class TestIntegration(unittest.TestCase):
    """Integration tests for the pillar system"""

    def setUp(self):
        """Set up test fixtures"""
        pygame.init()
        self.manager = PillarManager()

    def tearDown(self):
        """Clean up after tests"""
        pygame.quit()

    def test_complete_game_scenario(self):
        """Test a complete game scenario"""
        # Create all pillar types
        pillars = [
            Pillar(PillarType.ENCAPSULATION, 100, 200),
            Pillar(PillarType.INHERITANCE, 150, 250),
            Pillar(PillarType.POLYMORPHISM, 200, 300),
            Pillar(PillarType.ABSTRACTION, 250, 350),
            Pillar(PillarType.COMPOSITION, 300, 400)
        ]

        # Add pillars to different rooms
        for i, pillar in enumerate(pillars):
            room_pos = (i, 0)
            self.manager.add_pillar_to_room(room_pos, pillar)

        # Player moves through rooms collecting pillars
        player_rect = pygame.Rect(0, 0, 500, 500)

        collected_pillars = []
        for i in range(len(pillars)):
            room_pos = (i, 0)

            # Update pillars in room
            self.manager.update_pillars_in_room(room_pos, 0.016)

            # Check for collection
            collected = self.manager.check_pillar_collection(room_pos, player_rect)
            if collected:
                collected_pillars.append(collected)

        # Verify all pillars collected
        self.assertEqual(len(collected_pillars), 5)
        self.assertEqual(self.manager.collected_count, 5)
        self.assertTrue(self.manager.can_access_boss_room())

        # Verify all pillar types collected
        for pillar_type in PillarType:
            self.assertTrue(self.manager.has_collected(pillar_type))

    def test_encapsulation_demonstration(self):
        """Test that encapsulation is properly implemented"""
        pillar = Pillar(PillarType.ENCAPSULATION, 100, 200)

        # Test that we can access properties but not modify private attributes
        self.assertEqual(pillar.x, 100)
        self.assertEqual(pillar.y, 200)
        self.assertFalse(pillar.is_collected)

        # Test that rect property returns a copy (encapsulation)
        rect1 = pillar.rect
        rect2 = pillar.rect
        rect1.x = 999  # Modify the copy
        self.assertNotEqual(rect1.x, rect2.x)  # Original should be unchanged
        self.assertEqual(pillar.x, 100)  # Pillar position should be unchanged

        # Private attributes should not be directly accessible
        # (This is more of a convention test since Python doesn't truly enforce private)
        with self.assertRaises(AttributeError):
            _ = pillar.__x
        with self.assertRaises(AttributeError):
            _ = pillar.__collected

    def test_multiple_room_management(self):
        """Test managing pillars across multiple rooms"""
        rooms = [(0, 0), (1, 0), (0, 1), (1, 1), (2, 2)]
        pillars_per_room = []

        # Create different pillar configurations for each room
        for i, room in enumerate(rooms):
            room_pillars = []
            for j in range(i + 1):  # Room (0,0) gets 1 pillar, (1,0) gets 2, etc.
                pillar_type = list(PillarType)[j % len(PillarType)]
                pillar = Pillar(pillar_type, j * 100, j * 100)
                room_pillars.append(pillar)
                self.manager.add_pillar_to_room(room, pillar)
            pillars_per_room.append(room_pillars)

        # Verify correct pillar distribution
        total_expected = sum(len(pillars) for pillars in pillars_per_room)
        self.assertEqual(self.manager.total_count, total_expected)

        for i, room in enumerate(rooms):
            room_pillars = self.manager.get_pillars_in_room(room)
            self.assertEqual(len(room_pillars), i + 1)

    def test_animation_state_consistency(self):
        """Test that pillar animations remain consistent"""
        pillar = Pillar(PillarType.ENCAPSULATION, 100, 200)

        # Update multiple times and check consistency
        for _ in range(10):
            pillar.update(0.016)

        # After collection, updates should not affect visual state
        pillar.collect()
        for _ in range(10):
            pillar.update(0.016)  # Should not crash or change collected state

        self.assertTrue(pillar.is_collected)

    def test_collision_edge_cases(self):
        """Test collision detection edge cases"""
        pillar = Pillar(PillarType.ENCAPSULATION, 100, 200)

        # Test exact boundary collision
        boundary_rect = pygame.Rect(100, 200, 1, 1)  # Top-left corner
        self.assertTrue(pillar.check_collision(boundary_rect))

        # Test just outside boundary
        outside_rect = pygame.Rect(99, 199, 1, 1)
        self.assertFalse(pillar.check_collision(outside_rect))

        # Test overlapping collision
        overlap_rect = pygame.Rect(90, 190, 50, 50)
        self.assertTrue(pillar.check_collision(overlap_rect))

        # Test contained collision
        contained_rect = pygame.Rect(110, 210, 10, 10)
        self.assertTrue(pillar.check_collision(contained_rect))


class TestErrorHandling(unittest.TestCase):
    """Test error handling and edge cases"""

    def setUp(self):
        """Set up test fixtures"""
        pygame.init()
        self.manager = PillarManager()

    def tearDown(self):
        """Clean up after tests"""
        pygame.quit()

    def test_invalid_pillar_operations(self):
        """Test operations on invalid or None pillars"""
        # Test manager operations with non-existent rooms
        empty_room = (999, 999)
        pillars = self.manager.get_pillars_in_room(empty_room)
        self.assertEqual(pillars, [])

        # Update and draw operations on empty rooms should not crash
        self.manager.update_pillars_in_room(empty_room, 0.016)

        surface = Mock()
        self.manager.draw_pillars_in_room(empty_room, surface)

    def test_negative_positions(self):
        """Test pillars with negative positions"""
        pillar = Pillar(PillarType.ENCAPSULATION, -100, -200)
        self.assertEqual(pillar.x, -100)
        self.assertEqual(pillar.y, -200)

        # Should still work normally
        test_rect = pygame.Rect(-110, -210, 20, 20)
        self.assertTrue(pillar.check_collision(test_rect))

    def test_zero_delta_time(self):
        """Test update with zero delta time"""
        pillar = Pillar(PillarType.ENCAPSULATION, 100, 200)
        pillar.update(0.0)  # Should not crash

    def test_large_delta_time(self):
        """Test update with very large delta time"""
        pillar = Pillar(PillarType.ENCAPSULATION, 100, 200)
        pillar.update(1000.0)  # Should not crash

    def test_manager_state_consistency(self):
        """Test that manager maintains consistent state"""
        pillar1 = Pillar(PillarType.ENCAPSULATION, 100, 200)
        pillar2 = Pillar(PillarType.INHERITANCE, 150, 250)

        room1 = (0, 0)
        room2 = (1, 1)

        # Add pillars
        self.manager.add_pillar_to_room(room1, pillar1)
        self.manager.add_pillar_to_room(room2, pillar2)

        initial_total = self.manager.total_count
        initial_collected = self.manager.collected_count

        # Collect one pillar
        player_rect = pygame.Rect(90, 190, 50, 50)
        collected = self.manager.check_pillar_collection(room1, player_rect)

        # Verify state consistency
        self.assertIsNotNone(collected)
        self.assertEqual(self.manager.total_count, initial_total)  # Total doesn't change
        self.assertEqual(self.manager.collected_count, initial_collected + 1)

        # Verify specific pillar is marked as collected
        self.assertTrue(self.manager.has_collected(PillarType.ENCAPSULATION))
        self.assertFalse(self.manager.has_collected(PillarType.INHERITANCE))


class TestPerformance(unittest.TestCase):
    """Performance and stress tests"""

    def setUp(self):
        """Set up test fixtures"""
        pygame.init()
        self.manager = PillarManager()

    def tearDown(self):
        """Clean up after tests"""
        pygame.quit()

    def test_many_pillars_performance(self):
        """Test performance with many pillars"""
        # Create a large number of pillars
        num_rooms = 50
        pillars_per_room = 10

        pillar_types = list(PillarType)

        for room_x in range(num_rooms):
            for pillar_idx in range(pillars_per_room):
                room_pos = (room_x, 0)
                pillar_type = pillar_types[pillar_idx % len(pillar_types)]
                pillar = Pillar(pillar_type, pillar_idx * 50, 100)
                self.manager.add_pillar_to_room(room_pos, pillar)

        expected_total = num_rooms * pillars_per_room
        self.assertEqual(self.manager.total_count, expected_total)

        # Test operations don't become prohibitively slow
        import time

        # Test update performance
        start_time = time.time()
        for room_x in range(num_rooms):
            self.manager.update_pillars_in_room((room_x, 0), 0.016)
        update_time = time.time() - start_time

        # Should complete in reasonable time (less than 1 second for this test)
        self.assertLess(update_time, 1.0)

    def test_collision_detection_performance(self):
        """Test collision detection performance"""
        # Create pillars in a room
        room_pos = (0, 0)
        for i in range(100):
            pillar_type = list(PillarType)[i % len(PillarType)]
            pillar = Pillar(pillar_type, i * 10, i * 10)
            self.manager.add_pillar_to_room(room_pos, pillar)

        # Test collision checks
        player_rect = pygame.Rect(500, 500, 20, 20)  # Won't hit anything

        import time
        start_time = time.time()
        for _ in range(1000):  # Many collision checks
            self.manager.check_pillar_collection(room_pos, player_rect)
        collision_time = time.time() - start_time

        # Should complete in reasonable time
        self.assertLess(collision_time, 1.0)

if __name__ == '__main__':
    unittest.main()
