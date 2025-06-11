import sqlite3

conn = sqlite3.connect('game_data.db')
cursor = conn.cursor()

# Check hero speeds
print("Current hero speeds:")
cursor.execute("SELECT hero_type, speed FROM hero_stats")
heroes = cursor.fetchall()
for hero in heroes:
    print(f"- {hero[0]}: {hero[1]}")

print("\nCurrent monster speeds:")
cursor.execute("SELECT monster_type, speed FROM monster_stats")
monsters = cursor.fetchall()
for monster in monsters:
    print(f"- {monster[0]}: {monster[1]}")

conn.close() 