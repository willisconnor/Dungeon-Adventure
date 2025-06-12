import sqlite3

conn = sqlite3.connect('game_data.db')
c = conn.cursor()

print("Deleting lowercase duplicate animation_state rows for demon_boss...")
# Find all lowercase states that have an uppercase duplicate
c.execute('''
    DELETE FROM monster_animations
    WHERE monster_type = 'demon_boss'
      AND animation_state = LOWER(animation_state)
      AND animation_state != UPPER(animation_state)
      AND EXISTS (
        SELECT 1 FROM monster_animations AS m2
        WHERE m2.monster_type = 'demon_boss'
          AND m2.animation_state = UPPER(monster_animations.animation_state)
      )
''')
print("✓ Deleted lowercase duplicate rows.")

conn.commit()
conn.close() 