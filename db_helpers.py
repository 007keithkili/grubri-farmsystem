import sqlite3
from sqlalchemy import text

def ensure_task_columns(conn):
    """
    Ensure the 'task' table exists and has at least the 'status' and 'due_date' columns.
    Adds missing columns if necessary. Works with SQLite.
    """
    cur = conn.cursor() if hasattr(conn, "cursor") else get_cursor(conn)

    # If table doesn't exist, create a minimal sensible table
    cur.execute("SELECT name FROM sqlite_master WHERE type=''table'' AND name=''task''")
    if cur.fetchone() is None:
        cur.execute("""
            CREATE TABLE task (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                title TEXT,
                description TEXT,
                status TEXT DEFAULT 'Pending',
                due_date TEXT
            )
        """)
        try:
            conn.commit()
        except Exception:
            # some wrapped connections don't have commit; ignore
            pass
        return

    # Get existing columns
    # For wrappers that return SQLAlchemy results, fetchall() will still work via wrapper.
    cur.execute("PRAGMA table_info(task)")
    existing_rows = cur.fetchall() or []
    existing = {row[1] for row in existing_rows if len(row) > 1}

    # Columns we expect other code to use
    needed = {
        "status": "TEXT DEFAULT 'Pending'",
        "due_date": "TEXT"
    }

    for col, col_def in needed.items():
        if col not in existing:
            try:
                cur.execute(f"ALTER TABLE task ADD COLUMN {col} {col_def}")
                print(f"Added column '{col}' to task table.")
            except Exception as e:
                print(f"Could not add column '{col}': {e}")

    try:
        conn.commit()
    except Exception:
        pass

def get_cursor(conn):
    """
    Return a DB-API-like cursor for different connection types.
    - If conn has .cursor(), return that (sqlite3, psycopg2).
    - Otherwise return a small wrapper for SQLAlchemy-style connections.
    The wrapper converts SQL with '?' placeholders + tuple/list params into
    a named-parameter sqlalchemy.text(...) call.
    """
    if hasattr(conn, "cursor"):
        return conn.cursor()

    class _CursorWrapper:
        def __init__(self, conn):
            self.conn = conn
            self._last = None

        def execute(self, sql, params=None):
            # If we received a list/tuple of params and '?' placeholders, convert them
            if isinstance(sql, str) and params is not None and isinstance(params, (list, tuple)):
                if "?" in sql:
                    splits = sql.split("?")
                    # Build new SQL with :p0, :p1 placeholders
                    new_sql_parts = []
                    params_dict = {}
                    for i, part in enumerate(splits[:-1]):
                        new_sql_parts.append(part)
                        new_sql_parts.append(f":p{i}")
                        params_dict[f"p{i}"] = params[i] if i < len(params) else None
                    new_sql_parts.append(splits[-1])
                    sql = "".join(new_sql_parts)
                    params = params_dict

            # If sql is a plain string, use sqlalchemy.text() to be safe
            if isinstance(sql, str):
                sql_obj = text(sql)
            else:
                sql_obj = sql

            # Execute via SQLAlchemy connection
            if params is None:
                self._last = self.conn.execute(sql_obj)
            else:
                self._last = self.conn.execute(sql_obj, params)
            return self._last

        def fetchone(self):
            try:
                return self._last.fetchone()
            except Exception:
                try:
                    return self._last.first()
                except Exception:
                    rows = list(self._last)
                    return rows[0] if rows else None

        def fetchall(self):
            try:
                return self._last.fetchall()
            except Exception:
                return list(self._last)

    return _CursorWrapper(conn)
