#!/usr/bin/env python3
"""
Test script for the game database system.
This demonstrates how to use both the SQLite and Mock implementations.
"""

import sys
import os

# Add the src directory to the Python path
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

from utils.GameDatabaseCreator import create_game_database
from utils.SQLiteCharacterStats import SQLiteCharacterStats
from utils.MockCharacterStats import MockCharacterStats


def test_mock_implementation():
    """Test the mock implementation of CharacterStats."""
    print("=== Testing Mock Implementation ===")
    
    # Create mock stats manager
    mock_stats = MockCharacterStats()
    
    # Test hero stats
    print("\n--- Hero Stats ---")
    knight_stats = mock_stats.get_hero_stats('knight')
    if knight_stats:
        print(f"Knight stats: {knight_stats}")
    else:
        print("Knight stats not found")
    
    archer_stats = mock_stats.get_hero_stats('archer')
    if archer_stats:
        print(f"Archer stats: {archer_stats}")
    else:
        print("Archer stats not found")
    
    # Test monster stats
    print("\n--- Monster Stats ---")
    goblin_stats = mock_stats.get_monster_stats('goblin')
    if goblin_stats:
        print(f"Goblin stats: {goblin_stats}")
    else:
        print("Goblin stats not found")
    
    # Test animation data
    print("\n--- Animation Data ---")
    knight_idle = mock_stats.get_hero_animation_data('knight', 'idle')
    if knight_idle:
        print(f"Knight idle animation: {knight_idle}")
    else:
        print("Knight idle animation not found")
    
    # Test getting all animations
    print("\n--- All Knight Animations ---")
    all_knight_anims = mock_stats.get_all_hero_animations('knight')
    for anim_name, anim_data in all_knight_anims.items():
        print(f"  {anim_name}: {anim_data['sprite_path']}")


def test_sqlite_implementation():
    """Test the SQLite implementation of CharacterStats."""
    print("\n=== Testing SQLite Implementation ===")
    
    # First, create the database
    print("Creating game database...")
    create_game_database()
    
    # Create SQLite stats manager
    sqlite_stats = SQLiteCharacterStats('game_data.db')
    
    # Test hero stats
    print("\n--- Hero Stats ---")
    knight_stats = sqlite_stats.get_hero_stats('knight')
    if knight_stats:
        print(f"Knight stats: {knight_stats}")
    else:
        print("Knight stats not found")
    
    archer_stats = sqlite_stats.get_hero_stats('archer')
    if archer_stats:
        print(f"Archer stats: {archer_stats}")
    else:
        print("Archer stats not found")
    
    # Test monster stats
    print("\n--- Monster Stats ---")
    goblin_stats = sqlite_stats.get_monster_stats('goblin')
    if goblin_stats:
        print(f"Goblin stats: {goblin_stats}")
    else:
        print("Goblin stats not found")
    
    # Test animation data
    print("\n--- Animation Data ---")
    knight_idle = sqlite_stats.get_hero_animation_data('knight', 'idle')
    if knight_idle:
        print(f"Knight idle animation: {knight_idle}")
    else:
        print("Knight idle animation not found")
    
    # Test getting all animations
    print("\n--- All Knight Animations ---")
    all_knight_anims = sqlite_stats.get_all_hero_animations('knight')
    for anim_name, anim_data in all_knight_anims.items():
        print(f"  {anim_name}: {anim_data['sprite_path']}")


def compare_implementations():
    """Compare the results from both implementations."""
    print("\n=== Comparing Implementations ===")
    
    mock_stats = MockCharacterStats()
    sqlite_stats = SQLiteCharacterStats('game_data.db')
    
    # Compare knight stats
    mock_knight = mock_stats.get_hero_stats('knight')
    sqlite_knight = sqlite_stats.get_hero_stats('knight')
    
    print(f"\nKnight stats comparison:")
    print(f"Mock: {mock_knight}")
    print(f"SQLite: {sqlite_knight}")
    
    if mock_knight and sqlite_knight:
        print(f"Stats match: {mock_knight == sqlite_knight}")
    
    # Compare knight idle animation
    mock_idle = mock_stats.get_hero_animation_data('knight', 'idle')
    sqlite_idle = sqlite_stats.get_hero_animation_data('knight', 'idle')
    
    print(f"\nKnight idle animation comparison:")
    print(f"Mock: {mock_idle}")
    print(f"SQLite: {sqlite_idle}")
    
    if mock_idle and sqlite_idle:
        print(f"Animations match: {mock_idle == sqlite_idle}")


def main():
    """Main test function."""
    print("Game Database System Test")
    print("=" * 50)
    
    try:
        # Test mock implementation
        test_mock_implementation()
        
        # Test SQLite implementation
        test_sqlite_implementation()
        
        # Compare implementations
        compare_implementations()
        
        print("\n" + "=" * 50)
        print("All tests completed successfully!")
        
    except Exception as e:
        print(f"Error during testing: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main() 