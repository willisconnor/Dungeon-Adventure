from abc import ABC, abstractmethod
from enum import Enum, auto
from typing import Union, Optional

# Import existing monster classes
from src.model.Monster import Monster
from src.model.Goblin import Goblin
from src.model.Skeleton import Skeleton
from src.model.Ogre import Ogre
from src.model.DemonBoss import DemonBoss


class MonsterType(Enum):
    """Enumeration of available monster types"""
    GOBLIN = "goblin"
    SKELETON = "skeleton"
    OGRE = "ogre"
    DEMON_BOSS = "demon_boss"


class MonsterFactory(ABC):
    """Abstract factory for creating monsters using the factory method pattern"""

    @abstractmethod
    def create_monster(self, monster_type: MonsterType, x: int = 0, y: int = 0) -> Union[Monster, DemonBoss]:
        """Factory method to create monsters - must be implemented by concrete factories"""
        pass

    @abstractmethod
    def get_supported_types(self) -> list[MonsterType]:
        """Get list of monster types this factory can create"""
        pass


class DungeonMonsterFactory(MonsterFactory):
    """Concrete factory for creating dungeon monsters"""

    def __init__(self):
        """Initialize the factory with supported monster types"""
        self._supported_types = [
            MonsterType.GOBLIN,
            MonsterType.SKELETON,
            MonsterType.OGRE,
            MonsterType.DEMON_BOSS
        ]

    def create_monster(self, monster_type: MonsterType, x: int = 0, y: int = 0) -> Union[Monster, DemonBoss]:
        """
        Create a monster of the specified type at the given coordinates.

        Args:
            monster_type: The type of monster to create
            x: X coordinate for positioning (used by DemonBoss)
            y: Y coordinate for positioning (used by DemonBoss)

        Returns:
            A monster instance of the requested type

        Raises:
            ValueError: If monster_type is not supported
        """
        if monster_type not in self._supported_types:
            raise ValueError(f"Unsupported monster type: {monster_type}. "
                             f"Supported types: {[t.value for t in self._supported_types]}")

        # Use your existing classes exactly as they are
        if monster_type == MonsterType.GOBLIN:
            return self._create_goblin()
        elif monster_type == MonsterType.SKELETON:
            return self._create_skeleton()
        elif monster_type == MonsterType.OGRE:
            return self._create_ogre()
        elif monster_type == MonsterType.DEMON_BOSS:
            return self._create_demon_boss(x, y)

        # This should never be reached due to the validation above
        raise ValueError(f"Factory method not implemented for {monster_type}")

    def _create_goblin(self) -> Goblin:
        """Create a Goblin using  Goblin class"""
        return Goblin()

    def _create_skeleton(self) -> Skeleton:
        """Create a Skeleton using Skeleton class"""
        return Skeleton()

    def _create_ogre(self) -> Ogre:
        """Create an Ogre using Ogre class"""
        return Ogre()

    def _create_demon_boss(self, x: int, y: int) -> DemonBoss:
        """Create a DemonBoss using DemonBoss class"""
        return DemonBoss(x, y)

    def get_supported_types(self) -> list[MonsterType]:
        """Return list of monster types this factory can create"""
        return self._supported_types.copy()

    def create_random_monster(self, exclude_bosses: bool = True, x: int = 0, y: int = 0) -> Union[Monster, DemonBoss]:
        """
        Create a random monster from supported types.

        Args:
            exclude_bosses: If True, excludes boss monsters from random selection
            x: X coordinate for positioning
            y: Y coordinate for positioning

        Returns:
            A randomly selected monster instance
        """
        import random

        available_types = self._supported_types.copy()

        if exclude_bosses:
            # Filter out boss monsters (monsters with isBoss = True)
            available_types = [t for t in available_types if t != MonsterType.DEMON_BOSS]

        if not available_types:
            raise ValueError("No available monster types after filtering")

        random_type = random.choice(available_types)
        return self.create_monster(random_type, x, y)

    def create_boss_monster(self, x: int = 0, y: int = 0) -> Union[Monster, DemonBoss]:
        """
        Create a boss monster. Currently returns DemonBoss

        Args:
            x: X coordinate for positioning
            y: Y coordinate for positioning

        Returns:
            A boss monster instance
        """
        # For now, we only have one boss type, but this method allows for
        # easy extension when more boss types are added
        return self.create_monster(MonsterType.DEMON_BOSS, x, y)


class MonsterSpawner:
    """
    Utility class that uses the MonsterFactory to spawn monsters in different scenarios.
    This class handles the 'when' and 'where' of monster creation, while the factory
    handles the 'how'.
    """

    def __init__(self, factory: MonsterFactory = None):
        """
        Initialize spawner with a monster factory.

        Args:
            factory: MonsterFactory instance to use. Defaults to DungeonMonsterFactory.
        """
        self.factory = factory if factory is not None else DungeonMonsterFactory()

    def spawn_encounter_group(self, encounter_level: int = 1) -> list[Union[Monster, DemonBoss]]:
        """
        Spawn a group of monsters for an encounter based on difficulty level.

        Args:
            encounter_level: Difficulty level (1-3, where 3 includes bosses)

        Returns:
            List of monster instances for the encounter
        """
        monsters = []

        if encounter_level == 1:
            # Easy encounter - 1-2 basic monsters
            import random
            count = random.randint(1, 2)
            for _ in range(count):
                monsters.append(self.factory.create_random_monster(exclude_bosses=True))

        elif encounter_level == 2:
            # Medium encounter - 2-3 monsters
            import random
            count = random.randint(2, 3)
            for _ in range(count):
                monsters.append(self.factory.create_random_monster(exclude_bosses=True))

        elif encounter_level >= 3:
            # Hard encounter - includes a boss
            monsters.append(self.factory.create_boss_monster())
            # Add some minions
            import random
            minion_count = random.randint(1, 2)
            for _ in range(minion_count):
                monsters.append(self.factory.create_random_monster(exclude_bosses=True))

        return monsters

    def spawn_at_position(self, monster_type: MonsterType, x: int, y: int) -> Union[Monster, DemonBoss]:
        """
        Spawn a specific monster type at given coordinates.

        Args:
            monster_type: Type of monster to spawn
            x: X coordinate
            y: Y coordinate

        Returns:
            Monster instance positioned at specified coordinates
        """
        monster = self.factory.create_monster(monster_type, x, y)


        return monster




