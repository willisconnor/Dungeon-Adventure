import sqlite3

conn = sqlite3.connect('game_data.db')
c = conn.cursor()

print("Fixing demon boss attack animation state in database...")
c.execute('''
    UPDATE monster_animations
    SET animation_state = 'ATTACKING_1'
    WHERE monster_type = 'demon_boss' AND animation_state = 'attacking'
''')
print("✓ Demon boss attack animation state fixed!")

conn.commit()
conn.close() 