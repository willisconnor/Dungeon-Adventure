import sqlite3

conn = sqlite3.connect('game_data.db')
c = conn.cursor()

print("Fixing archer running animation in database (Samurai_Archer pack)...")
c.execute('''
    UPDATE hero_animations
    SET sprite_path = 'assets/sprites/heroes/archer/Samurai_Archer/Run.png',
        frame_count = 8,
        frame_width = 128,
        frame_height = 128
    WHERE hero_type = 'archer' AND animation_state = 'RUNNING'
''')
print("✓ Archer running animation database entry fixed!")

conn.commit()
conn.close() 