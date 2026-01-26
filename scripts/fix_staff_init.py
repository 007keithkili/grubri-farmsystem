import re, os, shutil, datetime, sys

APP = "app.py"
if not os.path.exists(APP):
    print("ERROR: app.py not found in", os.getcwd())
    sys.exit(2)

# create timestamped backup
bak = APP + ".bak." + datetime.datetime.now().strftime("%Y%m%d%H%M%S")
shutil.copy2(APP, bak)
print("Backup created at", bak)

text = open(APP, "r", encoding="utf-8").read()
orig = text

# find def tasks(...) line
m = re.search(r'(def\s+tasks\s*\([^)]*\)\s*:\s*\n)', text, flags=re.MULTILINE)
if not m:
    print("ERROR: def tasks(...) not found in app.py. Aborting.")
    sys.exit(1)

start = m.end()
snippet = text[start:start+2000]
if "staff_list" in snippet:
    print("staff_list already present near tasks(); skipping insertion.")
else:
    insert_block = (
        "    # Ensure staff_list exists (auto-patch)\n"
        "    staff_list = []\n"
        "    try:\n"
        "        if 'get_db_connection' in globals() or 'get_db_connection' in locals():\n"
        "            conn = get_db_connection()\n"
        "            cur = conn.cursor()\n"
        "            cur.execute(\"SELECT id, first_name, last_name FROM staff ORDER BY first_name\")\n"
        "            staff_list = cur.fetchall()\n"
        "            conn.close()\n"
        "    except Exception:\n"
        "        staff_list = []\n\n"
    )
    text = text[:start] + insert_block + text[start:]
    open(APP, "w", encoding="utf-8").write(text)
    print("Inserted staff_list init into tasks().")

print("Done. If something goes wrong restore the backup:", bak)
