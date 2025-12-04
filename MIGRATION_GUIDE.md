# Database Migration Guide - Multi-LLM Provider Support

## Overview
This migration adds multi-LLM provider support (Anthropic Claude + OpenAI GPT) to Special Agents.

## What Changed
- Added `llm_provider` column to `Agent` table
- New `llm_service.py` for unified LLM interface
- Updated chat routes to use `LLMService`
- Updated agent creation forms to select LLM provider
- Dynamic UI that shows correct API key prompts

## For Railway Deployment

### Automatic Migration (Recommended)
The migration will run automatically on deployment if you add this to your Railway service:

**Build Command:**
```bash
pip install -r requirements.txt
```

**Deploy Command:**
```bash
python3 backend/migrate_add_llm_provider.py && cd backend && python3 run.py
```

### Manual Migration
If you prefer to run it manually:

```bash
# SSH into Railway container or use Railway CLI
railway run python3 backend/migrate_add_llm_provider.py
```

## For Local Development

### Fresh Install
If you're setting up a new database:
```bash
cd backend
source venv/bin/activate
python3 init_db.py
```

### Existing Database
If you already have a database with agents:
```bash
cd backend
source venv/bin/activate
python3 migrate_add_llm_provider.py
```

## Verification

After migration, verify it worked:

```bash
# Check if column exists
python3 -c "from app import create_app, db; from sqlalchemy import inspect; app = create_app(); app.app_context().push(); print('llm_provider' in [c['name'] for c in inspect(db.engine).get_columns('agent')])"
```

Should print: `True`

## Rollback

If you need to rollback (not recommended):

**PostgreSQL:**
```sql
ALTER TABLE agent DROP COLUMN llm_provider;
```

**SQLite:**
```sql
-- SQLite doesn't support DROP COLUMN, requires table recreation
-- Not recommended - just keep the column
```

## Dependencies Added
- `openai==1.55.3` - OpenAI Python SDK

Make sure to run:
```bash
pip install -r requirements.txt
```
