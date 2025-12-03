# Railway Deployment Troubleshooting Guide

**Issue:** Cannot access metro.proxy.rlwy.net after deployment

## Step 1: Check Build Logs (CRITICAL)

1. Go to Railway dashboard: https://railway.app/dashboard
2. Click on your `special-agents` project
3. Click on the web service
4. Click **"Deployments"** tab
5. Click on the latest deployment
6. Check **"Build Logs"** - Look for:
   - ✅ `Building...` completed successfully
   - ❌ Any errors during `pip install -r requirements.txt`
   - ❌ Python version errors
   - ❌ Dependency installation failures

**Common build errors:**
- Missing `requirements.txt` in correct location
- Python version mismatch
- Dependency conflicts

## Step 2: Check Deploy Logs (CRITICAL)

1. In the same deployment view, click **"Deploy Logs"**
2. Look for:
   - ✅ `Starting process with command: ...` (should show gunicorn command)
   - ✅ `[INFO] Starting Special Agents in PRODUCTION mode`
   - ✅ `[INFO] Special Agents initialized successfully`
   - ❌ `ModuleNotFoundError` or `ImportError`
   - ❌ Database connection errors
   - ❌ `ANTHROPIC_API_KEY` missing errors
   - ❌ Port binding errors

## Step 3: Verify Environment Variables

1. Click on your web service → **"Variables"** tab
2. **Required variables** (must be set):
   ```
   ANTHROPIC_API_KEY=sk-ant-... (your key)
   SECRET_KEY=<generate with: python3 -c "import secrets; print(secrets.token_hex(32))">
   FLASK_ENV=production
   ```

3. **Check DATABASE_URL**:
   - Should be **auto-set** by Railway when you add PostgreSQL
   - Format: `postgresql://user:password@host:port/database`
   - If missing, you need to add PostgreSQL database (see Step 4)

## Step 4: Verify PostgreSQL Database is Added

1. In your Railway project dashboard, check if you see **TWO services**:
   - Web service (your app)
   - PostgreSQL database

2. **If PostgreSQL is missing:**
   - Click **"New"** in your project
   - Select **"Database"** → **"PostgreSQL"**
   - Railway will auto-provision and link it
   - DATABASE_URL will be automatically set

3. **If PostgreSQL exists:**
   - Click on PostgreSQL service
   - Check **"Connect"** tab
   - Verify connection details are valid

## Step 5: Check Service URL and Domain

1. Click on web service → **"Settings"** tab
2. Under **"Domains"**, check:
   - Is there a Railway-provided domain? (e.g., `special-agents-production.up.railway.app`)
   - Try accessing this domain instead of metro.proxy.rlwy.net
   - If no domain, click **"Generate Domain"**

## Step 6: Test Health Endpoint

Once you have a domain, test:
```bash
curl https://your-app.up.railway.app/health
```

**Expected response:**
```json
{"status": "healthy", "database": "healthy", "version": "1.0.0"}
```

**If you get errors:**
- `503`: Database connection failed
- `500`: Application error
- `404`: Routing issue or app not started

## Step 7: Check Railway Service Status

1. In Railway dashboard, check service status indicator:
   - ✅ Green dot = Running
   - 🔴 Red dot = Crashed/Failed
   - 🟡 Yellow dot = Building/Deploying

2. If crashed, check **"Deploy Logs"** for crash reason

## Step 8: Verify Start Command

1. Railway should auto-detect the `Procfile`
2. In service settings, check **"Start Command"**:
   ```
   cd backend && gunicorn --worker-class gevent --workers 2 --bind 0.0.0.0:$PORT --timeout 120 --access-logfile - --error-logfile - 'app:create_app()'
   ```

3. If missing or different, manually set it

## Step 9: Common Issues and Fixes

### Issue: "Application failed to respond"
**Fix:** Check deploy logs - app likely crashed on startup
- Missing SECRET_KEY
- Missing ANTHROPIC_API_KEY
- Database connection failed

### Issue: "502 Bad Gateway"
**Fix:** App not binding to correct port
- Verify Procfile uses `$PORT` (not hardcoded 8000)
- Check deploy logs for port binding errors

### Issue: "Database connection failed"
**Fix:**
- Ensure PostgreSQL service is added
- Check DATABASE_URL is set
- Verify DATABASE_URL starts with `postgresql://` (not `postgres://`)

### Issue: "Build succeeded but app crashes immediately"
**Fix:** Check deploy logs for Python errors
- Missing dependencies in requirements.txt
- Import errors
- Configuration errors

## Step 10: Get Detailed Logs

Run these commands to check logs:

1. **View recent logs:**
   - Railway dashboard → Service → "Deployments" → Latest deployment → "Deploy Logs"

2. **Look for specific errors:**
   - `ModuleNotFoundError` → Missing dependency
   - `Connection refused` → Database not connected
   - `Address already in use` → Port conflict (shouldn't happen on Railway)
   - `KeyError: 'ANTHROPIC_API_KEY'` → Environment variable missing

## Quick Checklist

- [ ] Build logs show successful build
- [ ] Deploy logs show "Special Agents initialized successfully"
- [ ] PostgreSQL database added to project
- [ ] DATABASE_URL environment variable set (auto-set by Railway)
- [ ] ANTHROPIC_API_KEY environment variable set
- [ ] SECRET_KEY environment variable set
- [ ] FLASK_ENV=production environment variable set
- [ ] Railway domain generated (not metro.proxy.rlwy.net)
- [ ] Service status shows green (running)
- [ ] /health endpoint returns 200 OK

## If Still Failing - Share These Details:

Please check and share:
1. **Build logs** (last 50 lines)
2. **Deploy logs** (last 50 lines)
3. **Environment variables** (names only, not values)
4. **Service status** (running/crashed/building)
5. **PostgreSQL status** (added or not)
6. **Generated domain** (the actual Railway domain)

---

## Most Likely Issues:

Based on "metro.proxy.rlwy.net fails":

1. **Wrong domain** - Railway domains are usually `*.up.railway.app`, not metro.proxy.rlwy.net
   - Check Settings → Domains for actual domain

2. **PostgreSQL not added** - App crashes without database
   - Add PostgreSQL service to project

3. **Missing SECRET_KEY** - App won't start without it
   - Generate: `python3 -c "import secrets; print(secrets.token_hex(32))"`
   - Add to environment variables

4. **Build failed silently** - Check build logs
   - Ensure requirements.txt is in `/home/fsiddiqui/special-agents/backend/requirements.txt`

---

**Next Step:** Go through Steps 1-6 above and report what you find. The deploy logs will tell us exactly what's wrong.
