import csv
import sqlite3
from pathlib import Path

DB = Path(__file__).parent.parent / 'database' / 'farm.db'
CSV = Path(__file__).parent.parent / 'data' / 'employees.csv'

if not DB.exists():
    print("ERROR: DB not found at", DB)
    raise SystemExit(1)
if not CSV.exists():
    print("ERROR: CSV not found at", CSV)
    raise SystemExit(1)

conn = sqlite3.connect(str(DB))
cur = conn.cursor()

inserted = 0
skipped = 0
errors = 0

with open(CSV, newline='', encoding='utf-8') as fh:
    reader = csv.DictReader(fh)
    for r in reader:
        name = (r.get('NAME') or r.get('Name') or r.get('name') or '').strip()
        id_number = (r.get('ID') or r.get('Id') or r.get('id') or '').strip()
        phone = (r.get('TELEPHONE') or r.get('Telephone') or r.get('telephone') or '').strip()
        position = (r.get('JOB DESCRIPTION') or r.get('JOB_DESCRIPTION') or r.get('Job Description') or '').strip()
        department = (r.get('DEPARTMENT') or r.get('Department') or r.get('department') or '').strip()

        if not name:
            skipped += 1
            continue

        parts = name.split()
        first_name = parts[0]
        last_name = ' '.join(parts[1:]) if len(parts) > 1 else ''

        try:
            if id_number:
                cur.execute("SELECT id FROM staff WHERE id_number = ?", (id_number,))
                if cur.fetchone():
                    skipped += 1
                    continue
            if phone:
                cur.execute("SELECT id FROM staff WHERE phone = ?", (phone,))
                if cur.fetchone():
                    skipped += 1
                    continue
        except Exception as e:
            print("Lookup error:", e)
            errors += 1
            continue

        try:
            cur.execute("""INSERT INTO staff
                (first_name, last_name, position, department, email, phone, address, dob, date_employed, status, created_at, id_number)
                VALUES (?, ?, ?, ?, ?, ?, ?, NULL, NULL, 'Active', CURRENT_TIMESTAMP, ?)
            """, (first_name, last_name, position, department, '', phone, '', id_number))
            inserted += 1
        except Exception as e:
            print("Insert error for", name, ":", e)
            errors += 1

conn.commit()
conn.close()
print(f"Done. inserted: {inserted}, skipped(existing): {skipped}, errors: {errors}")
