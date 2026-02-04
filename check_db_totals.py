#!/usr/bin/env python3
# check_db_totals.py
# Usage:
#   python check_db_totals.py --start 2026-01-01 --end 2026-02-01
# or
#   python check_db_totals.py   (defaults to last 30 days)

import sys, os, argparse, sqlite3
from datetime import date, timedelta, datetime

def try_import_get_conn():
    try:
        # Try to import get_db_connection from app.py (avoid starting server)
        import importlib.util
        spec = importlib.util.spec_from_file_location("app", os.path.join(os.getcwd(), "app.py"))
        app_mod = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(app_mod)
        if hasattr(app_mod, 'get_db_connection'):
            return app_mod.get_db_connection
        return None
    except Exception:
        return None

def guess_db_file():
    # look for sensible DB files in repo
    candidates = []
    for root, dirs, files in os.walk(".", topdown=True):
        # skip venv directories
        if 'venv' in root.split(os.sep) or 'env' in root.split(os.sep):
            continue
        for f in files:
            if f.endswith(('.sqlite','.db','.sqlite3')):
                candidates.append(os.path.join(root, f))
    # prefer ones in project root
    candidates.sort(key=lambda p: (0 if os.path.dirname(p) == '.' else 1, -os.path.getsize(p)))
    return candidates[0] if candidates else None

def connect_via_path(path):
    try:
        conn = sqlite3.connect(path)
        conn.row_factory = sqlite3.Row
        return conn, path
    except Exception as e:
        print("Could not connect to DB path:", path, e)
        return None, None

def main():
    p = argparse.ArgumentParser()
    p.add_argument('--start', help='Start date YYYY-MM-DD')
    p.add_argument('--end', help='End date YYYY-MM-DD')
    args = p.parse_args()

    # compute default 30-day range if not provided
    try:
        if args.start:
            start_dt = datetime.strptime(args.start, '%Y-%m-%d').date()
        else:
            start_dt = date.today() - timedelta(days=29)
        if args.end:
            end_dt = datetime.strptime(args.end, '%Y-%m-%d').date()
        else:
            end_dt = date.today()
    except Exception as e:
        print("Date parse error:", e)
        sys.exit(1)

    if start_dt > end_dt:
        start_dt, end_dt = end_dt, start_dt

    print("Checking totals for range:", start_dt.isoformat(), "->", end_dt.isoformat())

    # Try app's get_db_connection first
    get_conn = try_import_get_conn()
    conn = None
    db_path = None
    if get_conn:
        try:
            conn = get_conn()
            # attempt to discover file path for sqlite
            try:
                db_path = conn.execute("PRAGMA database_list").fetchall()[0]['file']
            except Exception:
                db_path = "(connection from get_db_connection)"
            print("Connected via get_db_connection() (app's helper).")
        except Exception as e:
            print("get_db_connection() exists but failed to return connection:", e)
            conn = None

    if conn is None:
        guessed = guess_db_file()
        if not guessed:
            print("No local sqlite/.db file found. If you use another DB (Postgres/MySQL) please run queries with that client or provide DB connection info.")
            sys.exit(1)
        conn, db_path = connect_via_path(guessed)
        if conn is None:
            print("Failed to open guessed DB file:", guessed)
            sys.exit(1)
        print("Connected to DB file:", db_path)

    cur = conn.cursor()

    # 1) show distinct transaction_type
    try:
        cur.execute("SELECT DISTINCT(transaction_type) as tt FROM financial")
        types = [row['tt'] for row in cur.fetchall()]
        print("Distinct transaction_type values:", types)
    except Exception as e:
        print("Could not query distinct transaction_type (table missing or schema mismatch):", e)

    # 2) sums for range
    try:
        cur.execute("""
            SELECT
              COALESCE(SUM(CASE WHEN LOWER(transaction_type)='income' THEN amount ELSE 0 END),0) as income_lower,
              COALESCE(SUM(CASE WHEN LOWER(transaction_type)='expense' THEN amount ELSE 0 END),0) as expense_lower,
              COALESCE(SUM(CASE WHEN transaction_type='income' THEN amount ELSE 0 END),0) as income_exact,
              COALESCE(SUM(CASE WHEN transaction_type='expense' THEN amount ELSE 0 END),0) as expense_exact
            FROM financial
            WHERE DATE(transaction_date) BETWEEN ? AND ?
        """, (start_dt.isoformat(), end_dt.isoformat()))
        row = cur.fetchone()
        inc_lower = row['income_lower'] if row and 'income_lower' in row.keys() else 0
        exp_lower = row['expense_lower'] if row and 'expense_lower' in row.keys() else 0
        inc_exact = row['income_exact'] if row and 'income_exact' in row.keys() else 0
        exp_exact = row['expense_exact'] if row and 'expense_exact' in row.keys() else 0

        print(f"SUM (case-insensitive LOWER): income={inc_lower}  expense={exp_lower}  net={(inc_lower - exp_lower)}")
        print(f"SUM (exact match): income={inc_exact}  expense={exp_exact}  net={(inc_exact - exp_exact)}")
    except Exception as e:
        print("Sum query failed (financial table might be missing or schema different):", e)

    # 3) recent financial rows (last 20 by transaction_date)
    try:
        cur.execute("SELECT DATE(transaction_date) as d, transaction_type, amount, description FROM financial ORDER BY DATE(transaction_date) DESC LIMIT 20")
        rows = cur.fetchall()
        print("\nRecent financial rows (date, type, amount, description):")
        for r in rows:
            d = r['d'] if 'd' in r.keys() else r[0]
            typ = r['transaction_type'] if 'transaction_type' in r.keys() else r[1]
            amt = r['amount'] if 'amount' in r.keys() else r[2]
            desc = r['description'] if 'description' in r.keys() else (r['desc'] if 'desc' in r.keys() else '')
            print(f"  {d}  |  {typ}  |  {amt}  |  {desc}")
    except Exception as e:
        print("Could not fetch recent financial rows:", e)

    # 4) grouped sums by date (show last 10 dates with sums)
    try:
        cur.execute("""
            SELECT DATE(transaction_date) as d,
              COALESCE(SUM(CASE WHEN LOWER(transaction_type)='income' THEN amount ELSE 0 END),0) as income,
              COALESCE(SUM(CASE WHEN LOWER(transaction_type)='expense' THEN amount ELSE 0 END),0) as expense
            FROM financial
            WHERE DATE(transaction_date) BETWEEN ? AND ?
            GROUP BY DATE(transaction_date)
            ORDER BY DATE(transaction_date) DESC
            LIMIT 10
        """, (start_dt.isoformat(), end_dt.isoformat()))
        rows = cur.fetchall()
        print("\nRecent grouped sums by date (date | income | expense):")
        for r in rows:
            print(f"  {r['d']} | {r['income']} | {r['expense']}")
    except Exception as e:
        print("Could not fetch grouped sums by date:", e)

    conn.close()
    print("\nDone. If the sums above match what you expect but dashboard still does not, reply with the output and I'll show the exact lines to change in app.py/template.")
    return

if __name__ == '__main__':
    main()
