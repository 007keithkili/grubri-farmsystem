# config.py - UPDATED
import os
from pathlib import Path

class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'dl-farm-secret-key-2025-change-in-production'
    SQLALCHEMY_DATABASE_URI = 'sqlite:///database/farm.db'
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    
    # Role permissions
    ROLE_PERMISSIONS = {
        'admin': ['all'],
        'manager': ['animals', 'breeding', 'medical', 'feed', 'inventory', 'staff', 'tasks'],
        'accountant': ['sales', 'customers', 'financial', 'suppliers']
    }

# Database path
DB_PATH = Path('database/farm.db')