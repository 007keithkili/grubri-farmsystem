import sqlite3
from pathlib import Path

DB = Path(__file__).parent.parent / 'database' / 'farm.db'

if not DB.exists():
    print("ERROR: database not found at", DB)
    raise SystemExit(1)

conn = sqlite3.connect(str(DB))
cur = conn.cursor()

# check columns
cur.execute("PRAGMA table_info(staff)")
cols = [r[1] for r in cur.fetchall()]
if 'id_number' in cols:
    print("Column id_number already exists - nothing to do.")
else:
    try:
        cur.execute("ALTER TABLE staff ADD COLUMN id_number TEXT")
        conn.commit()
        print("Added column id_number to staff table.")
    except Exception as e:
        print("Error adding column:", e)

conn.close()
