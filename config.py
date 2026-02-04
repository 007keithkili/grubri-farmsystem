# config.py
import os
from pathlib import Path

class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'dl-farm-secret-key-2025-change-in-production'

    # If you want to force using the local sqlite DB while developing,
    # set env var USE_LOCAL_SQLITE=1 (see PowerShell commands below).
    USE_LOCAL_SQLITE = os.environ.get("USE_LOCAL_SQLITE") == "1"

    # If not forcing local, prefer DATABASE_URL (adjust postgres prefix)
    _env_url = None if USE_LOCAL_SQLITE else os.environ.get('DATABASE_URL')
    if _env_url and _env_url.startswith("postgres://"):
        _env_url = _env_url.replace("postgres://", "postgresql://", 1)

    # Final DB URI: either explicit env DB or local sqlite fallback
    SQLALCHEMY_DATABASE_URI = _env_url or 'sqlite:///database/farm.db'
    SQLALCHEMY_TRACK_MODIFICATIONS = False

DB_PATH = Path('database/farm.db')
