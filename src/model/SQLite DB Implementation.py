import sqlite3
import os
from DungeonEntity import AnimationState

def initialize_database():
    """Create and initialize the game database with hero data"""

    #check if database already exists
    if os.path.exists('game_data.db'):
        print("Database already exists. Skipping initialization.")
        return

    #create a new databse
    conn = sqlite3.connect('game_data.db')
    c = conn.cursor()

    #create hero stats table
    c.execute('''
    CREATE TABLE hero_stats (
        hero_type TEXT PRIMARY KEY,
        max_health INTEGER,
        speed REAL,
        damage INTEGER,
        attack_range INTEGER,
        special_cooldown INTEGER
        )
        ''')

    #create hero_animations table
    c.execute('''
    CREATE TABLE hero_animations
    (
        id              INTEGER PRIMARY KEY AUTOINCREMENT,
        hero_type       TEXT,
        animation_state INTEGER,
        frame_count     INTEGER,
        FOREIGN KEY (hero_type) REFERENCES hero_stats (hero_type)
    )
        ''')

    #create hero sprites table
    c.execute('''
    CREATE TABLE hero_sprites
    (
        id              INTEGER PRIMARY KEY AUTOINCREMENT,
        hero_type       TEXT,
        animation_state INTEGER,
        sprite_path     TEXT,
        FOREIGN KEY (hero_type) REFERENCES hero_stats (hero_type)
    )
    ''')

    #insert hero stats ASK MOHAMMAD
    hero_stats = [
        #hero_type, max_health, speed, damage, attack_range, special_cooldown
        ('knight', 150, 6, 10,90, 15.0), #tankier but slow with high melee dmg
        ('cleric', 120, 7, 7, 75, 12.0), #Cleric is balanced
        ('archer', 100, 8, 8, 150, 10.0) #archer is fgaster with longer range attack
    ]

    c.executemany('INSERT INTO hero_stats VALUES (?,?,?,?,?,?)', hero_stats)

    #insert animation data for each hero
    animation_data = []

    #define frame counts for each hero
