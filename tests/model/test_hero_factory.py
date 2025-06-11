import unittest
from src.model.HeroFactory import HeroFactory, HeroType, DungeonHeroFactory
from src.model.knight import Knight
from src.model.archer import Archer
from src.model.cleric import Cleric


class TestHeroFactory(unittest.TestCase):
    """Tests for the HeroFactory class"""

    def setUp(self):
        """Set up a hero factory for testing"""
        self.factory = DungeonHeroFactory()

    def test_supported_types(self):
        """Test that factory supports expected hero types"""
        supported_types = self.factory.get_supported_types()
        
        # Check that all expected types are supported
        self.assertIn(HeroType.KNIGHT, supported_types)
        self.assertIn(HeroType.ARCHER, supported_types)
        self.assertIn(HeroType.CLERIC, supported_types)
        
        # Check count matches expected
        self.assertEqual(len(supported_types), 3)

    def test_create_knight(self):
        """Test creation of Knight hero"""
        x, y = 100, 200
        knight = self.factory.create_hero(HeroType.KNIGHT, x, y)
        
        # Check type and position
        self.assertIsInstance(knight, Knight)
        self.assertEqual(knight.get_x(), x)
        self.assertEqual(knight.get_y(), y)
        self.assertEqual(knight.get_hero_type(), "knight")

    def test_create_archer(self):
        """Test creation of Archer hero"""
        x, y = 150, 250
        archer = self.factory.create_hero(HeroType.ARCHER, x, y)
        
        # Check type and position
        self.assertIsInstance(archer, Archer)
        self.assertEqual(archer.get_x(), x)
        self.assertEqual(archer.get_y(), y)
        self.assertEqual(archer.get_hero_type(), "archer")

    def test_create_cleric(self):
        """Test creation of Cleric hero"""
        x, y = 200, 300
        cleric = self.factory.create_hero(HeroType.CLERIC, x, y)
        
        # Check type and position
        self.assertIsInstance(cleric, Cleric)
        self.assertEqual(cleric.get_x(), x)
        self.assertEqual(cleric.get_y(), y)
        self.assertEqual(cleric.get_hero_type(), "cleric")

    def test_unsupported_type(self):
        """Test that creating an unsupported hero type raises an error"""
        # Create a fake HeroType that's not supported
        class FakeHeroType(HeroType):
            FAKE = "fake"
            
        # Try to create a hero with unsupported type
        with self.assertRaises(ValueError):
            self.factory.create_hero(FakeHeroType.FAKE, 0, 0)


if __name__ == '__main__':
    unittest.main()