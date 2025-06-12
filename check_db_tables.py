import sqlite3

conn = sqlite3.connect('game_data.db')
c = conn.cursor()

print('Tables in game_data.db:')
for row in c.execute("SELECT name FROM sqlite_master WHERE type='table';"):
    print('-', row[0])

conn.close() 