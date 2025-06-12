import sqlite3

conn = sqlite3.connect('game_data.db')
c = conn.cursor()

print("Switching archer running animation to Walk.png (Samurai_Archer pack)...")
c.execute('''
    UPDATE hero_animations
    SET sprite_path = 'assets/sprites/heroes/archer/Samurai_Archer/Walk.png',
        frame_count = 16,
        frame_width = 128,
        frame_height = 128
    WHERE hero_type = 'archer' AND animation_state = 'RUNNING'
''')
print("✓ Archer running animation now uses Walk.png!")

conn.commit()
conn.close() 