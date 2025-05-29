import sqlite3
import os
from src.model.DungeonEntity import AnimationState

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
    animation_data = [
        #knight animations
        ('knight', AnimationState.IDLE.value, 4),
        ('knight', AnimationState.WALKING.value, 8),
        ('knight', AnimationState.ATTACKING_1.value, 5),
        ('knight', AnimationState.ATTACKING_2.value, 4),
        ('knight', AnimationState.ATTACKING_3.value, 4),
        ('knight', AnimationState.HURT.value, 2),
        ('knight', AnimationState.DEAD.value, 6),
        #special skill block
        ('knight', AnimationState.SPECIAL_SKILL.value, 5),

        #archer animations
        ('archer', AnimationState.IDLE.value, 9),
        ('archer', AnimationState.WALKING.value, 8),
        #each attack is a shot
        ('archer', AnimationState.ATTACKING_1.value, 14),
        ('archer', AnimationState.ATTACKING_2.value, 14),
        ('archer', AnimationState.ATTACKING_3.value, 14),
        ('archer', AnimationState.HURT.value, 3),
        ('archer', AnimationState.DEAD.value, 5),
        #Deflect special attack, define in hero class
        ('archer', AnimationState.SPECIAL_SKILL.value, 6),
        #possibly store arrow sprite here
        ('archer', AnimationState.ARROW.value, 1),

        # Cleric animations
        ('cleric', AnimationState.IDLE.value, 7),
        ('cleric', AnimationState.WALKING.value, 8),
        ('cleric', AnimationState.ATTACKING_1.value, 4),
        ('cleric', AnimationState.ATTACKING_2.value, 4),
        #no attack 3
        ('cleric', AnimationState.HURT.value, 3),
        ('cleric', AnimationState.DEAD.value, 6),
        #fireball by pitbull starts playing
        ('cleric', AnimationState.SPECIAL_SKILL.value, 8),
        #store projectile sprites here?
        ('cleric', AnimationState.FIREBALL.value, 12)
    ]

    c.executemany('INSERT INTO hero_animations VALUES (NULL,?,?,?)', animation_data)

    #Insert sprite paths for each hero and animation state
    #Format: hero_type, anmimation_state.value, sprite_path

    sprite_paths = [
        # Knight sprite paths
        ('knight', AnimationState.IDLE.value, 'assets/sprites/heroes/Knight_1/knight/Idle.png'),
        ('knight', AnimationState.WALKING.value, 'assets/sprites/heroes/Knight_1/knight/walk.png'),
        ('knight', AnimationState.ATTACKING_1.value, 'assets/sprites/heroes/Knight_1/knight/Attack 1.png'),
        ('knight', AnimationState.ATTACKING_2.value, 'assets/sprites/heroes/Knight_1/knight/Attack 2.png'),
        ('knight', AnimationState.ATTACKING_3.value, 'assets/sprites/heroes/Knight_1/knight/Attack 3.png'),
        ('knight', AnimationState.HURT.value, 'assets/sprites/heroes/Knight_1/knight/Hurt.png'),
        ('knight', AnimationState.DEAD.value, 'assets/sprites/heroes/knight/Knight_1/Dead.png'),
        ('knight', AnimationState.SPECIAL_SKILL.value, 'assets/sprites/heroes/knight/Knight_1/Defend.png'),
        ('knight', AnimationState.RUNNING.value, 'assets/sprites/heroes/knight/Knight_1/Run.png'),
        ('knight', AnimationState.JUMPING.value, 'assets/sprites/heroes/knight/Knight_1/Jump.png'),
        ('knight', AnimationState.RUNNING_ATTACK.value, 'assets/sprites/heroes/knight/Knight_1/Run+Attack.png'),

        # Archer sprite paths
        ('archer', AnimationState.IDLE.value, 'assets/sprites/heroes/archer/Samurai_Archer/Walk.png'),
        ('archer', AnimationState.WALKING.value, 'assets/sprites/heroes/archer/Samurai_Archer/Run.png'),
        ('archer', AnimationState.ATTACKING_1.value, 'assets/sprites/heroes/archer/Samurai_Archer/Shot.png'),
        ('archer', AnimationState.ATTACKING_2.value, 'assets/sprites/heroes/archer/Samurai_Archer/Shot.png'),
        ('archer', AnimationState.ATTACKING_3.value, 'assets/sprites/heroes/archer/Samurai_Archer/Shot.png'),
        ('archer', AnimationState.HURT.value, 'assets/sprites/heroes/archer/Samurai_Archer/Hurt.png'),
        ('archer', AnimationState.DEAD.value, 'assets/sprites/heroes/archer/Samurai_Archer/Dead.png'),
        ('archer', AnimationState.SPECIAL_SKILL.value, 'assets/sprites/heroes/archer/Samurai_Archer/Attack_1.png'),
        ('archer', AnimationState.ARROW.value, 'assets/sprites/heroes/archer/Samurai_Archer/Arrow.png'),
        ('archer', AnimationState.RUNNING.value, 'assets/sprites/heroes/archer/Samurai_Archer/Run.png'),
        ('archer', AnimationState.JUMPING.value, 'assets/sprites/heroes/archer/Samurai_Archer/Jump.png'),
        #('archer', AnimationState.RUNNING_ATTACK.value, 'assets/sprites/heroes/knight/Knight_1/Run+Attack.png'),

        # Cleric sprite paths
        ('cleric', AnimationState.IDLE.value, 'assets/sprites/heroes/cleric/Fire_Cleric/Idle.png'),
        ('cleric', AnimationState.WALKING.value, 'assets/sprites/heroes/cleric/Fire_Cleric/Walk.png'),
        ('cleric', AnimationState.ATTACKING_1.value, 'assets/sprites/heroes/cleric/Fire_Cleric/Attack_1.png'),
        ('cleric', AnimationState.ATTACKING_2.value, 'assets/sprites/heroes/cleric/Fire_Cleric/Attack_2.png'),
        ('cleric', AnimationState.HURT.value, 'assets/sprites/heroes/cleric/Fire_Cleric/Hurt.png'),
        ('cleric', AnimationState.DEAD.value, 'assets/sprites/heroes/cleric/Fire_Cleric/Dead.png'),
        ('cleric', AnimationState.SPECIAL_SKILL.value, 'assets/sprites/heroes/cleric/Fire_Cleric/Fireball.png'),
        ('cleric', AnimationState.FIREBALL.value, 'assets/sprites/heroes/cleric/Fire_Cleric/Charge.png'),
        ('cleric', AnimationState.RUNNING.value, 'assets/sprites/heroes/cleric/Fire_Cleric/Run.png'),
        ('cleric', AnimationState.JUMPING.value, 'assets/sprites/heroes/cleric/Fire_Cleric/Jump.png'),
        #('cleric', AnimationState.RUNNING_ATTACK.value, 'assets/sprites/heroes/knight/Knight_1/Run+Attack.png')

    ]

    c.executemany('INSERT INTO hero_sprites VALUES (NULL,?,?,?)', sprite_paths)

    #create enemy stats table
    c.execute('''
              CREATE TABLE enemy_stats
              (
                  enemy_type   TEXT PRIMARY KEY,
                  max_health   INTEGER,
                  speed        REAL,
                  damage       INTEGER,
                  attack_range INTEGER
              )
              ''')

    # Create enemy animations table
    c.execute('''
              CREATE TABLE enemy_animations
              (
                  id              INTEGER PRIMARY KEY AUTOINCREMENT,
                  enemy_type      TEXT,
                  animation_state INTEGER,
                  frame_count     INTEGER,
                  FOREIGN KEY (enemy_type) REFERENCES enemy_stats (enemy_type)
              )
              ''')

    # Create enemy sprites table
    c.execute('''
              CREATE TABLE enemy_sprites
              (
                  id              INTEGER PRIMARY KEY AUTOINCREMENT,
                  enemy_type      TEXT,
                  animation_state INTEGER,
                  sprite_path     TEXT,
                  FOREIGN KEY (enemy_type) REFERENCES enemy_stats (enemy_type)
              )
              ''')

    # Insert enemy stats
    enemy_stats = [
        # enemy_type, max_health, speed, damage, attack_range
        ('Skeleton_Archer', 80, 5, 8, 70),
        ('Skeleton_Spearman', 80, 5, 8, 70),
        ('Skeleton_Warrior', 80, 5, 8, 70),
        ('Gorgon_1', 100, 4, 10, 75),
        ('Gorgon_2', 100, 4, 10, 75),
        ('Gorgon_3', 100, 4, 10, 75)
    ]

    #will need separate handling for boss demon thingy

    c.executemany('INSERT INTO enemy_stats VALUES (?, ?, ?, ?, ?)', enemy_stats)

    # Insert enemy animation data
    enemy_animation_data = []

    # Basic animation frames for all enemies
    for enemy_type in ['Skeleton_Archer', 'Skeleton_Spearman', 'Skeleton_Warrior', 'Gorgon_1', 'Gorgon_2', 'Gorgon_3']:
        enemy_animation_data.extend([
            (enemy_type, AnimationState.IDLE.value, 4),
            (enemy_type, AnimationState.WALKING.value, 6),
            (enemy_type, AnimationState.ATTACKING_1.value, 5),
            (enemy_type, AnimationState.HURT.value, 3),
            (enemy_type, AnimationState.DYING.value, 5),
            (enemy_type, AnimationState.DEAD.value, 1)
        ])

    c.executemany('INSERT INTO enemy_animations VALUES (NULL, ?, ?, ?)', enemy_animation_data)

    # Insert enemy sprite paths
    enemy_sprite_paths = []

    # Generate sprite paths for each enemy type and animation state
    for enemy_type in ['Skeleton_Archer', 'Skeleton_Spearman', 'Skeleton_Warrior', 'Gorgon_1', 'Gorgon_2', 'Gorgon_3']:
        enemy_sprite_paths.extend([
            (enemy_type, AnimationState.IDLE.value, f'assets/sprites/enemies/{enemy_type}/idle_sheet.png'),
            (enemy_type, AnimationState.WALKING.value, f'assets/sprites/enemies/{enemy_type}/walking_sheet.png'),
            (enemy_type, AnimationState.ATTACKING_1.value, f'assets/sprites/enemies/{enemy_type}/attack_sheet.png'),
            (enemy_type, AnimationState.HURT.value, f'assets/sprites/enemies/{enemy_type}/hurt_sheet.png'),
            (enemy_type, AnimationState.DYING.value, f'assets/sprites/enemies/{enemy_type}/dying_sheet.png'),
            (enemy_type, AnimationState.DEAD.value, f'assets/sprites/enemies/{enemy_type}/dead_sheet.png')
        ])

    #Add boss sprite


    c.executemany('INSERT INTO enemy_sprites VALUES (NULL, ?, ?, ?)', enemy_sprite_paths)

    # Commit changes and close connection
    conn.commit()
    conn.close()

    print("Database initialization completed successfully!")


if __name__ == "__main__":
    initialize_database()