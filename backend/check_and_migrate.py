#!/usr/bin/env python3
# Copyright (c) 2025 Special Agents
# Licensed under MIT License - See LICENSE file for details

"""
Smart migration checker - only runs migrations if needed
This prevents migration errors on Railway deployments
"""
import os
import sys
from sqlalchemy import text, inspect

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app import create_app, db

def check_and_migrate():
    """Check database state and run migrations only if needed"""
    app = create_app()

    with app.app_context():
        inspector = inspect(db.engine)
        existing_tables = inspector.get_table_names()

        print("=" * 60)
        print("Database Migration Checker")
        print("=" * 60)
        print(f"\nFound {len(existing_tables)} tables: {existing_tables}")

        # Check if we have the new schema (singular table names)
        has_singular_tables = 'agent' in existing_tables and 'user' in existing_tables
        has_creation_mode = False

        if has_singular_tables:
            print("✓ Using singular table names (new schema)")

            # Check if we have creation_mode column
            try:
                columns = inspector.get_columns('agent_config')
                column_names = [col['name'] for col in columns]
                has_creation_mode = 'creation_mode' in column_names

                if has_creation_mode:
                    print("✓ Creation mode fields present")
                else:
                    print("⚠️  Creation mode fields missing - running migration...")
                    from migrate_add_creation_mode import migrate as add_creation_mode
                    add_creation_mode()

            except Exception as e:
                print(f"⚠️  Could not check agent_config: {e}")

        else:
            print("⚠️  Using old schema (plural table names) or fresh database")

            # Check if this is completely fresh
            if len(existing_tables) == 0:
                print("✓ Fresh database - creating all tables...")
                db.create_all()
                print("✓ Tables created successfully")
            else:
                print("⚠️  Old schema detected - needs manual migration")
                print("   Please run: python migrate_schema_v2.py")
                print("   Then run: python migrate_add_creation_mode.py")

        print("\n" + "=" * 60)
        print("Migration check complete!")
        print("=" * 60)

if __name__ == '__main__':
    check_and_migrate()
