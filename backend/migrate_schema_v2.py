#!/usr/bin/env python3
"""
Database migration for schema v2: Normalized structure with singular table names
WARNING: This drops all existing tables and recreates with new schema
"""
import os
import sys

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app import create_app, db
from sqlalchemy import inspect, text

def migrate():
    """Drop old tables and create new normalized schema"""
    app = create_app()

    with app.app_context():
        try:
            inspector = inspect(db.engine)
            existing_tables = inspector.get_table_names()

            print("=" * 60)
            print("Schema Migration v2: Normalized Database")
            print("=" * 60)

            if existing_tables:
                print(f"\nFound {len(existing_tables)} existing tables:")
                for table in existing_tables:
                    print(f"  - {table}")

                print("\n⚠️  Dropping old tables (no data loss - fresh deployment)...")

                # Detect database type
                db_url = str(db.engine.url)
                is_postgres = 'postgresql' in db_url

                # Drop all tables in correct order (respecting foreign keys)
                drop_order = [
                    'review', 'reviews',
                    'purchase', 'purchases',
                    'agent_stats', 'agent_pricing', 'agent_package', 'agent_config',
                    'agent', 'agents',
                    'user', 'users'
                ]

                for table in drop_order:
                    if table in existing_tables:
                        print(f"  Dropping {table}...")
                        if is_postgres:
                            db.session.execute(text(f'DROP TABLE IF EXISTS {table} CASCADE'))
                        else:
                            # SQLite doesn't support CASCADE
                            db.session.execute(text(f'DROP TABLE IF EXISTS {table}'))

                db.session.commit()
                print("✓ Old tables dropped")

            print("\nCreating new normalized schema...")
            db.create_all()

            # Verify new tables
            new_tables = inspect(db.engine).get_table_names()
            print(f"\n✓ Created {len(new_tables)} tables:")
            for table in sorted(new_tables):
                columns = inspect(db.engine).get_columns(table)
                print(f"  ✓ {table} ({len(columns)} columns)")

            print("\n" + "=" * 60)
            print("✓ Migration completed successfully!")
            print("=" * 60)
            return True

        except Exception as e:
            db.session.rollback()
            print(f"\n✗ Migration failed: {str(e)}")
            import traceback
            traceback.print_exc()
            return False

if __name__ == '__main__':
    success = migrate()
    sys.exit(0 if success else 1)
