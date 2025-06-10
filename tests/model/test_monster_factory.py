import unittest
from src.model.MonsterFactory import MonsterFactory, MonsterType
from src.model.Goblin import Goblin
from src.model.Ogre import Ogre
from src.model.Skeleton import Skeleton
from src.model.DemonBoss import DemonBoss


class TestMonsterFactory(unittest.TestCase):
    """Tests for the MonsterFactory class"""

    def setUp(self):
        """Set up a monster factory for testing"""
        self.factory = MonsterFactory()

    def test_supported_types(self):
        """Test that factory supports expected monster types"""
        supported_types = self.factory.get_supported_types()
        
        # Check that all expected types are supported
        self.assertIn(MonsterType.GOBLIN, supported_types)
        self.assertIn(MonsterType.OGRE, supported_types)
        self.assertIn(MonsterType.SKELETON, supported_types)
        self.assertIn(MonsterType.DEMON_BOSS, supported_types)

    def test_create_goblin(self):
        """Test creation of Goblin monster"""
        goblin = self.factory.create_monster(MonsterType.GOBLIN)
        
        # Check type
        self.assertIsInstance(goblin, Goblin)
        self.assertEqual(goblin.get_name(), "Goblin")

    def test_create_ogre(self):
        """Test creation of Ogre monster"""
        ogre = self.factory.create_monster(MonsterType.OGRE)
        
        # Check type
        self.assertIsInstance(ogre, Ogre)
        self.assertEqual(ogre.get_name(), "Ogre")

    def test_create_skeleton(self):
        """Test creation of Skeleton monster"""
        skeleton = self.factory.create_monster(MonsterType.SKELETON)
        
        # Check type
        self.assertIsInstance(skeleton, Skeleton)
        self.assertEqual(skeleton.get_name(), "Skeleton")

    def test_create_demon_boss(self):
        """Test creation of Demon Boss monster"""
        x, y = 100, 200
        boss = self.factory.create_monster(MonsterType.DEMON_BOSS, x, y)
        
        # Check type and position
        self.assertIsInstance(boss, DemonBoss)
        self.assertEqual(boss.get_name(), "Demon Boss")
        self.assertEqual(boss.get_x(), x)
        self.assertEqual(boss.get_y(), y)

    def test_create_random_monster(self):
        """Test creation of random monster"""
        # Create multiple random monsters
        monsters = [self.factory.create_random_monster() for _ in range(10)]
        
        # Verify all are valid monster instances
        for monster in monsters:
            self.assertTrue(isinstance(monster, (Goblin, Ogre, Skeleton)))
            self.assertFalse(isinstance(monster, DemonBoss))  # Boss shouldn't be random

    def test_create_monster_with_custom_stats(self):
        """Test creation of monster with custom stats"""
        custom_health = 150
        goblin = self.factory.create_monster(MonsterType.GOBLIN, custom_health=custom_health)
        
        # Check custom health was applied
        self.assertEqual(goblin.get_health(), custom_health)

    def test_unsupported_type(self):
        """Test that creating an unsupported monster type raises an error"""
        # Create a fake MonsterType that's not supported
        class FakeMonsterType(MonsterType):
            FAKE = "fake"
            
        # Try to create a monster with unsupported type
        with self.assertRaises(ValueError):
            self.factory.create_monster(FakeMonsterType.FAKE)


if __name__ == '__main__':
    unittest.main()