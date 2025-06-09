-- Asset pack metadata
CREATE TABLE IF NOT EXISTS asset_packs (
    pack_id TEXT PRIMARY KEY,
    pack_name TEXT NOT NULL,
    author TEXT,
    version TEXT,
    license TEXT,
    base_path TEXT NOT NULL
);

-- Character types (base table for heroes and enemies)
CREATE TABLE IF NOT EXISTS character_types (
    type_id TEXT PRIMARY KEY,
    type_name TEXT NOT NULL,  -- 'hero' or 'enemy'
    display_name TEXT NOT NULL,
    description TEXT
);

-- Character stats (shared by heroes and enemies)
CREATE TABLE IF NOT EXISTS character_stats (
    character_id TEXT PRIMARY KEY,
    type_id TEXT NOT NULL,
    max_health INTEGER NOT NULL,
    speed REAL NOT NULL,
    damage INTEGER NOT NULL,
    attack_range INTEGER NOT NULL,
    armor INTEGER DEFAULT 0,
    magic_resist INTEGER DEFAULT 0,
    critical_chance REAL DEFAULT 0.0,
    FOREIGN KEY (type_id) REFERENCES character_types(type_id)
);

-- Hero-specific stats (extends character_stats)
CREATE TABLE IF NOT EXISTS hero_stats (
    character_id TEXT PRIMARY KEY,
    special_cooldown REAL NOT NULL,
    special_ability_name TEXT NOT NULL,
    unlock_level INTEGER DEFAULT 1,
    FOREIGN KEY (character_id) REFERENCES character_stats(character_id)
);

-- Enemy-specific stats (extends character_stats)
CREATE TABLE IF NOT EXISTS enemy_stats (
    character_id TEXT PRIMARY KEY,
    spawn_weight INTEGER DEFAULT 10,
    experience_value INTEGER NOT NULL,
    gold_drop_min INTEGER DEFAULT 0,
    gold_drop_max INTEGER DEFAULT 0,
    FOREIGN KEY (character_id) REFERENCES character_stats(character_id)
);

-- Animation states reference table
CREATE TABLE IF NOT EXISTS animation_states (
    state_id INTEGER PRIMARY KEY,
    state_name TEXT NOT NULL UNIQUE,
    description TEXT,
    default_frame_rate REAL DEFAULT 24.0,
    default_loop INTEGER DEFAULT 1  -- Boolean
);

-- Character animations (linked to asset packs)
CREATE TABLE IF NOT EXISTS character_animations (
    animation_id INTEGER PRIMARY KEY AUTOINCREMENT,
    character_id TEXT NOT NULL,
    state_id INTEGER NOT NULL,
    pack_id TEXT NOT NULL,
    sprite_sheet_name TEXT NOT NULL,
    frame_count INTEGER NOT NULL,
    frame_width INTEGER NOT NULL,
    frame_height INTEGER NOT NULL,
    frame_rate REAL,
    loop INTEGER,  -- Boolean
    FOREIGN KEY (character_id) REFERENCES character_stats(character_id),
    FOREIGN KEY (state_id) REFERENCES animation_states(state_id),
    FOREIGN KEY (pack_id) REFERENCES asset_packs(pack_id)
);

-- Special effects and projectiles
CREATE TABLE IF NOT EXISTS special_effects (
    effect_id INTEGER PRIMARY KEY AUTOINCREMENT,
    effect_name TEXT NOT NULL,
    pack_id TEXT NOT NULL,
    sprite_sheet_name TEXT NOT NULL,
    frame_count INTEGER NOT NULL,
    frame_width INTEGER NOT NULL,
    frame_height INTEGER NOT NULL,
    frame_rate REAL NOT NULL,
    FOREIGN KEY (pack_id) REFERENCES asset_packs(pack_id)
);

-- Character effect mappings
CREATE TABLE IF NOT EXISTS character_effects (
    character_id TEXT NOT NULL,
    effect_id INTEGER NOT NULL,
    trigger_state_id INTEGER NOT NULL,  -- When this animation state plays
    effect_offset_x INTEGER DEFAULT 0,
    effect_offset_y INTEGER DEFAULT 0,
    PRIMARY KEY (character_id, effect_id, trigger_state_id),
    FOREIGN KEY (character_id) REFERENCES character_stats(character_id),
    FOREIGN KEY (effect_id) REFERENCES special_effects(effect_id),
    FOREIGN KEY (trigger_state_id) REFERENCES animation_states(state_id)
);

-- Initial data population
INSERT OR IGNORE INTO character_types (type_id, type_name, display_name) VALUES
('hero', 'hero', 'Playable Hero'),
('enemy', 'enemy', 'Enemy Character');

-- Standard animation states
INSERT OR IGNORE INTO animation_states (state_id, state_name, description, default_frame_rate, default_loop) VALUES
(0, 'idle', 'Character standing idle', 12.0, 1),
(1, 'walking', 'Character walking', 24.0, 1),
(2, 'running', 'Character running', 24.0, 1),
(3, 'attacking_1', 'Primary attack animation', 20.0, 0),
(4, 'attacking_2', 'Secondary attack animation', 20.0, 0),
(5, 'attacking_3', 'Tertiary attack animation', 20.0, 0),
(6, 'hurt', 'Character taking damage', 15.0, 0),
(7, 'dead', 'Character death animation', 15.0, 0),
(8, 'special_skill', 'Special ability animation', 18.0, 0),
(9, 'jumping', 'Character jumping', 20.0, 0),
(10, 'running_attack', 'Attack while running', 20.0, 0),
(11, 'projectile', 'Projectile animation', 24.0, 0),
(12, 'effect', 'Special effect', 24.0, 0),
(13, 'dying', 'Character dying sequence', 15.0, 0);