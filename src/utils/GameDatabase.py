from abc import ABC, abstractmethod
from typing import Dict, Any, Optional


class CharacterStats(ABC):
    """Base interface class for character statistics.
       This follows the Mock Object pattern to allow for testing and different data sources."""
    
    @abstractmethod
    def get_hero_stats(self, hero_type: str) -> Optional[Dict[str, Any]]:
        """Get stats for a specific hero type.
        
        Args:
            hero_type: The type of hero (e.g., 'knight', 'archer', 'cleric')
            
        Returns:
            Dictionary containing hero stats or None if not found
        """
        pass
    
    @abstractmethod
    def get_monster_stats(self, monster_type: str) -> Optional[Dict[str, Any]]:
        """Get stats for a specific monster type.
        
        Args:
            monster_type: The type of monster (e.g., 'gorgon', 'orc', 'boss')
            
        Returns:
            Dictionary containing monster stats or None if not found
        """
        pass
    
    @abstractmethod
    def get_hero_animation_data(self, hero_type: str, animation_state: str) -> Optional[Dict[str, Any]]:
        """Get animation data for a specific hero and animation state.
        
        Args:
            hero_type: The type of hero
            animation_state: The animation state (e.g., 'idle', 'walking', 'attacking')
            
        Returns:
            Dictionary containing animation data or None if not found
        """
        pass
    
    @abstractmethod
    def get_monster_animation_data(self, monster_type: str, animation_state: str) -> Optional[Dict[str, Any]]:
        """Get animation data for a specific monster and animation state.
        
        Args:
            monster_type: The type of monster
            animation_state: The animation state
            
        Returns:
            Dictionary containing animation data or None if not found
        """
        pass 