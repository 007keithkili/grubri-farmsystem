# add_task_columns.py
import sqlite3
from pathlib import Path

DB = Path(__file__).parent / 'database' / 'farm.db'

def add_columns():
    conn = sqlite3.connect(str(DB))
    cursor = conn.cursor()
    cursor.execute("PRAGMA table_info(task)")
    cols = {row[1] for row in cursor.fetchall()}

    if 'priority' not in cols:
        cursor.execute("ALTER TABLE task ADD COLUMN priority TEXT DEFAULT 'Normal'")
        print("Added 'priority' column")

    if 'category' not in cols:
        cursor.execute("ALTER TABLE task ADD COLUMN category TEXT DEFAULT 'general'")
        print("Added 'category' column")

    conn.commit()
    conn.close()

if __name__ == '__main__':
    add_columns()
