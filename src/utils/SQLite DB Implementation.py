import sqlite3
from sqlite3 import Error
import os
from src.model.DungeonEntity import AnimationState


def create_connection(db_file):
    """ Create a database connection to the SQLite database
    :param db_file: database file
    :return: Connection object or None
    """
    conn = None
    try:
        conn = sqlite3.connect(db_file)
        return conn
    except Error as e:
        print(f"Error connecting to database: {e}")
    return conn


def create_table(conn, create_table_sql):
    """ Create a table from the create_table_sql statement
    :param conn: Connection object
    :param create_table_sql: a CREATE TABLE SQL statement
    :return: None
    """
    try:
        c = conn.cursor()
        c.execute(create_table_sql)
    except Error as e:
        print(f"Error creating table: {e}")


def insert_data(conn, sql, data):
    """ Insert data into the database
    :param conn: Connection object
    :param sql: INSERT SQL statement
    :param data: Data to insert (tuple or list of tuples)
    :return: None
    """
    try:
        cur = conn.cursor()
        if isinstance(data[0], tuple):
            cur.executemany(sql, data)
        else:
            cur.execute(sql, data)
        conn.commit()
    except Error as e:
        print(f"Error inserting data: {e}")


def initialize_database():
    """Create and initialize the game database with hero and enemy data"""

    db_file = 'game_data.db.sql'

    # Check if database already exists and has data
    if os.path.exists(db_file):
        conn = create_connection(db_file)
        if conn is not None:
            try:
                cur = conn.cursor()
                cur.execute("SELECT count(*) FROM hero_stats")
                has_data = cur.fetchone()[0] > 0

                if has_data:
                    print("Database already initialized with data. Skipping initialization.")
                    conn.close()
                    return
            except:
                # If table doesn't exist, we'll create it below
                pass
            conn.close()

    # Create new database connection
    conn = create_connection(db_file)
    if conn is None:
        print("Error! Cannot create the database connection.")
        return

    # Try to import schema from SQL file
    try:
        # Try multiple possible locations for the SQL file
        possible_paths = [
            os.path.join('src', 'utils', 'game_data.db.sql'),
            os.path.join('utils', 'game_data.db.sql'),
            'game_data.db.sql'
        ]
        
        sql_script = None
        for path in possible_paths:
            if os.path.exists(path):
                with open(path, 'r') as sql_file:
                    sql_script = sql_file.read()
                break
        
        if sql_script is None:
            raise IOError("Could not find game_data.db.sql in any expected location")
            
        # Execute the SQL script
        conn.executescript(sql_script)
        print(f"Database schema created from SQL file successfully.")
        
    except (Error, IOError) as e:
        print(f"Error importing SQL schema: {e}")
        # Continue with fallback...
        print("Falling back to manual table creation.")

        # SQL to create hero stats table
        hero_stats_table = '''
                           CREATE TABLE hero_stats \
                           ( \
                               hero_type        TEXT PRIMARY KEY, \
                               max_health       INTEGER, \
                               speed            REAL, \
                               damage           INTEGER, \
                               attack_range     INTEGER, \
                               special_cooldown INTEGER
                           ) \
                           '''

        # SQL to create hero animations table
        hero_animations_table = '''
                                CREATE TABLE hero_animations \
                                ( \
                                    id              INTEGER PRIMARY KEY AUTOINCREMENT, \
                                    hero_type       TEXT, \
                                    animation_state INTEGER, \
                                    frame_count     INTEGER, \
                                    FOREIGN KEY (hero_type) REFERENCES hero_stats (hero_type)
                                ) \
                                '''

        # SQL to create hero sprites table
        hero_sprites_table = '''
                             CREATE TABLE hero_sprites \
                             ( \
                                 id              INTEGER PRIMARY KEY AUTOINCREMENT, \
                                 hero_type       TEXT, \
                                 animation_state INTEGER, \
                                 sprite_path     TEXT, \
                                 FOREIGN KEY (hero_type) REFERENCES hero_stats (hero_type)
                             ) \
                             '''

        # SQL to create enemy stats table
        enemy_stats_table = '''
                            CREATE TABLE enemy_stats \
                            ( \
                                enemy_type   TEXT PRIMARY KEY, \
                                max_health   INTEGER, \
                                speed        REAL, \
                                damage       INTEGER, \
                                attack_range INTEGER
                            ) \
                            '''

        # SQL to create enemy animations table
        enemy_animations_table = '''
                                 CREATE TABLE enemy_animations \
                                 ( \
                                     id              INTEGER PRIMARY KEY AUTOINCREMENT, \
                                     enemy_type      TEXT, \
                                     animation_state INTEGER, \
                                     frame_count     INTEGER, \
                                     FOREIGN KEY (enemy_type) REFERENCES enemy_stats (enemy_type)
                                 ) \
                                 '''

        # SQL to create enemy sprites table
        enemy_sprites_table = '''
                              CREATE TABLE enemy_sprites \
                              ( \
                                  id              INTEGER PRIMARY KEY AUTOINCREMENT, \
                                  enemy_type      TEXT, \
                                  animation_state INTEGER, \
                                  sprite_path     TEXT, \
                                  FOREIGN KEY (enemy_type) REFERENCES enemy_stats (enemy_type)
                              ) \
                              '''

        # Create tables
        tables = [
            hero_stats_table,
            hero_animations_table,
            hero_sprites_table,
            enemy_stats_table,
            enemy_animations_table,
            enemy_sprites_table
        ]

        for table in tables:
            create_table(conn, table)

    # Insert initial data
    insert_initial_data(conn)

    # Close connection
    conn.close()
    print("Database initialization completed successfully!")


def insert_initial_data(conn):
    """Insert initial data into the database tables"""
    # Insert hero stats data
    hero_stats = [
        # hero_type, max_health, speed, damage, attack_range, special_cooldown
        ('knight', 150, 6, 10, 90, 15.0),  # tankier but slow with high melee dmg
        ('cleric', 120, 7, 7, 75, 12.0),  # Cleric is balanced
        ('archer', 100, 8, 8, 150, 10.0)  # archer is faster with longer range attack
    ]

    insert_data(conn, 'INSERT INTO hero_stats VALUES (?,?,?,?,?,?)', hero_stats)

    # Insert animation data for each hero
    animation_data = [
        # knight animations
        ('knight', AnimationState.IDLE.value, 4),
        ('knight', AnimationState.WALKING.value, 8),
        ('knight', AnimationState.ATTACKING_1.value, 5),
        ('knight', AnimationState.ATTACKING_2.value, 4),
        ('knight', AnimationState.ATTACKING_3.value, 4),
        ('knight', AnimationState.HURT.value, 2),
        ('knight', AnimationState.DEAD.value, 6),
        ('knight', AnimationState.SPECIAL_SKILL.value, 5),

        # archer animations
        ('archer', AnimationState.IDLE.value, 9),
        ('archer', AnimationState.WALKING.value, 8),
        ('archer', AnimationState.ATTACKING_1.value, 14),
        ('archer', AnimationState.ATTACKING_2.value, 14),
        ('archer', AnimationState.ATTACKING_3.value, 14),
        ('archer', AnimationState.HURT.value, 3),
        ('archer', AnimationState.DEAD.value, 5),
        ('archer', AnimationState.SPECIAL_SKILL.value, 6),
        ('archer', AnimationState.ARROW.value, 1),

        # Cleric animations
        ('cleric', AnimationState.IDLE.value, 7),
        ('cleric', AnimationState.WALKING.value, 8),
        ('cleric', AnimationState.ATTACKING_1.value, 4),
        ('cleric', AnimationState.ATTACKING_2.value, 4),
        ('cleric', AnimationState.HURT.value, 3),
        ('cleric', AnimationState.DEAD.value, 6),
        ('cleric', AnimationState.SPECIAL_SKILL.value, 8),
        ('cleric', AnimationState.FIREBALL.value, 12)
    ]

    insert_data(conn, 'INSERT INTO hero_animations VALUES (NULL,?,?,?)', animation_data)

    # Insert sprite paths for each hero and animation state
    sprite_paths = [
        # Knight sprite paths
        ('knight', AnimationState.IDLE.value, 'assets/sprites/heroes/Knight_1/knight/Idle.png'),
        ('knight', AnimationState.WALKING.value, 'assets/sprites/heroes/Knight_1/knight/walk.png'),
        ('knight', AnimationState.ATTACKING_1.value, 'assets/sprites/heroes/Knight_1/knight/Attack 1.png'),
        ('knight', AnimationState.ATTACKING_2.value, 'assets/sprites/heroes/Knight_1/knight/Attack 2.png'),
        ('knight', AnimationState.ATTACKING_3.value, 'assets/sprites/heroes/Knight_1/knight/Attack 3.png'),
        ('knight', AnimationState.HURT.value, 'assets/sprites/heroes/Knight_1/knight/Hurt.png'),
        ('knight', AnimationState.DEAD.value, 'assets/sprites/heroes/Knight_1/knight/Dead.png'),
        ('knight', AnimationState.SPECIAL_SKILL.value, 'assets/sprites/heroes/Knight_1/knight/Defend.png'),
        ('knight', AnimationState.RUNNING.value, 'assets/sprites/heroes/Knight_1/knight/Run.png'),
        ('knight', AnimationState.JUMPING.value, 'assets/sprites/heroes/Knight_1/knight/Jump.png'),
        ('knight', AnimationState.RUNNING_ATTACK.value, 'assets/sprites/heroes/Knight_1/knight/Run+Attack.png'),

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
    ]

    insert_data(conn, 'INSERT INTO hero_sprites VALUES (NULL,?,?,?)', sprite_paths)

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

    insert_data(conn, 'INSERT INTO enemy_stats VALUES (?, ?, ?, ?, ?)', enemy_stats)

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

    insert_data(conn, 'INSERT INTO enemy_animations VALUES (NULL, ?, ?, ?)', enemy_animation_data)

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

    insert_data(conn, 'INSERT INTO enemy_sprites VALUES (NULL, ?, ?, ?)', enemy_sprite_paths)


# Helper functions for retrieving data from the database
def get_hero_stats(hero_type):
    """Get stats for a specific hero type
    :param hero_type: Type of hero (knight, archer, cleric)
    :return: Dictionary with hero stats
    """
    conn = create_connection('game_data.db')
    if conn is None:
        return None

    try:
        cur = conn.cursor()
        cur.execute("SELECT * FROM hero_stats WHERE hero_type = ?", (hero_type,))
        row = cur.fetchone()

        if row:
            return {
                'hero_type': row[0],
                'max_health': row[1],
                'speed': row[2],
                'damage': row[3],
                'attack_range': row[4],
                'special_cooldown': row[5]
            }
        return None
    except Error as e:
        print(f"Error retrieving hero stats: {e}")
        return None
    finally:
        conn.close()


def get_animation_data(entity_type, is_hero=True):
    """Get animation data for a specific entity
    :param entity_type: Type of entity (hero or enemy type)
    :param is_hero: True if entity is a hero, False if enemy
    :return: Dictionary with animation states and frame counts
    """
    conn = create_connection('game_data.db')
    if conn is None:
        return None

    table = "hero_animations" if is_hero else "enemy_animations"
    column = "hero_type" if is_hero else "enemy_type"

    try:
        cur = conn.cursor()
        cur.execute(f"SELECT animation_state, frame_count FROM {table} WHERE {column} = ?",
                    (entity_type,))
        rows = cur.fetchall()

        if rows:
            return {row[0]: row[1] for row in rows}
        return {}
    except Error as e:
        print(f"Error retrieving animation data: {e}")
        return {}
    finally:
        conn.close()


def get_sprite_path(entity_type, animation_state, is_hero=True):
    """Get sprite path for a specific entity and animation state
    :param entity_type: Type of entity (hero or enemy type)
    :param animation_state: The animation state value
    :param is_hero: True if entity is a hero, False if enemy
    :return: Path to the sprite sheet
    """
    conn = create_connection('game_data.db')
    if conn is None:
        return None

    table = "hero_sprites" if is_hero else "enemy_sprites"
    column = "hero_type" if is_hero else "enemy_type"

    try:
        cur = conn.cursor()
        cur.execute(f"SELECT sprite_path FROM {table} WHERE {column} = ? AND animation_state = ?",
                    (entity_type, animation_state))
        row = cur.fetchone()

        if row:
            return row[0]
        return None
    except Error as e:
        print(f"Error retrieving sprite path: {e}")
        return None
    finally:
        conn.close()


if __name__ == "__main__": # Initialize database
    initialize_database()

    # Then test a query
    hero = get_hero_stats("knight")
    if hero:
        print(f"Successfully retrieved knight data: {hero}")
    else:
        print("Failed to retrieve knight data")

    # Test animation data retrieval
    animations = get_animation_data("knight")
    if animations:
        print(f"Successfully retrieved knight animations: {animations}")
    else:
        print("Failed to retrieve knight animations")
