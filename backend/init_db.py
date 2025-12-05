#!/usr/bin/env python3
"""Initialize the database with all tables"""
import os
import sys

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app import create_app, db

def init_database():
    """Create all database tables"""
    app = create_app()

    with app.app_context():
        print("Creating database tables...")
        db.create_all()
        print("✓ Database initialized successfully")

if __name__ == '__main__':
    init_database()
