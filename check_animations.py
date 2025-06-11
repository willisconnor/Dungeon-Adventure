import sqlite3

conn = sqlite3.connect('game_data.db')
cursor = conn.cursor()

# Check all animation states in the database
cursor.execute("SELECT DISTINCT animation_state FROM hero_animations ORDER BY animation_state")
states = cursor.fetchall()
print("Animation states in database:")
for state in states:
    print(f"- '{state[0]}'")

conn.close() 