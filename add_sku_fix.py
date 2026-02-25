#!/usr/bin/env python3
import os, sys, sqlite3, datetime, shutil

def find_dbs(base):
    candidates = []
    for root, dirs, files in os.walk(base):
        for f in files:
            if f.lower().endswith(('.db', '.sqlite', '.sqlite3', '.db3')):
                candidates.append(os.path.abspath(os.path.join(root, f)))
    # Also check common instance/data locations
    maybe = [os.path.join(base,"instance","database.db"), os.path.join(base,"data.db"), os.path.join(base,"app.db")]
    for p in maybe:
        if os.path.exists(p) and p not in candidates:
            candidates.append(os.path.abspath(p))
    return candidates

def process(db):
    print("\\n----")
    print("Processing:", db)
    conn = None
    try:
        conn = sqlite3.connect(db)
        cur = conn.cursor()
        # check inventory table exists
        cur.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='inventory';")
        if not cur.fetchone():
            print("  SKIP: 'inventory' table not found in this DB.")
            return
        cur.execute("PRAGMA table_info(inventory);")
        cols = [r[1] for r in cur.fetchall()]
        print("  Columns present:", cols)
        if 'sku' in cols:
            print("  OK: 'sku' column already exists.")
            return
        # backup
        ts = datetime.datetime.now().strftime('%Y%m%d%H%M%S')
        bak = db + f'.bak.{ts}'
        conn.close()
        conn = None
        shutil.copy2(db, bak)
        print("  Backup created:", bak)
        # add column
        conn = sqlite3.connect(db)
        cur = conn.cursor()
        print("  Adding 'sku' column (TEXT, NULLABLE)...")
        cur.execute("ALTER TABLE inventory ADD COLUMN sku TEXT;")
        conn.commit()
        # verify
        cur.execute("PRAGMA table_info(inventory);")
        cols2 = [r[1] for r in cur.fetchall()]
        print("  Columns now:", cols2)
        if 'sku' in cols2:
            print("  SUCCESS: 'sku' added to", db)
        else:
            print("  FAILURE: 'sku' still missing after ALTER.")
    except Exception as e:
        print("  ERROR processing", db, ":", e)
    finally:
        try:
            if conn:
                conn.close()
        except:
            pass

if __name__ == "__main__":
    base = os.path.abspath(os.getcwd())
    targets = []
    # if a DB path arg provided, use only that
    if len(sys.argv) > 1:
        arg = sys.argv[1]
        if os.path.exists(arg):
            targets = [os.path.abspath(arg)]
        else:
            print("Provided path does not exist:", arg)
            sys.exit(2)
    else:
        targets = find_dbs(base)
    if not targets:
        print("No DB files found automatically. Provide DB path as argument, e.g.:")
        print("  python add_sku_fix.py C:\\path\\to\\database.db")
        sys.exit(1)
    for db in targets:
        process(db)
    print("\\nAll done. Restart your Flask server and test /inventory.")
