import sqlite3, os, sys

# change this if your DB file is in a different location
db = os.path.join(os.getcwd(), "database", "farm.db")

print("Checking DB path:", db)

if not os.path.exists(db):
    print("WARNING: DB file not found at this path.")
    print("If your DB is elsewhere, either move it to 'database/farm.db' or edit this script to point to the correct path.")
    sys.exit(2)

try:
    conn = sqlite3.connect(db)
    cur = conn.cursor()

    # integrity
    ok = cur.execute("PRAGMA integrity_check").fetchone()
    print("\\nPRAGMA integrity_check ->", ok)

    # list tables
    tables = [r[0] for r in cur.execute("SELECT name FROM sqlite_master WHERE type='table' ORDER BY name")]
    print("\\nTables found (%d): %s" % (len(tables), tables))

    # show schema for key tables (adjust list if you want other tables)
    key_tables = ['production','inventory','sale','livestock','user','staff']
    for t in key_tables:
        if t in tables:
            print("\\n--- Schema for table: %s ---" % t)
            rows = cur.execute("PRAGMA table_info('%s')" % t).fetchall()
            # print column info in readable form
            if rows:
                print("cid | name | type | notnull | dflt_value | pk")
                for r in rows:
                    print("%s | %s | %s | %s | %s | %s" % (r[0], r[1], r[2], r[3], r[4], r[5]))
            else:
                print("(no columns returned)")
        else:
            print("\\n--- Table NOT PRESENT: %s ---" % t)

    # optionally show a couple rows from production to check data shape (non-destructive)
    if 'production' in tables:
        print("\\nSample rows from production (up to 5):")
        try:
            for r in cur.execute("SELECT * FROM production LIMIT 5"):
                print(r)
        except Exception as e:
            print("Could not SELECT from production (maybe missing columns):", e)

    conn.close()
    print("\\nDB diagnostic finished successfully.")
    sys.exit(0)

except Exception as e:
    print("\\nDB error:", e)
    try:
        conn.close()
    except:
        pass
    sys.exit(3)
