# db_helper.py
# DB connection helper (works with Postgres via DATABASE_URL, falls back to local sqlite)
import os
from pathlib import Path
from sqlalchemy import create_engine, text

BASE_DIR = Path(__file__).resolve().parent

# Use DATABASE_URL env var when present (Render Postgres or other managed DB)
DATABASE_URL = os.environ.get('DATABASE_URL')
if DATABASE_URL:
    # Render / some services return "postgres://..." which SQLAlchemy rejects.
    # Convert legacy scheme to SQLAlchemy-compatible scheme.
    if DATABASE_URL.startswith("postgres://"):
        DATABASE_URL = DATABASE_URL.replace("postgres://", "postgresql://", 1)
else:
    # fallback to a local sqlite file (for local dev or quick demo)
    DATABASE_URL = f"sqlite:///{BASE_DIR / 'data.db'}"

# For sqlite we must pass check_same_thread to allow multithreaded servers
connect_args = {}
if DATABASE_URL.startswith("sqlite"):
    connect_args = {"check_same_thread": False}

# Create DB engine (SQLAlchemy 1.4/2.0 style)
engine = create_engine(DATABASE_URL, future=True, connect_args=connect_args)

def get_db_connection():
    """
    Returns a SQLAlchemy Connection object. Example usage:
        conn = get_db_connection()
        res = conn.execute(text("SELECT * FROM staff"))
        rows = [dict(r) for r in res.fetchall()]
        conn.close()

    Notes:
    - Use sqlalchemy.text() for SQL strings.
    - For SELECTs, `res.fetchall()` returns Row objects convertible to dict.
    - For single-value queries, you can use `res.scalar()` after executing.
    - After INSERT/UPDATE/DELETE you must call `conn.commit()`.
    """
    return engine.connect()
