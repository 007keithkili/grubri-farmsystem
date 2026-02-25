#!/usr/bin/env python3
import os, sys, sqlite3, datetime, shutil

def find_dbs(base):
    candidates = []
    for root, dirs, files in os.walk(base):
        for f in files:
            if f.lower().endswith(('.db', '.sqlite', '.sqlite3', '.db3')):
                candidates.append(os.path.abspath(os.path.join(root, f)))
    # some common locations
    maybe = [os.path.join(base,"instance","database.db"), os.path.join(base,"data.db"), os.path.join(base,"app.db")]
    for p in maybe:
        if os.path.exists(p) and p not in candidates:
            candidates.append(os.path.abspath(p))
    return candidates

def ensure_columns(db, columns):
    print("\\n----")
    print("Processing:", db)
    conn = None
    try:
        conn = sqlite3.connect(db)
        cur = conn.cursor()
        # ensure inventory table exists
        cur.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='inventory';")
        if not cur.fetchone():
            print("  SKIP: 'inventory' table not found in this DB.")
            return
        cur.execute("PRAGMA table_info(inventory);")
        existing = [r[1] for r in cur.fetchall()]
        print("  Existing columns:", existing)
        to_add = [c for c in columns if c not in existing]
        if not to_add:
            print("  OK: all requested columns already exist.")
            return
        # backup original DB
        ts = datetime.datetime.now().strftime('%Y%m%d%H%M%S')
        bak = db + f'.bak.{ts}'
        conn.close()
        conn = None
        shutil.copy2(db, bak)
        print("  Backup created:", bak)
        # reopen and add columns
        conn = sqlite3.connect(db)
        cur = conn.cursor()
        for col in to_add:
            # SQLite allows: ALTER TABLE <table> ADD COLUMN <name> <type>;
            print(f"  Adding column '{col}' (TEXT NULLABLE)...")
            cur.execute(f'ALTER TABLE inventory ADD COLUMN "{col}" TEXT;')
        conn.commit()
        # verify
        cur.execute("PRAGMA table_info(inventory);")
        newcols = [r[1] for r in cur.fetchall()]
        print("  Columns now:", newcols)
        missing_after = [c for c in columns if c not in newcols]
        if not missing_after:
            print("  SUCCESS: all requested columns present in", db)
        else:
            print("  WARNING: these columns still missing:", missing_after)
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
    cols_arg = "location,sku"
    if len(sys.argv) > 1:
        # first arg may be columns if called from PS with only columns
        cols_arg = sys.argv[1]
    # optional second arg is path
    db_arg = None
    if len(sys.argv) > 2:
        db_arg = sys.argv[2]
    columns = [c.strip() for c in cols_arg.split(",") if c.strip()]
    targets = []
    if db_arg:
        if os.path.exists(db_arg):
            targets = [os.path.abspath(db_arg)]
        else:
            print("Provided DB path does not exist:", db_arg)
            sys.exit(2)
    else:
        targets = find_dbs(base)
    if not targets:
        print("No DB files found automatically. Provide DB path as argument, e.g.:")
        print("  python add_columns_fix.py \"location,sku\" C:\\path\\to\\database.db")
        sys.exit(1)
    for db in targets:
        ensure_columns(db, columns)
    print("\\nAll done. Restart your Flask server and test the route that failed.")
