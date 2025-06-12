import sqlite3

conn = sqlite3.connect('game_data.db')
c = conn.cursor()

print("Fixing archer idle animation in database (Samurai_Archer pack)...")
c.execute('''
    UPDATE hero_animations
    SET sprite_path = 'assets/sprites/heroes/archer/Samurai_Archer/Idle.png',
        frame_count = 9,
        frame_width = 128,
        frame_height = 128
    WHERE hero_type = 'archer' AND animation_state = 'IDLE'
''')
print("✓ Archer idle animation database entry fixed!")

conn.commit()
conn.close() 