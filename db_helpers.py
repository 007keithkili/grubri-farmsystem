import sqlite3

def ensure_task_columns(conn):
    \"\"\"
    Ensure the 'task' table exists and has at least the 'status' and 'due_date' columns.
    Adds missing columns if necessary. Works with SQLite.
    \"\"\"
    cur = conn.cursor()

    # If table doesn't exist, create a minimal sensible table
    cur.execute(\"SELECT name FROM sqlite_master WHERE type='table' AND name='task'\")
    if cur.fetchone() is None:
        cur.execute(\"\"\"
            CREATE TABLE task (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                title TEXT,
                description TEXT,
                status TEXT DEFAULT 'Pending',
                due_date TEXT
            )
        \"\"\")
        conn.commit()
        return

    # Get existing columns
    cur.execute(\"PRAGMA table_info(task)\")
    existing = {row[1] for row in cur.fetchall()}

    # Columns we expect other code to use
    needed = {
        \"status\": \"TEXT DEFAULT 'Pending'\",
        \"due_date\": \"TEXT\"
    }

    for col, col_def in needed.items():
        if col not in existing:
            try:
                cur.execute(f\"ALTER TABLE task ADD COLUMN {col} {col_def}\")
                print(f\"Added column '{col}' to task table.\")
            except sqlite3.OperationalError as e:
                print(f\"Could not add column '{col}': {e}\")

    conn.commit()
