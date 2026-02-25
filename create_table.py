import sqlite3, sys, os
p = sys.argv[1]
sql = """CREATE TABLE IF NOT EXISTS inventory (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  name TEXT NOT NULL,
  quantity INTEGER DEFAULT 0,
  unit TEXT,
  price REAL DEFAULT 0,
  notes TEXT,
  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);"""
try:
    # ensure directory exists
    os.makedirs(os.path.dirname(os.path.abspath(p)), exist_ok=True)
    conn = sqlite3.connect(p)
    conn.executescript(sql)
    conn.commit()
    conn.close()
    print(f"CREATED/ENSURED inventory in: {p}")
except Exception as e:
    print(f"ERROR creating inventory in {p}: {e}")
