import sqlite3

conn = sqlite3.connect('game_data.db')
c = conn.cursor()

print("Fixing demon boss animation_state values to be uppercase...")
c.execute('''
    UPDATE monster_animations
    SET animation_state = UPPER(animation_state)
    WHERE monster_type = 'demon_boss'
''')
print("✓ All demon boss animation_state values are now uppercase.")

conn.commit()
conn.close() 