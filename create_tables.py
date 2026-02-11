#!/usr/bin/env python3
"""
create_tables.py
Creates (if missing) inventory and production tables and backs up an existing DB.
"""
import sqlite3, glob, os, shutil, time, sys

def find_db_file():
    patterns = ['**/*.db', '**/*.sqlite', '**/*.sqlite3']
    candidates = []
    for p in patterns:
        candidates.extend(glob.glob(p, recursive=True))
    # ignore virtualenv files
    candidates = [c for c in candidates if '/venv/' not in c.replace("\\\\","/").lower() and '\\\\venv\\\\' not in c.lower()]
    if candidates:
        candidates.sort(key=lambda p: os.path.getmtime(p), reverse=True)
        return os.path.abspath(candidates[0])
    os.makedirs('instance', exist_ok=True)
    return os.path.abspath(os.path.join('instance', 'dl_farm.db'))

def backup_db(path):
    if os.path.exists(path):
        ts = time.strftime('%Y%m%d-%H%M%S')
        b = f"{path}.bak-{ts}"
        shutil.copy2(path, b)
        print(f"Backup created: {b}")
    else:
        print("No existing DB found; a new DB will be created at:", path)

def create_tables(conn):
    sql = """
    CREATE TABLE IF NOT EXISTS inventory (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL,
        sku TEXT,
        quantity REAL DEFAULT 0,
        unit TEXT,
        location TEXT,
        notes TEXT,
        created_at DATETIME DEFAULT CURRENT_TIMESTAMP
    );

    CREATE TABLE IF NOT EXISTS production (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        record_date TEXT,
        animal_name TEXT,
        production_type TEXT,
        quantity REAL DEFAULT 0,
        unit TEXT,
        health_status TEXT,
        notes TEXT,
        recorded_by TEXT,
        created_at DATETIME DEFAULT CURRENT_TIMESTAMP
    );

    CREATE INDEX IF NOT EXISTS idx_inventory_created_at ON inventory(created_at);
    CREATE INDEX IF NOT EXISTS idx_production_record_date ON production(record_date);
    """
    cur = conn.cursor()
    cur.executescript(sql)
    conn.commit()

def main():
    db_path = find_db_file()
    print("Using DB file:", db_path)
    backup_db(db_path)
    conn = sqlite3.connect(db_path)
    try:
        create_tables(conn)
        print("Tables created (if they did not already exist).")
    except Exception as e:
        print("Error creating tables:", e)
        sys.exit(1)
    finally:
        conn.close()
    print("Done. Restart your Flask app / WSGI workers and try the route again.")

if __name__ == '__main__':
    main()
