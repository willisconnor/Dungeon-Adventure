import sqlite3

conn = sqlite3.connect('game_data.db')
c = conn.cursor()

print("Deleting demon boss 'attacking' animation_state rows in monster_animations...")
c.execute('''
    DELETE FROM monster_animations
    WHERE monster_type = 'demon_boss' AND animation_state = 'attacking'
''')
print("✓ Deleted any 'attacking' rows for demon boss.")

conn.commit()
conn.close() 