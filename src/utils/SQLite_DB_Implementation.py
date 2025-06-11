import sqlite3
import os
from enum import IntEnum
from typing import List, Dict, Any, Optional, Tuple
from dataclasses import dataclass


class AnimationState(IntEnum):
    IDLE = 0
    WALKING = 1
    RUNNING = 2
    ATTACKING_1 = 3
    ATTACKING_2 = 4
    ATTACKING_3 = 5
    HURT = 6
    DEAD = 7
    SPECIAL_SKILL = 8
    JUMPING = 9
    RUNNING_ATTACK = 10
    PROJECTILE = 11
    EFFECT = 12
    DYING = 13


@dataclass
class AnimationData:
    sprite_sheet_path: str
    frame_count: int
    frame_rate: float
    frame_width: int
    frame_height: int
    loop: bool


class DatabaseHandler:
    """Handles all database operations with asset pack support"""

    def __init__(self, db_path: str = 'game_data.db'):
        self.db_path = db_path
        self.conn = None

    def __enter__(self):
        self.connect()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close()

    def connect(self):
        """Establish database connection"""
        self.conn = sqlite3.connect(self.db_path)
        self.conn.row_factory = sqlite3.Row
        self.conn.execute("PRAGMA foreign_keys = ON")

    def close(self):
        """Close database connection"""
        if self.conn:
            self.conn.close()
            self.conn = None

    def initialize_database(self, asset_packs: List[Dict]):
        """Initialize database with asset pack data"""
        if os.path.exists(self.db_path):
            return

        with self.conn:
            # Create tables from schema
            with open('game_schema.sql', 'r') as f:
                self.conn.executescript(f.read())

            # Insert asset pack data
            self._insert_asset_packs(asset_packs)

            # Insert game characters with asset pack references
            self._insert_default_characters(asset_packs)

    def _insert_asset_packs(self, asset_packs: List[Dict]):
        """Register asset packs in the database"""
        for pack in asset_packs:
            self.conn.execute(
                """INSERT INTO asset_packs
                       (pack_id, pack_name, author, version, license, base_path)
                   VALUES (?, ?, ?, ?, ?, ?)""",
                (pack['id'], pack['name'], pack.get('author'),
                 pack.get('version'), pack.get('license'), pack['path'])
            )

            # Insert animation configurations
            for anim in pack.get('animations', []):
                self.conn.execute(
                    """INSERT INTO animation_config
                       (pack_id, character_type, animation_state, sprite_sheet_name,
                        frame_count, frame_rate, frame_width, frame_height, loop)
                       VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)""",
                    (pack['id'], anim['character_type'], anim['state'],
                     anim['sprite_sheet'], anim['frame_count'],
                     anim.get('frame_rate', 24.0), anim['frame_width'],
                     anim['frame_height'], anim.get('loop', True))
                )

            # Insert special animations
            for special in pack.get('special_animations', []):
                cursor = self.conn.execute(
                    """INSERT INTO special_animations
                       (pack_id, animation_name, sprite_sheet_name,
                        frame_count, frame_rate, frame_width, frame_height)
                       VALUES (?, ?, ?, ?, ?, ?, ?)""",
                    (pack['id'], special['name'], special['sprite_sheet'],
                     special['frame_count'], special.get('frame_rate', 24.0),
                     special['frame_width'], special['frame_height'])
                )

                # Link special animations to characters
                for char_link in special.get('character_links', []):
                    self.conn.execute(
                        """INSERT INTO character_special_animations
                               (character_type, character_name, animation_state, special_animation_id)
                           VALUES (?, ?, ?, ?)""",
                        (char_link['character_type'], char_link['character_name'],
                         char_link['state'], cursor.lastrowid)
                    )

    def _insert_default_characters(self, asset_packs: List[Dict]):
        """Insert heroes and enemies with asset pack references"""
        # Find asset packs by name or ID
        knight_pack = next(p for p in asset_packs if 'knight' in p['id'].lower())
        archer_pack = next(p for p in asset_packs if 'archer' in p['id'].lower())
        cleric_pack = next(p for p in asset_packs if 'cleric' in p['id'].lower())

        # Insert heroes
        heroes = [
            ('knight', 375, 50, 55, 40, 15.0, knight_pack['id']),
            ('cleric', 250, 35, 85, 75, 12.0, cleric_pack['id']),
            ('archer', 150, 20, 40, 150, 10.0, archer_pack['id'])
        ]
        self.conn.executemany(
            """INSERT INTO hero_stats
               (hero_type, max_health, speed, damage, attack_range, special_cooldown, asset_pack_id)
               VALUES (?, ?, ?, ?, ?, ?, ?)""",
            heroes
        )

        # Insert enemies (example)
        skeleton_pack = next(p for p in asset_packs if 'skeleton' in p['id'].lower())
        gorgon_pack = next(p for p in asset_packs if 'gorgon' in p['id'].lower())

        enemies = [
            ('Skeleton_Archer', 50, 10, 50, 100, skeleton_pack['id']),
            ('Skeleton_Spearman', 70, 15, 40, 70, skeleton_pack['id']),
            ('Skeleton_Warrior', 95, 20, 30, 45, skeleton_pack['id']),
            ('Gorgon_1', 100, 75, 35, 40, gorgon_pack['id']),
            ('Gorgon_2', 105, 75, 35, 40, gorgon_pack['id']),
            ('Gorgon_3', 115, 75, 35, 40, gorgon_pack['id'])
        ]
        self.conn.executemany(
            """INSERT INTO enemy_stats
                   (enemy_type, max_health, speed, damage, attack_range, asset_pack_id)
               VALUES (?, ?, ?, ?, ?, ?)""",
            enemies
        )

    # Data access methods
    def get_character_animation(self, character_type: str, character_name: str,
                                state: AnimationState) -> Optional[AnimationData]:
        """Get animation data for a character from its asset pack"""
        # Determine which table to query
        table = 'hero_stats' if character_type == 'hero' else 'enemy_stats'
        id_field = 'hero_type' if character_type == 'hero' else 'enemy_type'

        # Get the asset pack for this character
        pack = self.conn.execute(
            f"""SELECT asset_pack_id FROM {table} WHERE {id_field} = ?""",
            (character_name,)
        ).fetchone()

        if not pack:
            return None

        # Get animation config from the asset pack
        anim = self.conn.execute(
            """SELECT ac.sprite_sheet_name,
                      ac.frame_count,
                      ac.frame_rate,
                      ac.frame_width,
                      ac.frame_height,
                      ac.loop,
                      ap.base_path
               FROM animation_config ac
                        JOIN asset_packs ap ON ac.pack_id = ap.pack_id
               WHERE ac.pack_id = ?
                 AND ac.character_type = ?
                 AND ac.animation_state = ?""",
            (pack['asset_pack_id'], character_type, int(state))
        ).fetchone()

        if anim:
            return AnimationData(
                sprite_sheet_path=os.path.join(anim['base_path'], anim['sprite_sheet_name']),
                frame_count=anim['frame_count'],
                frame_rate=anim['frame_rate'],
                frame_width=anim['frame_width'],
                frame_height=anim['frame_height'],
                loop=bool(anim['loop'])
            )
        return None

    def get_special_animation(self, character_type: str, character_name: str,
                              state: AnimationState) -> Optional[AnimationData]:
        """Get special animation data (projectiles, effects)"""
        anim = self.conn.execute("""
            SELECT sa.sprite_sheet_name,
                      sa.frame_count,
                      sa.frame_rate,
                      sa.frame_width,
                      sa.frame_height,
                      ap.base_path
               FROM character_special_animations csa
                        JOIN special_animations sa ON csa.special_animation_id = sa.animation_id
                        JOIN asset_packs ap ON sa.pack_id = ap.pack_id
               WHERE csa.character_type = ?
                 AND csa.character_name = ?
                 AND csa.animation_state = ?""",
            (character_type, character_name, int(state))
        ).fetchone()

        if anim:
            return AnimationData(
                sprite_sheet_path=os.path.join(anim['base_path'], anim['sprite_sheet_name']),
                frame_count=anim['frame_count'],
                frame_rate=anim['frame_rate'],
                frame_width=anim['frame_width'],
                frame_height=anim['frame_height'],
                loop=False  # Most special animations don't loop
            )
        return None

    def get_character_stats(self, character_type: str, character_name: str) -> Optional[Dict]:
        """Get stats for a character"""
        table = 'hero_stats' if character_type == 'hero' else 'enemy_stats'
        id_field = 'hero_type' if character_type == 'hero' else 'enemy_type'

        cursor = self.conn.execute(
            f'SELECT * FROM {table} WHERE {id_field} = ?',
            (character_name,)
        )
        return dict(cursor.fetchone()) if cursor else None


# Example asset pack configuration
EXAMPLE_ASSET_PACKS = [
    {
        'id': 'knight_pack_1',
        'name': 'Medieval Knight',
        'author': 'GameArtStudio',
        'version': '1.0',
        'license': 'CC-BY-4.0',
        'path': 'assets/sprites/heroes/knight_pack',
        'animations': [
            {
                'character_type': 'hero',
                'state': AnimationState.IDLE,
                'sprite_sheet': 'knight_idle.png',
                'frame_count': 4,
                'frame_width': 64,
                'frame_height': 64,
                'loop': True
            },
            # More animations...
        ],
        'special_animations': [
            {
                'name': 'shield_block',
                'sprite_sheet': 'shield_effect.png',
                'frame_count': 8,
                'frame_width': 128,
                'frame_height': 128,
                'character_links': [
                    {
                        'character_type': 'hero',
                        'character_name': 'knight',
                        'state': AnimationState.SPECIAL_SKILL
                    }
                ]
            }
        ]
    },
    # More asset packs...
]

if __name__ == "__main__":
    with DatabaseHandler() as db:
        db.initialize_database(EXAMPLE_ASSET_PACKS)

        # Example usage
        knight_idle = db.get_character_animation('hero', 'knight', AnimationState.IDLE)
        print(f"Knight idle animation: {knight_idle}")

        knight_stats = db.get_character_stats('hero', 'knight')
        print(f"Knight stats: {knight_stats}")

        knight_special = db.get_special_animation('hero', 'knight', AnimationState.SPECIAL_SKILL)
        print(f"Knight special animation: {knight_special}")