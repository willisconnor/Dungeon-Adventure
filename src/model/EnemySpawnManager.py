"""
EnemySpawnManager.py - Manages pseudo-random enemy spawning throughout the dungeon
Similar to the Pillar system but for enemy distribution
"""
from typing import Dict, List, Tuple, Optional, Set
from enum import Enum
import random
import pygame

# Import the monster factory and types
from src.model.MonsterFactory import MonsterFactory, DungeonMonsterFactory, MonsterType, MonsterSpawner
from src.model.Monster import Monster
from src.model.DemonBoss import DemonBoss


class SpawnPoint:
    """Represents a potential spawn location for enemies"""

    def __init__(self, x: int, y: int, spawn_type: str = "ground"):
        self.__x = x
        self.__y = y
        self.__spawn_type = spawn_type  # "ground", "platform", "air"
        self.__occupied = False
        self.__cooldown = 0.0

    @property
    def x(self) -> int:
        return self.__x

    @property
    def y(self) -> int:
        return self.__y

    @property
    def is_available(self) -> bool:
        return not self.__occupied and self.__cooldown <= 0

    def occupy(self):
        """Mark this spawn point as occupied"""
        self.__occupied = True

    def release(self):
        """Release this spawn point"""
        self.__occupied = False
        self.__cooldown = 5.0  # 5 second cooldown before reuse

    def update(self, dt: float):
        """Update spawn point cooldown"""
        if self.__cooldown > 0:
            self.__cooldown -= dt


class RoomEnemyConfig:
    """Configuration for enemies in a specific room"""

    def __init__(self, room_position: Tuple[int, int]):
        self.__room_position = room_position
        self.__enemy_types: List[MonsterType] = []
        self.__spawn_points: List[SpawnPoint] = []
        self.__min_enemies = 1
        self.__max_enemies = 2
        self.__difficulty_modifier = 1.0
        self.__spawned_enemies: List[Monster] = []
        self.__is_cleared = False

    def add_spawn_point(self, spawn_point: SpawnPoint):
        """Add a spawn point to this room"""
        self.__spawn_points.append(spawn_point)

    def set_enemy_types(self, enemy_types: List[MonsterType]):
        """Set allowed enemy types for this room"""
        self.__enemy_types = enemy_types

    def set_enemy_count(self, min_enemies: int, max_enemies: int):
        """Set min/max enemy count for this room"""
        self.__min_enemies = max(1, min_enemies)
        self.__max_enemies = max(self.__min_enemies, max_enemies)

    def get_spawn_points(self) -> List[SpawnPoint]:
        """Get available spawn points"""
        return [sp for sp in self.__spawn_points if sp.is_available]

    def get_enemy_types(self) -> List[MonsterType]:
        """Get allowed enemy types for this room"""
        return self.__enemy_types.copy()

    def get_enemy_count(self) -> int:
        """Get random enemy count within configured range"""
        return random.randint(self.__min_enemies, self.__max_enemies)

    def mark_cleared(self):
        """Mark this room as cleared"""
        self.__is_cleared = True

    def is_cleared(self) -> bool:
        """Check if room has been cleared"""
        return self.__is_cleared

    def add_spawned_enemy(self, enemy: Monster):
        """Track a spawned enemy"""
        self.__spawned_enemies.append(enemy)

    def remove_dead_enemies(self):
        """Clean up dead enemies from tracking"""
        self.__spawned_enemies = [e for e in self.__spawned_enemies if e.is_alive]

    def has_living_enemies(self) -> bool:
        """Check if room has any living enemies"""
        self.remove_dead_enemies()
        return len(self.__spawned_enemies) > 0


class EnemySpawnManager:
    """Manages enemy spawning throughout the dungeon with proper encapsulation"""

    def __init__(self):
        # Private attributes
        self.__room_configs: Dict[Tuple[int, int], RoomEnemyConfig] = {}
        self.__monster_factory = DungeonMonsterFactory()
        self.__monster_spawner = MonsterSpawner(self.__monster_factory)
        self.__active_enemies: Dict[Tuple[int, int], List[Monster]] = {}
        self.__global_difficulty = 1.0
        self.__rooms_cleared: Set[Tuple[int, int]] = set()

        # Enemy distribution templates
        self.__enemy_templates = {
            "early_game": [MonsterType.GORGON, MonsterType.SKELETON],
            "mid_game": [MonsterType.SKELETON, MonsterType.OGRE],
            "late_game": [MonsterType.OGRE, MonsterType.SKELETON],
            "mixed": [MonsterType.GORGON, MonsterType.SKELETON, MonsterType.OGRE]
        }

    def initialize_room_spawns(self, room_position: Tuple[int, int], room_width: int,
                               room_height: int, floor_y: int, is_boss_room: bool = False,
                               is_start_room: bool = False):
        """Initialize spawn configuration for a room"""
        if is_start_room or is_boss_room:
            # No regular enemies in start or boss rooms
            return

        config = RoomEnemyConfig(room_position)

        # Create spawn points based on room size
        self.__generate_spawn_points(config, room_width, room_height, floor_y)

        # Determine enemy types based on room distance from start
        enemy_template = self.__determine_enemy_template(room_position)
        config.set_enemy_types(enemy_template)

        # Set enemy count based on room position
        min_enemies, max_enemies = self.__calculate_enemy_count(room_position)
        config.set_enemy_count(min_enemies, max_enemies)

        self.__room_configs[room_position] = config

    def __generate_spawn_points(self, config: RoomEnemyConfig, room_width: int,
                                room_height: int, floor_y: int):
        """Generate spawn points for a room"""
        # Create ground spawn points
        num_spawn_points = 4  # Can be adjusted
        margin = 150  # Distance from walls

        for i in range(num_spawn_points):
            # Distribute spawn points across the room width
            x = margin + (i * (room_width - 2 * margin) // (num_spawn_points - 1))
            y = floor_y - 60  # Slightly above floor for enemy height

            spawn_point = SpawnPoint(x, y, "ground")
            config.add_spawn_point(spawn_point)

    def __determine_enemy_template(self, room_position: Tuple[int, int]) -> List[MonsterType]:
        """Determine enemy types based on room position"""
        # Calculate distance from center (assumed start position)
        center = (1, 1)  # Assuming 3x3 grid with center at (1,1)
        distance = abs(room_position[0] - center[0]) + abs(room_position[1] - center[1])

        if distance <= 1:
            return self.__enemy_templates["early_game"]
        elif distance <= 2:
            return self.__enemy_templates["mid_game"]
        else:
            return self.__enemy_templates["late_game"]

    def __calculate_enemy_count(self, room_position: Tuple[int, int]) -> Tuple[int, int]:
        """Calculate min/max enemies based on room position"""
        # Distance from center affects enemy count
        center = (1, 1)
        distance = abs(room_position[0] - center[0]) + abs(room_position[1] - center[1])

        if distance <= 1:
            return (1, 2)
        elif distance <= 2:
            return (2, 3)
        else:
            return (2, 4)

    def spawn_enemies_for_room(self, room_position: Tuple[int, int], ground_y_override: int = None) -> List[Monster]:
        """Spawn enemies for a specific room"""
        if room_position not in self.__room_configs:
            return []

        config = self.__room_configs[room_position]

        # Don't spawn if room is already cleared
        if config.is_cleared():
            return []

        # Clean up any dead enemies first
        config.remove_dead_enemies()

        # Don't spawn if enemies still alive in room
        if config.has_living_enemies():
            return []

        spawned_enemies = []
        spawn_points = config.get_spawn_points()
        enemy_types = config.get_enemy_types()
        
        # Use the corrected method to get enemy count
        enemy_count = min(config.get_enemy_count(), len(spawn_points))

        # Shuffle spawn points for variety
        random.shuffle(spawn_points)

        for i in range(enemy_count):
            if i < len(spawn_points) and enemy_types:
                spawn_point = spawn_points[i]
                enemy_type = random.choice(enemy_types)

                # Create enemy at spawn point - notice we're using a ground-relative Y position
                enemy = self.__monster_factory.create_monster(
                    enemy_type,
                    spawn_point.x,
                    spawn_point.y
                )
                
                # Make sure the enemy is positioned correctly relative to the ground
                # This ensures the enemy's feet are on the ground
                if ground_y_override is not None:
                    # Position the enemy with its feet on the ground
                    enemy_height = enemy.rect.height if hasattr(enemy, 'rect') else 64
                    enemy.set_position(enemy.rect.x, ground_y_override - enemy_height)

                # Occupy the spawn point
                spawn_point.occupy()

                # Track the enemy
                config.add_spawned_enemy(enemy)
                spawned_enemies.append(enemy)

                # Store in active enemies dict
                if room_position not in self.__active_enemies:
                    self.__active_enemies[room_position] = []
                self.__active_enemies[room_position].append(enemy)

        return spawned_enemies

    def create_enemy_at_position(self, x: int, y: int) -> Optional[Monster]:
        """Create an enemy at the specified position"""
        enemy_type = random.choice([MonsterType.GORGON, MonsterType.SKELETON, MonsterType.OGRE])
        return self.__monster_factory.create_monster(enemy_type, x, y)

    def update(self, current_room_position: Tuple[int, int], dt: float):
        """Update spawn manager for current room"""
        if current_room_position in self.__room_configs:
            config = self.__room_configs[current_room_position]

            # Update spawn point cooldowns
            for spawn_point in config.get_spawn_points():
                spawn_point.update(dt)

            # Check if room is cleared
            if not config.has_living_enemies() and len(self.__active_enemies.get(current_room_position, [])) > 0:
                config.mark_cleared()
                self.__rooms_cleared.add(current_room_position)

    def get_active_enemies_for_room(self, room_position: Tuple[int, int]) -> List[Monster]:
        """Get list of active enemies in a specific room"""
        if room_position in self.__active_enemies:
            # Filter out dead enemies
            alive_enemies = [e for e in self.__active_enemies[room_position] if e.is_alive]
            self.__active_enemies[room_position] = alive_enemies
            return alive_enemies
        return []

    def clear_room_enemies(self, room_position: Tuple[int, int]):
        """Clear all enemies from a room (used when leaving room)"""
        if room_position in self.__active_enemies:
            self.__active_enemies[room_position].clear()

    def is_room_cleared(self, room_position: Tuple[int, int]) -> bool:
        """Check if a room has been cleared of enemies"""
        return room_position in self.__rooms_cleared

    def reset_room(self, room_position: Tuple[int, int]):
        """Reset a room's cleared status (for respawning)"""
        if room_position in self.__rooms_cleared:
            self.__rooms_cleared.remove(room_position)
        if room_position in self.__room_configs:
            self.__room_configs[room_position].mark_cleared(False)

    def set_global_difficulty(self, difficulty: float):
        """Set global difficulty modifier (affects enemy stats)"""
        self.__global_difficulty = max(0.5, min(2.0, difficulty))

    def get_rooms_cleared_count(self) -> int:
        """Get number of rooms cleared"""
        return len(self.__rooms_cleared)

    def get_total_enemies_in_room(self, room_position: Tuple[int, int]) -> int:
        """Get total number of enemies that can spawn in a room"""
        if room_position in self.__room_configs:
            config = self.__room_configs[room_position]
            return config.get_enemy_count()
        return 0

    def _setup_ground_movement(self, enemy: Monster):
        """Setup enemy for ground-only movement"""
        # Disable vertical movement capabilities
        if hasattr(enemy, 'can_jump'):
            enemy.can_jump = False
        if hasattr(enemy, 'can_fly'):
            enemy.can_fly = False
        if hasattr(enemy, 'gravity_enabled'):
            enemy.gravity_enabled = False

        # Set movement constraints
        if hasattr(enemy, 'movement_type'):
            enemy.movement_type = 'ground_only'