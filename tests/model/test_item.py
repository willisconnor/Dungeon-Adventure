import unittest
from unittest.mock import MagicMock
from src.model.Item import Item


class TestItem(unittest.TestCase):
    """Tests for the Item class"""

    def setUp(self):
        """Set up an Item instance for testing"""
        self.item_name = "Health Potion"
        self.item_type = "consumable"
        self.item_value = 50
        self.item = Item(self.item_name, self.item_type, self.item_value)

    def test_initialization(self):
        """Test that an item is initialized with correct values"""
        self.assertEqual(self.item.get_name(), self.item_name)
        self.assertEqual(self.item.get_type(), self.item_type)
        self.assertEqual(self.item.get_value(), self.item_value)
        self.assertFalse(self.item.is_used())

    def test_use_item(self):
        """Test using an item"""
        # Create a mock hero
        hero = MagicMock()
        
        # Item is not used initially
        self.assertFalse(self.item.is_used())
        
        # Use the item
        result = self.item.use(hero)
        
        # Check result and state
        self.assertTrue(result)
        self.assertTrue(self.item.is_used())

    def test_use_already_used_item(self):
        """Test using an already used item"""
        # Create a mock hero
        hero = MagicMock()
        
        # Use the item once
        self.item.use(hero)
        
        # Try to use it again
        result = self.item.use(hero)
        
        # Should fail
        self.assertFalse(result)

    def test_item_effect(self):
        """Test item effect on hero"""
        # Create a mock hero
        hero = MagicMock()
        
        # Use the item
        self.item.use(hero)
        
        # If item has specific effects, check they were applied
        if self.item_type == "health_potion":
            hero.heal.assert_called_once_with(self.item_value)
        elif self.item_type == "damage_boost":
            hero.boost_damage.assert_called_once_with(self.item_value)
        # Add checks for other item types as needed

    def test_reset_item(self):
        """Test resetting a used item"""
        # Create a mock hero
        hero = MagicMock()
        
        # Use the item
        self.item.use(hero)
        self.assertTrue(self.item.is_used())
        
        # Reset the item
        self.item.reset()
        self.assertFalse(self.item.is_used())
        
        # Should be able to use it again
        result = self.item.use(hero)
        self.assertTrue(result)

    def test_copy_item(self):
        """Test creating a copy of an item"""
        # Use the item
        hero = MagicMock()
        self.item.use(hero)
        
        # Create a copy
        item_copy = self.item.copy()
        
        # Verify copy has same properties but is not used
        self.assertEqual(item_copy.get_name(), self.item_name)
        self.assertEqual(item_copy.get_type(), self.item_type)
        self.assertEqual(item_copy.get_value(), self.item_value)
        self.assertFalse(item_copy.is_used())

    def test_string_representation(self):
        """Test the string representation of the item"""
        item_str = str(self.item)
        
        # Check that string contains important information
        self.assertIn(self.item_name, item_str)
        self.assertIn(self.item_type, item_str)
        self.assertIn(str(self.item_value), item_str)
        self.assertIn("Not Used", item_str)
        
        # Use the item and check string again
        hero = MagicMock()
        self.item.use(hero)
        used_item_str = str(self.item)
        self.assertIn("Used", used_item_str)


if __name__ == '__main__':
    unittest.main()