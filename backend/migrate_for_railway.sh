#!/bin/bash
# Migration script to run on Railway deployment
# This ensures the llm_provider column exists in production

echo "Running database migration for llm_provider..."

# Run the migration script
python3 migrate_add_llm_provider.py

if [ $? -eq 0 ]; then
    echo "✓ Migration completed successfully"
else
    echo "✗ Migration failed"
    exit 1
fi
