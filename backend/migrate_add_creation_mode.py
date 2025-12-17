# Copyright (c) 2025 Special Agents
# Licensed under MIT License - See LICENSE file for details

"""
Migration: Add creation mode and example conversations support
Adds fields to track how agents were created and store example interactions
"""
import os
import sys
from sqlalchemy import text

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app import create_app, db

def migrate():
    """Add new fields for enhanced agent creation"""
    app = create_app()

    with app.app_context():
        print("🔄 Adding creation mode and example conversation support...")

        # Check if columns already exist
        from sqlalchemy import inspect
        inspector = inspect(db.engine)

        try:
            columns = inspector.get_columns('agent_config')
            column_names = [col['name'] for col in columns]

            if 'creation_mode' in column_names:
                print("✅ Creation mode fields already exist - skipping migration")
                return

        except Exception:
            print("⚠️  Could not check existing columns, proceeding with migration...")

        # Detect database type
        engine_name = db.engine.name
        is_postgres = engine_name == 'postgresql'

        try:
            # Add creation_mode to agent_config table
            if is_postgres:
                db.session.execute(text('''
                    ALTER TABLE agent_config
                    ADD COLUMN IF NOT EXISTS creation_mode VARCHAR(20) DEFAULT 'web_form'
                '''))
                db.session.execute(text('''
                    ALTER TABLE agent_config
                    ADD COLUMN IF NOT EXISTS template_id VARCHAR(50)
                '''))
                db.session.execute(text('''
                    ALTER TABLE agent_config
                    ADD COLUMN IF NOT EXISTS example_conversations TEXT
                '''))
            else:  # SQLite
                # Check if columns exist
                result = db.session.execute(text("PRAGMA table_info(agent_config)")).fetchall()
                existing_columns = [row[1] for row in result]

                if 'creation_mode' not in existing_columns:
                    db.session.execute(text('''
                        ALTER TABLE agent_config
                        ADD COLUMN creation_mode VARCHAR(20) DEFAULT 'web_form'
                    '''))

                if 'template_id' not in existing_columns:
                    db.session.execute(text('''
                        ALTER TABLE agent_config
                        ADD COLUMN template_id VARCHAR(50)
                    '''))

                if 'example_conversations' not in existing_columns:
                    db.session.execute(text('''
                        ALTER TABLE agent_config
                        ADD COLUMN example_conversations TEXT
                    '''))

            db.session.commit()
            print("✅ Migration completed successfully!")
            print("\nNew fields added:")
            print("  - creation_mode: Track how agent was created (web_form, template, package, ai_assistant)")
            print("  - template_id: If created from template, which one")
            print("  - example_conversations: JSON array of example interactions")

        except Exception as e:
            db.session.rollback()
            print(f"❌ Migration failed: {str(e)}")
            raise

if __name__ == '__main__':
    migrate()
