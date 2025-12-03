# Production Deployment Guide - Special Agents

**Target:** Get live in production in under 30 minutes
**Platform:** Railway (recommended for speed) or Render
**Database:** PostgreSQL (included)

---

## 🚀 **FASTEST PATH: Railway (Recommended)**

### **Why Railway:**
- ✅ Fastest deployment (5-10 minutes)
- ✅ PostgreSQL included (automatic)
- ✅ Free tier: $5/month credit
- ✅ Automatic SSL
- ✅ Simple environment variables
- ✅ GitHub integration

### **Step-by-Step Railway Deployment:**

#### **1. Create Railway Account (2 min)**
1. Go to: https://railway.app
2. Sign up with GitHub
3. Verify email

#### **2. Create New Project (1 min)**
1. Click "New Project"
2. Select "Deploy from GitHub repo"
3. Choose `jinnks/special-agents` repository
4. Railway will detect the Procfile automatically

#### **3. Add PostgreSQL Database (1 min)**
1. In your project, click "New"
2. Select "Database" → "PostgreSQL"
3. Railway will provision PostgreSQL and add DATABASE_URL automatically
4. **Database is now ready!**

#### **4. Configure Environment Variables (3 min)**

Click on your web service → "Variables" tab → Add these:

```bash
# Required
ANTHROPIC_API_KEY=your-anthropic-api-key-here
SECRET_KEY=generate-a-random-secret-key-here
FLASK_ENV=production

# Optional (Railway sets DATABASE_URL automatically)
# DATABASE_URL is auto-set by Railway when you add PostgreSQL
```

**To generate SECRET_KEY:**
```bash
python3 -c "import secrets; print(secrets.token_hex(32))"
```

#### **5. Deploy! (2 min)**
1. Railway automatically deploys when you push to GitHub
2. Or click "Deploy" in Railway dashboard
3. Wait 2-3 minutes for build
4. Click on the URL Railway provides (e.g., `special-agents-production.up.railway.app`)

#### **6. Verify Deployment (1 min)**
Check these URLs:
- `https://your-app.up.railway.app/health` → Should return `{"status": "healthy"}`
- `https://your-app.up.railway.app/` → Should show homepage
- Test registration and login

---

## 🎯 **ALTERNATIVE: Render (Also Good)**

### **Why Render:**
- ✅ Free tier available
- ✅ PostgreSQL included
- ✅ Auto-SSL
- ✅ Good for startups

### **Step-by-Step Render Deployment:**

#### **1. Create Render Account**
1. Go to: https://render.com
2. Sign up with GitHub
3. Verify email

#### **2. Create Web Service**
1. Click "New +" → "Web Service"
2. Connect GitHub repository `jinnks/special-agents`
3. Configure:
   - **Name:** special-agents
   - **Runtime:** Python 3
   - **Build Command:** `cd backend && pip install -r requirements.txt`
   - **Start Command:** `cd backend && gunicorn --worker-class gevent --workers 2 --bind 0.0.0.0:$PORT 'app:create_app()'`
   - **Plan:** Free

#### **3. Add PostgreSQL Database**
1. Click "New +" → "PostgreSQL"
2. Name it (e.g., `special-agents-db`)
3. Select Free plan
4. Copy the "Internal Database URL"

#### **4. Set Environment Variables**
In Web Service → "Environment":

```bash
ANTHROPIC_API_KEY=your-key-here
SECRET_KEY=your-secret-key-here
DATABASE_URL=<paste-internal-database-url>
FLASK_ENV=production
```

#### **5. Deploy**
Render auto-deploys. Wait 5-10 minutes for first build.

---

## 🔧 **ALTERNATIVE: DigitalOcean App Platform**

### **Step-by-Step:**

#### **1. Create DO Account**
1. Go to: https://cloud.digitalocean.com
2. Sign up (may need credit card, but $200 free credit for 60 days)

#### **2. Create App**
1. Apps → Create App
2. Connect GitHub `jinnks/special-agents`
3. Detect: Python
4. Configure:
   - **Build Command:** `cd backend && pip install -r requirements.txt`
   - **Run Command:** `cd backend && gunicorn --worker-class gevent --workers 2 --bind 0.0.0.0:8080 'app:create_app()'`

#### **3. Add PostgreSQL**
1. Add Component → Database → PostgreSQL
2. Dev or Basic plan
3. Attach to app (DATABASE_URL auto-set)

#### **4. Environment Variables**
```bash
ANTHROPIC_API_KEY=your-key
SECRET_KEY=your-secret
FLASK_ENV=production
```

#### **5. Deploy**
Click "Create Resources" → Wait 10 minutes

---

## 📊 **Post-Deployment Checklist**

### **Immediate (After Deploy):**
- [ ] Visit `/health` endpoint → Should return `{"status": "healthy"}`
- [ ] Test homepage loads
- [ ] Register a new user
- [ ] Test login
- [ ] Upload a .sagent package
- [ ] Test chat with an agent

### **Within 1 Hour:**
- [ ] Update HackerNews post with live URL
- [ ] Update Reddit post with live URL
- [ ] Test from mobile device
- [ ] Check logs for errors (Railway/Render dashboard)

### **Within 24 Hours:**
- [ ] Set up custom domain (if you have one)
- [ ] Monitor for issues
- [ ] Respond to any user feedback

---

## 🌐 **Custom Domain Setup (Optional)**

### **Railway:**
1. Go to your service settings
2. Click "Domains"
3. Add your custom domain (e.g., `specialagents.com`)
4. Add CNAME record in your DNS:
   - Name: `@` or `www`
   - Value: `<your-railway-domain>`
5. SSL auto-configured

### **Render:**
1. Go to your service → "Settings"
2. Add custom domain
3. Follow DNS instructions
4. SSL auto-configured

---

## 📈 **Monitoring**

### **Built-in Monitoring:**
- Railway: Logs tab (real-time)
- Render: Logs tab (real-time)
- DigitalOcean: Insights tab

### **Health Check:**
- `/health` endpoint returns status
- Set up uptime monitoring (optional):
  - UptimeRobot (free): https://uptimerobot.com
  - Pingdom
  - StatusCake

### **Logging:**
- All logs go to stdout (JSON format in production)
- View in platform dashboard
- Errors logged with stack traces

---

## 🔐 **Security Checklist**

### **Already Implemented:**
- ✅ Rate limiting (200/day, 50/hour per IP)
- ✅ Security headers (XSS, CSRF, etc.)
- ✅ HTTPS (automatic on all platforms)
- ✅ Password hashing (Bcrypt)
- ✅ SQL injection prevention (SQLAlchemy ORM)
- ✅ Input validation
- ✅ Error handling (no stack traces to users)

### **Environment Variables (Never commit these):**
- ✅ ANTHROPIC_API_KEY
- ✅ SECRET_KEY
- ✅ DATABASE_URL (auto-set by platform)

---

## 💰 **Cost Estimates**

### **Railway:**
- Free: $5 credit/month (enough for MVP)
- After credit: ~$5-10/month
- PostgreSQL: Included

### **Render:**
- Free tier available
- PostgreSQL: Free tier
- Paid: $7/month (after free tier)

### **DigitalOcean:**
- $0 with free credit (60 days)
- After: $5/month app + $7/month database = $12/month

**Recommendation:** Start with Railway (fastest, easiest, $5 free credit)

---

## 🚨 **Troubleshooting**

### **Build Fails:**
```bash
# Check Python version
cat runtime.txt  # Should be python-3.12.0

# Check requirements.txt exists
ls backend/requirements.txt

# Check Procfile
cat Procfile
```

### **Database Connection Fails:**
```bash
# Check DATABASE_URL is set
echo $DATABASE_URL

# Check it starts with postgresql://
# Railway/Render auto-set this
```

### **App Crashes:**
```bash
# Check logs in platform dashboard
# Look for Python errors
# Verify ANTHROPIC_API_KEY is set
```

### **Health Check Fails:**
```bash
# Visit /health endpoint
# Should return: {"status": "healthy", "database": "healthy"}
# If database unhealthy, check DATABASE_URL
```

---

## 📞 **Support**

**If something doesn't work:**
1. Check logs in platform dashboard
2. Verify all environment variables are set
3. Check `/health` endpoint
4. Review error messages

**Platform Support:**
- Railway: https://railway.app/help
- Render: https://render.com/docs
- DigitalOcean: https://docs.digitalocean.com

---

## ✅ **Quick Start Command Summary**

```bash
# 1. Push to GitHub (already done)
git add -A
git commit -m "Production-ready deployment"
git push origin main

# 2. Go to Railway.app
# 3. New Project → Deploy from GitHub → special-agents
# 4. Add PostgreSQL database
# 5. Set environment variables (ANTHROPIC_API_KEY, SECRET_KEY)
# 6. Deploy automatically happens
# 7. Get URL and test!
```

---

## 🎯 **Success Criteria**

**You've successfully deployed when:**
- ✅ `/health` returns `{"status": "healthy"}`
- ✅ Homepage loads without errors
- ✅ User registration works
- ✅ Login works
- ✅ Can upload .sagent packages
- ✅ Can chat with agents
- ✅ HTTPS working (automatic)
- ✅ No errors in logs

**Time to deploy:** 10-30 minutes depending on platform

**After deployment:** Update HN/Reddit posts with live URL!

---

**RECOMMENDED NEXT STEP:** Use Railway for fastest deployment (5-10 minutes)

**Let's get this live!** 🚀
