from abc import ABC, abstractmethod
from enum import Enum, auto
from typing import Union, Optional

# Import existing hero classes
from src.model.DungeonHero import Hero
from src.model.knight import Knight
from src.model.archer import Archer
from src.model.cleric import Cleric


class HeroType(Enum):
    """Enumeration of available hero types"""
    KNIGHT = "knight"
    ARCHER = "archer"
    CLERIC = "cleric"


class HeroFactory(ABC):
    """Abstract factory for creating heroes using the factory method pattern"""

    @abstractmethod
    def create_hero(self, hero_type: HeroType, x: int = 0, y: int = 0) -> Hero:
        """Factory method to create heroes - must be implemented by concrete factories"""
        pass

    @abstractmethod
    def get_supported_types(self) -> list[HeroType]:
        """Get list of hero types this factory can create"""
        pass


class DungeonHeroFactory(HeroFactory):
    """Concrete factory for creating dungeon heroes"""

    def __init__(self):
        """Initialize the factory with supported hero types"""
        self._supported_types = [
            HeroType.KNIGHT,
            HeroType.ARCHER,
            HeroType.CLERIC
        ]

    def create_hero(self, hero_type: HeroType, x: int = 0, y: int = 0) -> Hero:
        """
        Create a hero of the specified type at the given coordinates.

        Args:
            hero_type: The type of hero to create
            x: X coordinate for positioning
            y: Y coordinate for positioning

        Returns:
            A hero instance of the requested type

        Raises:
            ValueError: If hero_type is not supported
        """
        if hero_type not in self._supported_types:
            raise ValueError(f"Unsupported hero type: {hero_type}. "
                             f"Supported types: {[t.value for t in self._supported_types]}")

        if hero_type == HeroType.KNIGHT:
            return self._create_knight(x, y)
        elif hero_type == HeroType.ARCHER:
            return self._create_archer(x, y)
        elif hero_type == HeroType.CLERIC:
            return self._create_cleric(x, y)

        # This should never be reached due to the validation above
        raise ValueError(f"Factory method not implemented for {hero_type}")

    def _create_knight(self, x: int, y: int) -> Knight:
        """Create a Knight using Knight class"""
        return Knight(x, y)

    def _create_archer(self, x: int, y: int) -> Archer:
        """Create an Archer using Archer class"""
        return Archer(x, y)

    def _create_cleric(self, x: int, y: int) -> Cleric:
        """Create a Cleric using Cleric class"""
        return Cleric(x, y)

    def get_supported_types(self) -> list[HeroType]:
        """Return list of hero types this factory can create"""
        return self._supported_types.copy()