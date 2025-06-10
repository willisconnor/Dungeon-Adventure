import unittest
from unittest.mock import MagicMock, patch
import pygame
from src.view.Menu import Button


class TestButton(unittest.TestCase):
    """Tests for the Button class in Menu"""

    def setUp(self):
        """Set up Button test environment"""
        # Initialize pygame
        pygame.init()
        
        # Mock the font
        self.mock_font = MagicMock()
        self.mock_font.render = MagicMock(return_value=pygame.Surface((100, 30)))
        
        # Button parameters
        self.image = pygame.Surface((120, 40))
        self.pos = (300, 200)
        self.text = "Test Button"
        self.base_color = (255, 255, 255)
        self.hover_color = (200, 200, 200)
        self.action = "test_action"
        
        # Create button
        self.button = Button(
            image=self.image,
            pos=self.pos,
            text_input=self.text,
            font=self.mock_font,
            base_color=self.base_color,
            hovering_color=self.hover_color,
            action=self.action
        )

    def tearDown(self):
        """Clean up pygame"""
        pygame.quit()

    def test_initialization(self):
        """Test button initialization"""
        # Check that the button has correct action
        self.assertEqual(self.button.action, self.action)
        
        # Create a button with no image
        text_only_button = Button(
            image=None,
            pos=self.pos,
            text_input=self.text,
            font=self.mock_font,
            base_color=self.base_color,
            hovering_color=self.hover_color,
            action=self.action
        )
        
        # Check that text-only button was created successfully
        self.assertEqual(text_only_button.action, self.action)

    def test_update(self):
        """Test button update method"""
        # Create a mock screen
        mock_screen = MagicMock()
        mock_screen.blit = MagicMock()
        
        # Update the button
        self.button.update(mock_screen)
        
        # Verify that screen.blit was called twice (once for image, once for text)
        self.assertEqual(mock_screen.blit.call_count, 2)

    def test_check_for_input(self):
        """Test button input checking"""
        # Position inside button (assuming button is centered on pos)
        inside_pos = (self.pos[0], self.pos[1])
        self.assertTrue(self.button.check_for_input(inside_pos))
        
        # Position outside button
        outside_pos = (self.pos[0] + 100, self.pos[1] + 100)
        self.assertFalse(self.button.check_for_input(outside_pos))

    def test_change_color(self):
        """Test button color changing based on hover"""
        # Mock the font.render method
        self.mock_font.render = MagicMock()
        
        # Test hover color change
        hover_pos = self.pos  # Position over the button
        self.button.change_color(hover_pos)
        
        # Should render with hover color
        self.mock_font.render.assert_called_with(self.text, True, self.hover_color)
        
        # Reset mock
        self.mock_font.render.reset_mock()
        
        # Test base color
        non_hover_pos = (0, 0)  # Position away from button
        self.button.change_color(non_hover_pos)
        
        # Should render with base color
        self.mock_font.render.assert_called_with(self.text, True, self.base_color)


if __name__ == '__main__':
    unittest.main()