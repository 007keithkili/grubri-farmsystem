# db_helper.py
# Compatibility DB helper:
# - If DATABASE_URL points to SQLite -> return a DB-API sqlite3.Connection
# - Otherwise use SQLAlchemy engine and provide a wrapper that exposes
#   cursor()/commit()/rollback()/close() so old code using sqlite3 still works.
import os
import sqlite3
from pathlib import Path

from sqlalchemy import create_engine

BASE_DIR = Path(__file__).resolve().parent

# Read DATABASE_URL from env (set by Render/Railway/others). Fallback to local sqlite file.
DATABASE_URL = os.environ.get("DATABASE_URL") or f"sqlite:///{BASE_DIR / 'data.db'}"

# Helper: if sqlite, compute file path
def _sqlite_file_from_url(url: str) -> Path:
    # expect sqlite:///absolute/path/to/file.db or sqlite:///:memory:
    if url == "sqlite:///:memory:":
        return None
    prefix = "sqlite:///"
    if url.startswith(prefix):
        return Path(url[len(prefix):])
    # fallback: if someone passed just a filename
    return Path(url)

# SQLAlchemy engine only created for non-sqlite DBs
_engine = None
_is_sqlite = False
_sqlite_file = None

if DATABASE_URL.startswith("sqlite"):
    _is_sqlite = True
    _sqlite_file = _sqlite_file_from_url(DATABASE_URL)
    if _sqlite_file:
        _sqlite_file.parent.mkdir(parents=True, exist_ok=True)
else:
    # create engine for Postgres or other SQLAlchemy-supported DBs
    # (No connect_args here - let SQLAlchemy choose defaults)
    _engine = create_engine(DATABASE_URL, future=True)

# Cursor wrapper for SQLAlchemy connections (gives cursor-like interface)
class _SACursor:
    def __init__(self, sa_conn):
        self._sa_conn = sa_conn
        self._result = None

    def execute(self, sql, params=None):
        # Use exec_driver_sql so we can pass positional tuple params when available
        if params is None:
            self._result = self._sa_conn.exec_driver_sql(sql)
        else:
            # pass params directly; SQLAlchemy will forward them to the DBAPI
            self._result = self._sa_conn.exec_driver_sql(sql, params)
        return self

    def fetchall(self):
        if self._result is None:
            return []
        return self._result.fetchall()

    def fetchone(self):
        if self._result is None:
            return None
        return self._result.fetchone()

    def close(self):
        # nothing to do - SQLAlchemy result closes by GC
        pass

# DB connection wrapper for SQLAlchemy that exposes cursor(), commit(), rollback(), close()
class _SAConnWrapper:
    def __init__(self, engine):
        self._engine = engine
        # open a connection
        self._sa_conn = self._engine.connect()
        self._transaction = None

    def cursor(self):
        return _SACursor(self._sa_conn)

    def commit(self):
        # begin a transient transaction if none exists, commit it
        if self._transaction is None:
            # begin a transaction, then immediately commit (exec_driver_sql already ran)
            tx = self._sa_conn.begin()
            tx.commit()
        else:
            self._transaction.commit()
            self._transaction = None

    def rollback(self):
        if self._transaction is not None:
            try:
                self._transaction.rollback()
            except Exception:
                pass
            self._transaction = None

    def close(self):
        try:
            if self._transaction is not None:
                try:
                    self._transaction.close()
                except Exception:
                    pass
                self._transaction = None
            self._sa_conn.close()
        except Exception:
            pass

def get_db_connection():
    """
    Return a DB connection object compatible with existing app code.
    - For SQLite: returns a sqlite3.Connection (DB-API).
    - For other DBs: returns a wrapper with .cursor(), .commit(), .rollback(), .close().
    """
    if _is_sqlite:
        if _sqlite_file is None:
            # in-memory sqlite
            conn = sqlite3.connect(":memory:", check_same_thread=False)
        else:
            conn = sqlite3.connect(str(_sqlite_file), check_same_thread=False)
        # give row access by name if app expects it sometimes
        conn.row_factory = sqlite3.Row
        return conn
    else:
        # return a wrapper around a SQLAlchemy Connection
        return _SAConnWrapper(_engine)
