import sqlite3
import os
from dataclasses import dataclass
from typing import Dict, List, Optional


@dataclass
class CharacterStats:
    def __init__(self):
        pass
    character_id: str
    type: str  # 'hero' or 'enemy'
    max_health: int
    speed: float
    damage: int
    attack_range: int
    armor: int = 0
    magic_resist: int = 0
    critical_chance: float = 0.0


@dataclass
def HeroStats(CharacterStats):
    def __init__(self):
        pass

    special_cooldown: float
    special_ability_name: str
    unlock_level: int = 1


@dataclass
def EnemyStats(CharacterStats):
    def __init__(self):
        pass

    spawn_weight: int
    experience_value: int
    gold_drop_min: int
    gold_drop_max: int


@dataclass
class AnimationData:
    def __init__(self):
        pass

    sprite_sheet_path: str
    frame_count: int
    frame_width: int
    frame_height: int
    frame_rate: float
    loop: bool


@dataclass
class SpecialEffect:
    effect_id: int
    effect_name: str
    sprite_sheet_path: str
    frame_count: int
    frame_width: int
    frame_height: int
    frame_rate: float


class GameDatabase:
    def __init__(self, db_path='game_data.db'):
        self.db_path = db_path
        self.conn = None

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

    def __enter__(self):
        self.connect()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close()

    def get_character_stats(self, character_id: str) -> Optional[CharacterStats]:
        """Get base stats for any character (hero or enemy)"""
        row = self.conn.execute(
            '''SELECT cs.*, ct.type_name
               FROM character_stats cs
                        JOIN character_types ct ON cs.type_id = ct.type_id
               WHERE cs.character_id = ?''',
            (character_id,)
        ).fetchone()

        if not row:
            return None

        if row['type_name'] == 'hero':
            return self._get_hero_stats(character_id)
        else:
            return self._get_enemy_stats(character_id)

    def _get_hero_stats(self, character_id: str) -> Optional[HeroStats]:
        """Get complete hero stats"""
        row = self.conn.execute(
            '''SELECT cs.*, hs.*, ct.type_name
               FROM character_stats cs
                        JOIN hero_stats hs ON cs.character_id = hs.character_id
                        JOIN character_types ct ON cs.type_id = ct.type_id
               WHERE cs.character_id = ?''',
            (character_id,)
        ).fetchone()

        if not row:
            return None

        return HeroStats(
            character_id=row['character_id'],
            type=row['type_name'],
            max_health=row['max_health'],
            speed=row['speed'],
            damage=row['damage'],
            attack_range=row['attack_range'],
            armor=row['armor'],
            magic_resist=row['magic_resist'],
            critical_chance=row['critical_chance'],
            special_cooldown=row['special_cooldown'],
            special_ability_name=row['special_ability_name'],
            unlock_level=row['unlock_level']
        )

    def _get_enemy_stats(self, character_id: str) -> Optional[EnemyStats]:
        """Get complete enemy stats"""
        row = self.conn.execute(
            '''SELECT cs.*, es.*, ct.type_name
               FROM character_stats cs
                        JOIN enemy_stats es ON cs.character_id = es.character_id
                        JOIN character_types ct ON cs.type_id = ct.type_id
               WHERE cs.character_id = ?''',
            (character_id,)
        ).fetchone()

        if not row:
            return None

        return EnemyStats(
            character_id=row['character_id'],
            type=row['type_name'],
            max_health=row['max_health'],
            speed=row['speed'],
            damage=row['damage'],
            attack_range=row['attack_range'],
            armor=row['armor'],
            magic_resist=row['magic_resist'],
            critical_chance=row['critical_chance'],
            spawn_weight=row['spawn_weight'],
            experience_value=row['experience_value'],
            gold_drop_min=row['gold_drop_min'],
            gold_drop_max=row['gold_drop_max']
        )

    def get_animation(self, character_id: str, state_id: int) -> Optional[AnimationData]:
        """Get animation data for a character state"""
        row = self.conn.execute(
            '''SELECT ca.*, ap.base_path, as.default_frame_rate, as.default_loop
               FROM character_animations ca
                        JOIN asset_packs ap ON ca.pack_id = ap.pack_id
                        JOIN animation_states as
               ON ca.state_id = as.state_id
               WHERE ca.character_id = ? AND ca.state_id = ?''',
            (character_id, state_id)
        ).fetchone()

        if not row:
            return None

        return AnimationData(
            sprite_sheet_path=os.path.join(row['base_path'], row['sprite_sheet_name']),
            frame_count=row['frame_count'],
            frame_width=row['frame_width'],
            frame_height=row['frame_height'],
            frame_rate=row['frame_rate'] if row['frame_rate'] else row['default_frame_rate'],
            loop=bool(row['loop'] if row['loop'] is not None else row['default_loop'])
        )

    def get_character_effects(self, character_id: str, state_id: int) -> List[SpecialEffect]:
        """Get special effects triggered by a character animation state"""
        rows = self.conn.execute(
            '''SELECT se.*, ap.base_path
               FROM character_effects ce
                        JOIN special_effects se ON ce.effect_id = se.effect_id
                        JOIN asset_packs ap ON se.pack_id = ap.pack_id
               WHERE ce.character_id = ?
                 AND ce.trigger_state_id = ?''',
            (character_id, state_id)
        ).fetchall()

        return [
            SpecialEffect(
                effect_id=row['effect_id'],
                effect_name=row['effect_name'],
                sprite_sheet_path=os.path.join(row['base_path'], row['sprite_sheet_name']),
                frame_count=row['frame_count'],
                frame_width=row['frame_width'],
                frame_height=row['frame_height'],
                frame_rate=row['frame_rate']
            )
            for row in rows
        ]

    def get_all_hero_ids(self) -> List[str]:
        """Get IDs of all playable heroes"""
        rows = self.conn.execute(
            '''SELECT cs.character_id
               FROM character_stats cs
               JOIN character_types ct ON cs.type_id = ct.type_id
               WHERE ct.type_name = 'hero'''''
        ).fetchall()
        return [row['character_id'] for row in rows]

    def get_all_enemy_ids(self) -> List[str]:
        """Get IDs of all enemy types"""
        rows = self.conn.execute(
            '''SELECT cs.character_id
               FROM character_stats cs
               JOIN character_types ct ON cs.type_id = ct.type_id
               WHERE ct.type_name = 'enemy'''
        ).fetchall()
        return [row['character_id'] for row in rows]


# Example usage
if __name__ == "__main__":
    with GameDatabase() as db:
        # Get knight stats
        knight = db.get_character_stats('knight')
        print(f"Knight stats: {knight}")

        # Get knight idle animation
        knight_idle = db.get_animation('knight', 0)
        print(f"Knight idle animation: {knight_idle}")

        # Get knight special skill effects
        knight_effects = db.get_character_effects('knight', 8)
        print(f"Knight special effects: {knight_effects}")