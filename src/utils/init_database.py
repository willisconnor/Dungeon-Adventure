import sqlite3
import os
from enum import IntEnum


class DatabaseInitializer:
    def __init__(self, db_path='game_data.db'):
        self.db_path = db_path
        self.conn = None

    def initialize(self):
        """Initialize the complete database structure and data"""
        if os.path.exists(self.db_path):
            os.remove(self.db_path)  # For development, remove in production

        self.conn = sqlite3.connect(self.db_path)
        self.conn.row_factory = sqlite3.Row
        self.conn.execute("PRAGMA foreign_keys = ON")

        # Create schema
        with open('game_schema.sql', 'r') as f:
            self.conn.executescript(f.read())

        # Insert all game data
        self._insert_asset_packs()
        self._insert_characters()
        self._insert_animations()
        self._insert_special_effects()

        self.conn.commit()
        self.conn.close()

    def _insert_asset_packs(self):
        """Insert all asset pack metadata"""
        packs = [
            ('knight_pack', 'Knight Assets', 'GameArtStudio', '1.0',
             'CC-BY-4.0', 'assets/sprites/heroes/knight'),
            ('archer_pack', 'Archer Assets', 'GameArtStudio', '1.0',
             'CC-BY-4.0', 'assets/sprites/heroes/archer'),
            ('cleric_pack', 'Cleric Assets', 'GameArtStudio', '1.0',
             'CC-BY-4.0', 'assets/sprites/heroes/cleric'),
            ('skeleton_pack', 'Skeleton Enemies', 'MonsterFactory', '1.2',
             'CC-BY-4.0', 'assets/sprites/enemies/skeletons'),
            ('gorgon_pack', 'Gorgon Enemies', 'MonsterFactory', '1.1',
             'CC-BY-4.0', 'assets/sprites/enemies/gorgons')
        ]
        self.conn.executemany(
            '''INSERT INTO asset_packs
                   (pack_id, pack_name, author, version, license, base_path)
               VALUES (?, ?, ?, ?, ?, ?)''',
            packs
        )

    def _insert_characters(self):
        """Insert all playable heroes and enemies"""
        # Base character stats
        characters = [
            # character_id, type_id, max_health, speed, damage, attack_range
            ('knight', 'hero', 375, 50, 55, 40),
            ('cleric', 'hero', 250, 35, 85, 75),
            ('archer', 'hero', 150, 20, 40, 150),
            ('skeleton_archer', 'enemy', 50, 10, 50, 100),
            ('skeleton_spearman', 'enemy', 70, 15, 40, 70),
            ('skeleton_warrior', 'enemy', 95, 20, 30, 45),
            ('gorgon_1', 'enemy', 100, 75, 35, 40),
            ('gorgon_2', 'enemy', 105, 75, 35, 40),
            ('gorgon_3', 'enemy', 115, 75, 35, 40)
        ]
        self.conn.executemany(
            '''INSERT INTO character_stats
                   (character_id, type_id, max_health, speed, damage, attack_range)
               VALUES (?, ?, ?, ?, ?, ?)''',
            characters
        )

        # Hero-specific stats
        heroes = [
            ('knight', 15.0, 'Shield Bash', 1),
            ('cleric', 12.0, 'Healing Light', 1),
            ('archer', 10.0, 'Piercing Shot', 1)
        ]
        self.conn.executemany(
            '''INSERT INTO hero_stats
                   (character_id, special_cooldown, special_ability_name, unlock_level)
               VALUES (?, ?, ?, ?)''',
            heroes
        )

        # Enemy-specific stats
        enemies = [
            ('skeleton_archer', 10, 50, 5, 10),
            ('skeleton_spearman', 15, 70, 7, 14),
            ('skeleton_warrior', 20, 95, 10, 20),
            ('gorgon_1', 15, 100, 15, 30),
            ('gorgon_2', 15, 105, 15, 30),
            ('gorgon_3', 15, 115, 15, 30)
        ]
        self.conn.executemany(
            '''INSERT INTO enemy_stats
               (character_id, spawn_weight, experience_value, gold_drop_min, gold_drop_max)
               VALUES (?, ?, ?, ?, ?)''',
            enemies
        )

    def _insert_animations(self):
        """Insert all character animations"""
        animations = [
            # Knight animations
            ('knight', 0, 'knight_pack', 'idle.png', 4, 64, 64, 12.0, 1),
            ('knight', 1, 'knight_pack', 'walk.png', 8, 64, 64, 24.0, 1),
            ('knight', 3, 'knight_pack', 'attack1.png', 5, 64, 64, 20.0, 0),
            # ... more knight animations

            # Archer animations
            ('archer', 0, 'archer_pack', 'idle.png', 9, 64, 64, 12.0, 1),
            ('archer', 1, 'archer_pack', 'walk.png', 8, 64, 64, 24.0, 1),
            ('archer', 3, 'archer_pack', 'attack.png', 14, 64, 64, 20.0, 0),
            # ... more archer animations

            # Skeleton animations
            ('skeleton_archer', 0, 'skeleton_pack', 'archer_idle.png', 4, 64, 64, 12.0, 1),
            ('skeleton_archer', 1, 'skeleton_pack', 'archer_walk.png', 6, 64, 64, 24.0, 1),
            ('skeleton_archer', 3, 'skeleton_pack', 'archer_attack.png', 5, 64, 64, 20.0, 0),
            # ... more enemy animations
        ]
        self.conn.executemany(
            '''INSERT INTO character_animations
               (character_id, state_id, pack_id, sprite_sheet_name,
                frame_count, frame_width, frame_height, frame_rate, loop)
               VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)''',
            animations
        )

    def _insert_special_effects(self):
        """Insert special effects and link to characters"""
        # Insert effects
        effects = [
            ('fireball', 'cleric_pack', 'fireball.png', 12, 32, 32, 24.0),
            ('arrow', 'archer_pack', 'arrow.png', 1, 32, 32, 24.0),
            ('shield_effect', 'knight_pack', 'shield_bash.png', 8, 64, 64, 18.0)
        ]
        effect_ids = []
        for effect in effects:
            cursor = self.conn.execute(
                '''INSERT INTO special_effects
                   (effect_name, pack_id, sprite_sheet_name,
                    frame_count, frame_width, frame_height, frame_rate)
                   VALUES (?, ?, ?, ?, ?, ?, ?)''',
                effect
            )
            effect_ids.append(cursor.lastrowid)

        # Link effects to characters
        effect_links = [
            ('cleric', effect_ids[0], 8),  # Fireball on special skill
            ('archer', effect_ids[1], 3),  # Arrow on attack1
            ('archer', effect_ids[1], 4),  # Arrow on attack2
            ('archer', effect_ids[1], 5),  # Arrow on attack3
            ('knight', effect_ids[2], 8)  # Shield effect on special
        ]
        self.conn.executemany(
            '''INSERT INTO character_effects
                   (character_id, effect_id, trigger_state_id)
               VALUES (?, ?, ?)''',
            effect_links
        )


if __name__ == "__main__":
    initializer = DatabaseInitializer()
    initializer.initialize()
    print("Database initialized with all character data!")