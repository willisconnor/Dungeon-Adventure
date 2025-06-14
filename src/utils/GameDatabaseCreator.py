import sqlite3
from sqlite3 import Error

def create_connection(db_file):
    try:
        conn = sqlite3.connect(db_file)
        return conn
    except Error as e:
        print(e)
    return None

def create_hero_stats_table(conn):
    try:
        c = conn.cursor()
        c.execute('''CREATE TABLE IF NOT EXISTS hero_stats (
            hero_type TEXT PRIMARY KEY,
            max_health INTEGER NOT NULL,
            health INTEGER NOT NULL,
            speed INTEGER NOT NULL,
            damage INTEGER NOT NULL,
            attack_range INTEGER NOT NULL,
            attack_speed REAL NOT NULL,
            special_cooldown REAL NOT NULL,
            defense INTEGER NOT NULL,
            critical_chance REAL NOT NULL,
            critical_damage REAL NOT NULL
        );''')
        print('hero_stats table created')
    except Error as e:
        print(e)

def create_monster_stats_table(conn):
    try:
        c = conn.cursor()
        c.execute('''CREATE TABLE IF NOT EXISTS monster_stats (
            monster_type TEXT PRIMARY KEY,
            max_health INTEGER NOT NULL,
            health INTEGER NOT NULL,
            speed INTEGER NOT NULL,
            damage INTEGER NOT NULL,
            attack_range INTEGER NOT NULL,
            attack_speed REAL NOT NULL,
            defense INTEGER NOT NULL,
            critical_chance REAL NOT NULL,
            critical_damage REAL NOT NULL,
            experience_value INTEGER NOT NULL,
            gold_value INTEGER NOT NULL
        );''')
        print('monster_stats table created')
    except Error as e:
        print(e)

def create_hero_animations_table(conn):
    try:
        c = conn.cursor()
        c.execute('''CREATE TABLE IF NOT EXISTS hero_animations (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            hero_type TEXT NOT NULL,
            animation_state TEXT NOT NULL,
            sprite_path TEXT NOT NULL,
            frame_count INTEGER NOT NULL,
            frame_rate REAL NOT NULL,
            frame_width INTEGER NOT NULL,
            frame_height INTEGER NOT NULL,
            UNIQUE(hero_type, animation_state)
        );''')
        print('hero_animations table created')
    except Error as e:
        print(e)

def create_monster_animations_table(conn):
    try:
        c = conn.cursor()
        c.execute('''CREATE TABLE IF NOT EXISTS monster_animations (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            monster_type TEXT NOT NULL,
            animation_state TEXT NOT NULL,
            sprite_path TEXT NOT NULL,
            frame_count INTEGER NOT NULL,
            frame_rate REAL NOT NULL,
            frame_width INTEGER NOT NULL,
            frame_height INTEGER NOT NULL,
            UNIQUE(monster_type, animation_state)
        );''')
        print('monster_animations table created')
    except Error as e:
        print(e)

def insert_hero_stats(conn):
    try:
        heroes = [
            ('knight', 375, 375, 12, 55, 80, 1.3, 10.0, 20, 0.1, 1.5),
            ('archer', 150, 150, 10, 40, 120, 2.0, 8.0, 10, 0.15, 2.0),
            ('cleric', 250, 250, 8, 85, 60, 0.75, 12.0, 15, 0.05, 1.8)
        ]
        sql = '''INSERT OR REPLACE INTO hero_stats(
            hero_type, max_health, health, speed, damage, attack_range, attack_speed, special_cooldown, defense, critical_chance, critical_damage
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)'''
        c = conn.cursor()
        for hero in heroes:
            c.execute(sql, hero)
        conn.commit()
        print('hero_stats inserted')
    except Error as e:
        print(e)

def insert_monster_stats(conn):
    try:
        monsters = [
            ('gorgon', 50, 50, 1, 8, 60, 1.5, 5, 0.05, 1.2, 10, 5),
            ('orc', 80, 80, 1, 12, 70, 1.2, 8, 0.08, 1.3, 20, 10), #future implementation
            ('skeleton', 60, 60, 1, 10, 65, 1.3, 3, 0.06, 1.4, 15, 8),
            ('demon_boss', 500, 500, 0, 25, 120, 0.8, 15, 0.12, 1.6, 100, 50)
        ]
        sql = '''INSERT OR REPLACE INTO monster_stats(
            monster_type, max_health, health, speed, damage, attack_range, attack_speed, defense, critical_chance, critical_damage, experience_value, gold_value
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)'''
        c = conn.cursor()
        for monster in monsters:
            c.execute(sql, monster)
        conn.commit()
        print('monster_stats inserted')
    except Error as e:
        print(e)

def insert_hero_animations(conn):
    try:
        # Base path for hero sprites
        base_path = "assets/sprites/heroes"
        
        animations = [
            # Knight animations
            ('knight', 'IDLE', f'{base_path}/knight/Knight_1/Knight_Idle.png', 4, 0.15, 64, 64),
            ('knight', 'WALKING', f'{base_path}/knight/Knight_1/Knight_Walk.png', 6, 0.12, 64, 64),
            ('knight', 'ATTACKING_1', f'{base_path}/knight/Knight_1/Knight_Attack1.png', 5, 0.1, 64, 64),
            ('knight', 'ATTACKING_2', f'{base_path}/knight/Knight_1/Knight_Attack2.png', 4, 0.1, 64, 64),
            ('knight', 'ATTACKING_3', f'{base_path}/knight/Knight_1/Knight_Attack3.png', 4, 0.1, 64, 64),
            ('knight', 'SPECIAL_SKILL', f'{base_path}/knight/Knight_1/Knight_Special.png', 6, 0.08, 64, 64),
            ('knight', 'DEFENDING', f'{base_path}/knight/Knight_1/Knight_Defend.png', 3, 0.2, 64, 64),
            ('knight', 'HURT', f'{base_path}/knight/Knight_1/Knight_Hurt.png', 2, 0.3, 64, 64),

            # Archer animations - UPDATE THESE LINES
            ('archer', 'IDLE', f'{base_path}/archer/Samurai_Archer/Archer_Idle.png', 4, 0.15, 64, 64),
            ('archer', 'WALKING', f'{base_path}/archer/Samurai_Archer/Archer_Walk.png', 6, 0.12, 64, 64),
            ('archer', 'ATTACKING_1', f'{base_path}/archer/Samurai_Archer/Archer_Attack.png', 5, 0.1, 64, 64),
            ('archer', 'ATTACKING_2', f'{base_path}/archer/Samurai_Archer/Archer_Attack2.png', 4, 0.1, 64, 64),
            ('archer', 'ATTACKING_3', f'{base_path}/archer/Samurai_Archer/Archer_Attack3.png', 4, 0.1, 64, 64),
            ('archer', 'SPECIAL_SKILL', f'{base_path}/archer/Samurai_Archer/Archer_Special.png', 6, 0.08, 64, 64),
            ('archer', 'DEFENDING', f'{base_path}/archer/Samurai_Archer/Archer_Defend.png', 3, 0.2, 64, 64),
            ('archer', 'HURT', f'{base_path}/archer/Samurai_Archer/Archer_Hurt.png', 2, 0.3, 64, 64),
            
            # Cleric animations
            ('cleric', 'IDLE', f'{base_path}/cleric/Fire_Cleric/Cleric_Idle.png', 4, 0.15, 64, 64),
            ('cleric', 'WALKING', f'{base_path}/cleric/Fire_Cleric/Cleric_Walk.png', 6, 0.12, 64, 64),
            ('cleric', 'ATTACKING_1', f'{base_path}/cleric/Fire_Cleric/Cleric_Attack.png', 5, 0.1, 64, 64),
            ('cleric', 'ATTACKING_2', f'{base_path}/cleric/Fire_Cleric/Cleric_Attack2.png', 4, 0.1, 64, 64),
            ('cleric', 'ATTACKING_3', f'{base_path}/cleric/Fire_Cleric/Cleric_Attack3.png', 4, 0.1, 64, 64),
            ('cleric', 'SPECIAL_SKILL', f'{base_path}/cleric/Fire_Cleric/Cleric_Special.png', 6, 0.08, 64, 64),
            ('cleric', 'DEFENDING', f'{base_path}/cleric/Fire_Cleric/Cleric_Defend.png', 3, 0.2, 64, 64),
            ('cleric', 'HURT', f'{base_path}/cleric/Fire_Cleric/Cleric_Hurt.png', 2, 0.3, 64, 64),
        ]
        
        sql = '''INSERT OR REPLACE INTO hero_animations(
            hero_type, animation_state, sprite_path, frame_count, frame_rate, frame_width, frame_height
        ) VALUES (?, ?, ?, ?, ?, ?, ?)'''
        
        c = conn.cursor()
        for animation in animations:
            c.execute(sql, animation)
        
        conn.commit()
        print('hero_animations inserted')
    except Error as e:
        print(e)

def insert_monster_animations(conn):
    try:
        # Base path for monster sprites
        base_path = "assets/sprites/monsters"
        
        animations = [
            # Goblin animations
            ('gorgon', 'idle', f'{base_path}/Gorgon_1/Idle.png', 4, 0.15, 48, 48),
            ('gorgon', 'walking', f'{base_path}/Gorgon_1/Walk.png', 6, 0.12, 48, 48),
            ('gorgon', 'attacking', f'{base_path}/Gorgon_1/Attack.png', 4, 0.1, 48, 48),
            ('gorgon', 'hurt', f'{base_path}/Gorgon_1/Hurt.png', 2, 0.3, 48, 48),
            
            # Orc animations
            ('orc', 'idle', f'{base_path}/orc/Orc_Idle.png', 4, 0.15, 64, 64),
            ('orc', 'walking', f'{base_path}/orc/Orc_Walk.png', 6, 0.12, 64, 64),
            ('orc', 'attacking', f'{base_path}/orc/Orc_Attack.png', 5, 0.1, 64, 64),
            ('orc', 'hurt', f'{base_path}/orc/Orc_Hurt.png', 2, 0.3, 64, 64),
            
            # Skeleton animations
            ('skeleton', 'idle', f'{base_path}/skeleton/Skeleton_Idle.png', 4, 0.15, 48, 48),
            ('skeleton', 'walking', f'{base_path}/skeleton/Skeleton_Walk.png', 6, 0.12, 48, 48),
            ('skeleton', 'attacking', f'{base_path}/skeleton/Skeleton_Attack.png', 4, 0.1, 48, 48),
            ('skeleton', 'hurt', f'{base_path}/skeleton/Skeleton_Hurt.png', 2, 0.3, 48, 48),
            
            # Demon Boss animations
            ('demon_boss', 'idle', f'{base_path}/demon_boss/Demon_Idle.png', 4, 0.2, 128, 128),
            ('demon_boss', 'walking', f'{base_path}/demon_boss/Demon_Walk.png', 6, 0.15, 128, 128),
            ('demon_boss', 'attacking', f'{base_path}/demon_boss/Demon_Attack.png', 6, 0.1, 128, 128),
            ('demon_boss', 'special', f'{base_path}/demon_boss/Demon_Special.png', 8, 0.08, 128, 128),
            ('demon_boss', 'hurt', f'{base_path}/demon_boss/Demon_Hurt.png', 3, 0.3, 128, 128),
        ]
        
        sql = '''INSERT OR REPLACE INTO monster_animations(
            monster_type, animation_state, sprite_path, frame_count, frame_rate, frame_width, frame_height
        ) VALUES (?, ?, ?, ?, ?, ?, ?)'''
        
        c = conn.cursor()
        for animation in animations:
            c.execute(sql, animation)
        
        conn.commit()
        print('monster_animations inserted')
    except Error as e:
        print(e)

def create_game_database():
    db_file = 'game_data.db'
    conn = create_connection(db_file)
    if conn is not None:
        create_hero_stats_table(conn)
        create_monster_stats_table(conn)
        create_hero_animations_table(conn)
        create_monster_animations_table(conn)
        insert_hero_stats(conn)
        insert_monster_stats(conn)
        insert_hero_animations(conn)
        insert_monster_animations(conn)
        print('Game database created successfully!')
        conn.close()
    else:
        print('Error! Cannot create the database connection.')

if __name__ == '__main__':
    create_game_database() 