#!/usr/bin/env python3
import os, sys, sqlite3, shutil, re, datetime

base = os.path.abspath(os.getcwd())
print("Project base:", base)

# collect candidate DB files
candidates = []

# 1) files under project with common sqlite extensions
for root, dirs, files in os.walk(base):
    for f in files:
        if f.lower().endswith(('.db', '.sqlite', '.sqlite3', '.db3')):
            candidates.append(os.path.join(root, f))

# 2) also parse app.py for quoted db filenames
app_py = os.path.join(base, 'app.py')
if os.path.exists(app_py):
    try:
        text = open(app_py, 'r', encoding='utf-8', errors='ignore').read()
        matches = re.findall(r"['\"]([^'\"]+\.(?:db|sqlite|sqlite3|db3))['\"]", text, flags=re.IGNORECASE)
        for p in matches:
            p_abs = p if os.path.isabs(p) else os.path.normpath(os.path.join(base, p))
            if os.path.exists(p_abs) and p_abs not in candidates:
                candidates.append(p_abs)
    except Exception as e:
        print("Warning parsing app.py:", e)

# dedupe
candidates = list(dict.fromkeys(candidates))

if not candidates:
    print("No DB files found. If your app uses a DB outside project, run this script with the DB path as argument:")
    print("  python ensure_sku.py C:\\full\\path\\to\\database.db")
    sys.exit(1)

print("Candidate DB files:")
for c in candidates:
    print(" -", c)

def check_and_add_sku(db_path):
    print("\n----")
    print("Processing:", db_path)
    try:
        conn = sqlite3.connect(db_path)
        cur = conn.cursor()
        # check if inventory table exists
        cur.execute(\"SELECT name FROM sqlite_master WHERE type='table' AND name='inventory';\")
        if not cur.fetchone():
            print("  SKIP: 'inventory' table not found in this DB.")
            conn.close()
            return

        # list columns
        cur.execute(\"PRAGMA table_info(inventory);\")
        cols = cur.fetchall()
        col_names = [c[1] for c in cols]
        print("  Columns present:", col_names)

        if 'sku' in col_names:
            print("  OK: 'sku' column already exists.")
            conn.close()
            return

        # backup before change
        ts = datetime.datetime.now().strftime('%Y%m%d%H%M%S')
        bak = db_path + f'.bak.{ts}'
        print("  Creating backup:", bak)
        conn.close()
        shutil.copy2(db_path, bak)

        # add column
        conn = sqlite3.connect(db_path)
        cur = conn.cursor()
        print("  Adding 'sku' column (TEXT, NULLABLE)...")
        cur.execute(\"ALTER TABLE inventory ADD COLUMN sku TEXT;\")
        conn.commit()

        # verify
        cur.execute(\"PRAGMA table_info(inventory);\")
        cols2 = cur.fetchall()
        col_names2 = [c[1] for c in cols2]
        print("  Columns now:", col_names2)
        if 'sku' in col_names2:
            print("  SUCCESS: 'sku' added to", db_path)
        else:
            print("  FAILURE: 'sku' still missing after ALTER. See sqlite output.")
        conn.close()
    except Exception as e:
        print("  ERROR processing", db_path, ":", e)
        try:
            conn.close()
        except:
            pass

# If a path was supplied as argument, restrict to that
if len(sys.argv) > 1:
    arg = sys.argv[1]
    if os.path.exists(arg):
        check_and_add_sku(os.path.abspath(arg))
    else:
        print("Provided path does not exist:", arg)
        sys.exit(2)
else:
    for db in candidates:
        check_and_add_sku(db)

print("\\nAll done. If you changed DB(s), restart Flask and test /inventory.")
