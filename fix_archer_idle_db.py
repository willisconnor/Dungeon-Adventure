import sqlite3

conn = sqlite3.connect('game_data.db')
c = conn.cursor()

# Set the correct path, frame count, and frame size for archer idle
print("Fixing archer idle animation in database...")
c.execute('''
    UPDATE hero_animations
    SET sprite_path = 'assets/sprites/enemies/Skeleton_Archer/Idle.png',
        frame_count = 7,
        frame_width = 128,
        frame_height = 128
    WHERE hero_type = 'archer' AND animation_state = 'IDLE'
''')
print("✓ Archer idle animation database entry fixed!")

conn.commit()
conn.close() 