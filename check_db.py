import sqlite3, sys
p = sys.argv[1]
try:
    conn = sqlite3.connect(p)
    cur = conn.cursor()
    cur.execute("SELECT name FROM sqlite_master WHERE type=\'table\' AND name=\'inventory\';")
    exists = cur.fetchone() is not None
    conn.close()
    print(f"{p} -> inventory exists: {exists}")
except Exception as e:
    print(f"{p} -> ERROR: {e}")
