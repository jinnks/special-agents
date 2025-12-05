#!/usr/bin/env python3
"""
Database migration: Add llm_provider column to Agent table
Safe for both SQLite and PostgreSQL
"""
import os
import sys

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app import create_app, db
from sqlalchemy import inspect, text

def column_exists(table_name, column_name):
    """Check if a column exists in a table"""
    try:
        inspector = inspect(db.engine)
        columns = [col['name'] for col in inspector.get_columns(table_name)]
        return column_name in columns
    except Exception:
        # Table doesn't exist yet
        return False

def migrate():
    """Add llm_provider column to agent table"""
    app = create_app()

    with app.app_context():
        try:
            # Check if table exists
            inspector = inspect(db.engine)
            tables = inspector.get_table_names()

            if 'agent' not in tables:
                print("✓ Table 'agent' doesn't exist yet - will be created by db.create_all()")
                return True

            # Check if column already exists
            if column_exists('agent', 'llm_provider'):
                print("✓ Column 'llm_provider' already exists in 'agent' table")
                return True

            print("Adding 'llm_provider' column to 'agent' table...")

            # Detect database type
            db_url = str(db.engine.url)
            is_postgres = 'postgresql' in db_url

            # Add column based on database type
            if is_postgres:
                # PostgreSQL
                db.session.execute(text(
                    "ALTER TABLE agent ADD COLUMN llm_provider VARCHAR(50) NOT NULL DEFAULT 'anthropic'"
                ))
            else:
                # SQLite
                db.session.execute(text(
                    "ALTER TABLE agent ADD COLUMN llm_provider VARCHAR(50) NOT NULL DEFAULT 'anthropic'"
                ))

            db.session.commit()
            print("✓ Column 'llm_provider' added successfully")

            # Verify
            if column_exists('agent', 'llm_provider'):
                print("✓ Migration verified - column exists")
                return True
            else:
                print("✗ Migration failed - column not found after creation")
                return False

        except Exception as e:
            db.session.rollback()
            print(f"✗ Migration failed: {str(e)}")
            import traceback
            traceback.print_exc()
            return False

if __name__ == '__main__':
    success = migrate()
    sys.exit(0 if success else 1)
