import sqlite3, sys
p = sys.argv[1]
sql = '''CREATE TABLE IF NOT EXISTS inventory (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  name TEXT NOT NULL,
  quantity INTEGER DEFAULT 0,
  unit TEXT,
  price REAL DEFAULT 0,
  notes TEXT,
  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);'''
try:
    conn = sqlite3.connect(p)
    conn.executescript(sql)
    conn.commit()
    print('Created/ensured inventory table in:', p)
except Exception as e:
    print('ERROR creating table in', p, ':', e)
finally:
    try: conn.close()
    except: pass
