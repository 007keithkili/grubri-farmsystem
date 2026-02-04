# db_helper.py
"""
DB helper for dl-farm-management-system.

Exports:
 - engine: SQLAlchemy Engine (created from DATABASE_URL or sqlite fallback)
 - get_db_connection(): returns a DB-API connection object compatible with
   existing code that uses .cursor(), .commit(), .close().

Behavior:
 - If env var DATABASE_URL is set, it's used. Otherwise we use sqlite file ./data.db.
 - If DATABASE_URL is Postgres, this will use psycopg2 for cursor-style connections.
"""

from pathlib import Path
import os
import sqlite3
import urllib.parse

from sqlalchemy import create_engine

# Try to import psycopg2 but do not fail import if not installed (we only need it for postgres)
try:
    import psycopg2
except Exception:
    psycopg2 = None

BASE_DIR = Path(__file__).resolve().parent

# Choose DB URL
env_db = os.environ.get("DATABASE_URL", "").strip()
if env_db:
    DATABASE_URL = env_db
else:
    sqlite_path = (BASE_DIR / "data.db").as_posix()  # use forward slashes to avoid Windows backslash issues
    DATABASE_URL = f"sqlite:///{sqlite_path}"

# Create SQLAlchemy engine
if DATABASE_URL.startswith("sqlite"):
    # Ensure folder exists
    (BASE_DIR).mkdir(parents=True, exist_ok=True)
    connect_args = {"check_same_thread": False}
    engine = create_engine(DATABASE_URL, future=True, connect_args=connect_args)
else:
    # For Postgres / other DBs let SQLAlchemy handle the URL
    engine = create_engine(DATABASE_URL, future=True)


def get_db_connection():
    """
    Return a DB-API connection suitable for existing code:
      - sqlite3.Connection (with row_factory=sqlite3.Row) when DATABASE_URL is sqlite.
      - psycopg2 connection when DATABASE_URL is Postgres/pgx.
    Raises informative errors if psycopg2 is required but missing.
    """
    if DATABASE_URL.startswith("sqlite"):
        db_file = BASE_DIR / "data.db"
        conn = sqlite3.connect(str(db_file), detect_types=sqlite3.PARSE_DECLTYPES | sqlite3.PARSE_COLNAMES)
        conn.row_factory = sqlite3.Row
        return conn

    # Non-sqlite: parse and connect with psycopg2
    if psycopg2 is None:
        raise RuntimeError(
            "psycopg2 is required for Postgres DATABASE_URL. Install psycopg2-binary "
            "(pip install psycopg2-binary) or switch to sqlite."
        )

    # Parse URL using urllib; supports postgresql://user:pass@host:port/dbname and also URLs with query params
    parsed = urllib.parse.urlparse(DATABASE_URL)
    # urlparse path is '/dbname'
    dbname = parsed.path.lstrip("/") if parsed.path else None
    user = urllib.parse.unquote(parsed.username) if parsed.username else None
    password = urllib.parse.unquote(parsed.password) if parsed.password else None
    host = parsed.hostname
    port = parsed.port

    # If query has e.g. sslmode, build dsn string to include options
    query = urllib.parse.parse_qs(parsed.query)
    # Build kwargs for psycopg2
    conn_kwargs = {}
    if dbname:
        conn_kwargs["dbname"] = dbname
    if user:
        conn_kwargs["user"] = user
    if password:
        conn_kwargs["password"] = password
    if host:
        conn_kwargs["host"] = host
    if port:
        conn_kwargs["port"] = port

    # include any simple single-valued query params as connect options (e.g. sslmode)
    for k, v in query.items():
        if len(v) == 1:
            conn_kwargs[k] = v[0]

    conn = psycopg2.connect(**conn_kwargs)
    return conn
