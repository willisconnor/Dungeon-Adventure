import sqlite3

conn = sqlite3.connect('game_data.db')
cursor = conn.cursor()

# Check tables
cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
tables = cursor.fetchall()
print("Tables in database:")
for table in tables:
    print(f"- {table[0]}")

# Check hero_animations table specifically
try:
    cursor.execute("SELECT COUNT(*) FROM hero_animations")
    count = cursor.fetchone()[0]
    print(f"\nhero_animations table has {count} rows")
    
    cursor.execute("SELECT hero_type, animation_state FROM hero_animations LIMIT 5")
    rows = cursor.fetchall()
    print("Sample hero_animations data:")
    for row in rows:
        print(f"- {row[0]}: {row[1]}")
except Exception as e:
    print(f"Error checking hero_animations: {e}")

conn.close() 