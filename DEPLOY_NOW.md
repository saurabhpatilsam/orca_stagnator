# 🚀 Deploy to Vercel + Railway (FREE)

## ✅ Your Setup
- **Frontend:** Vercel (Free tier)
- **Backend:** Railway (Free tier - $5 credit/month)
- **Domain:** infignity.com (DNS at Hostinger)
- **URL:** www.infignity.com/supabase_csv_upload

---

## 📋 Prerequisites

- [ ] GitHub account
- [ ] Vercel account (sign up at vercel.com)
- [ ] Railway account (sign up at railway.app)
- [ ] Access to Hostinger DNS settings

---

## 🎯 PART 1: Deploy Backend to Railway (10 minutes)

### **Step 1: Create GitHub Repository**

```bash
cd /Users/stagnator/Downloads/orca-ven-backend-main

# Initialize git (if not already)
git init

# Create .gitignore
cat > .gitignore << EOF
__pycache__/
*.pyc
.env
.DS_Store
node_modules/
frontend/dist/
frontend/node_modules/
*.log
EOF

# Commit files
git add api_server.py upload_tick_data.py requirements_api.txt
git commit -m "Add CSV upload API"

# Create repo on GitHub and push
# (Go to github.com, create new repo "csv-upload-api")
git remote add origin https://github.com/YOUR_USERNAME/csv-upload-api.git
git branch -M main
git push -u origin main
```

### **Step 2: Deploy to Railway**

1. **Go to:** https://railway.app
2. **Click:** "Start a New Project"
3. **Select:** "Deploy from GitHub repo"
4. **Choose:** Your `csv-upload-api` repository
5. **Railway will auto-detect Python and deploy!**

### **Step 3: Add Environment Variables**

In Railway dashboard:

1. Click on your project
2. Go to **"Variables"** tab
3. Add these variables:

```
SUPABASE_URL=https://dcoukhtfcloqpfmijock.supabase.co
SUPABASE_KEY=your_supabase_anon_key
PORT=8000
```

4. Click **"Deploy"** (Railway will redeploy with env vars)

### **Step 4: Get Your Backend URL**

1. In Railway dashboard, go to **"Settings"**
2. Click **"Generate Domain"**
3. Copy the URL (e.g., `https://csv-upload-api-production.up.railway.app`)

**Save this URL - you'll need it for the frontend!**

---

## 🎨 PART 2: Deploy Frontend to Vercel (10 minutes)

### **Step 1: Update API URL in Frontend**

```bash
cd /Users/stagnator/Downloads/orca-ven-backend-main/frontend
```

Edit `src/App.jsx` and add this at the top (after imports):

```javascript
// Add this after the imports (around line 4)
const API_URL = 'https://YOUR-RAILWAY-URL.up.railway.app';
```

Then update the fetch call (around line 50):

```javascript
// Change from:
const response = await fetch('/api/upload-tick-data', {

// To:
const response = await fetch(`${API_URL}/api/upload-tick-data`, {
```

### **Step 2: Build Frontend**

```bash
cd /Users/stagnator/Downloads/orca-ven-backend-main/frontend

# Install dependencies
npm install

# Build for production
npm run build
```

### **Step 3: Deploy to Vercel**

**Option A: Using Vercel CLI (Recommended)**

```bash
# Install Vercel CLI
npm install -g vercel

# Login to Vercel
vercel login

# Deploy
vercel --prod

# When prompted:
# - Set up and deploy? Yes
# - Which scope? Your account
# - Link to existing project? No
# - Project name? csv-upload-frontend
# - Directory? ./
# - Override settings? No
```

**Option B: Using Vercel Dashboard**

1. Go to https://vercel.com/dashboard
2. Click **"Add New"** → **"Project"**
3. Import your GitHub repo (or upload `dist` folder)
4. Click **"Deploy"**

### **Step 4: Get Your Vercel URL**

After deployment, Vercel will give you a URL like:
```
https://csv-upload-frontend.vercel.app
```

Test it! Upload should work now! ✅

---

## 🌐 PART 3: Configure Custom Domain (15 minutes)

### **Step 1: Add Domain to Vercel**

1. Go to Vercel dashboard
2. Click on your project
3. Go to **"Settings"** → **"Domains"**
4. Click **"Add"**
5. Enter: `www.infignity.com`
6. Vercel will show you DNS records to add

**Vercel will show something like:**
```
Type: CNAME
Name: www
Value: cname.vercel-dns.com
```

### **Step 2: Update DNS at Hostinger**

1. **Login to Hostinger:** https://hpanel.hostinger.com
2. Go to **"Domains"** → Select `infignity.com`
3. Click **"DNS / Name Servers"**
4. Click **"Manage"** or **"DNS Zone"**

**Add/Update these records:**

```
Type: CNAME
Name: www
Points to: cname.vercel-dns.com
TTL: 3600
```

**Optional - Redirect root domain:**
```
Type: A
Name: @
Points to: 76.76.21.21 (Vercel's IP)
TTL: 3600
```

5. Click **"Save"** or **"Add Record"**

### **Step 3: Configure Path-Based Routing**

Since you want `www.infignity.com/supabase_csv_upload`, you have two options:

**Option A: Subdomain (Recommended)**

Use: `csv-upload.infignity.com` instead

In Hostinger DNS:
```
Type: CNAME
Name: csv-upload
Points to: cname.vercel-dns.com
```

In Vercel, add domain: `csv-upload.infignity.com`

**Option B: Path-Based (Requires Main Site)**

If you have a main site at `www.infignity.com`, add this to your main site's config:

```nginx
# Nginx config
location /supabase_csv_upload {
    proxy_pass https://csv-upload-frontend.vercel.app;
}
```

Or use Vercel's rewrites in `vercel.json`:

```json
{
  "rewrites": [
    {
      "source": "/supabase_csv_upload/:path*",
      "destination": "/:path*"
    }
  ]
}
```

### **Step 4: Wait for DNS Propagation**

- DNS changes take 5-60 minutes
- Check status: https://dnschecker.org
- Enter: `www.infignity.com`

---

## ✅ PART 4: Final Configuration

### **Update CORS in Backend**

Go to Railway dashboard:

1. Click on your project
2. Go to **"Variables"**
3. Add:

```
ALLOWED_ORIGINS=https://www.infignity.com,https://csv-upload.infignity.com
```

Then update `api_server.py` (redeploy via git push):

```python
import os

app.add_middleware(
    CORSMiddleware,
    allow_origins=os.getenv("ALLOWED_ORIGINS", "*").split(","),
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
```

### **Test Everything**

1. **Test Backend:**
   ```bash
   curl https://YOUR-RAILWAY-URL.up.railway.app/api/health
   ```

2. **Test Frontend:**
   ```bash
   curl https://www.infignity.com/supabase_csv_upload
   ```

3. **Test Upload:**
   - Go to your URL
   - Upload a CSV file
   - Check Supabase for data

---

## 💰 Cost Breakdown

### **Vercel (Frontend)**
- ✅ **FREE** for personal projects
- 100 GB bandwidth/month
- Unlimited deployments
- Custom domain included

### **Railway (Backend)**
- ✅ **$5 FREE credit/month**
- ~500 hours of runtime
- 100 GB outbound bandwidth
- More than enough for your use case!

**Total Cost: $0/month** (Railway free tier covers everything)

---

## 🔧 Maintenance

### **Update Backend:**
```bash
cd /Users/stagnator/Downloads/orca-ven-backend-main
git add .
git commit -m "Update backend"
git push
# Railway auto-deploys!
```

### **Update Frontend:**
```bash
cd frontend
npm run build
vercel --prod
# Vercel auto-deploys!
```

---

## 📊 Monitoring

### **Railway Dashboard:**
- View logs: Railway dashboard → Logs
- View metrics: Railway dashboard → Metrics
- View deployments: Railway dashboard → Deployments

### **Vercel Dashboard:**
- View analytics: Vercel dashboard → Analytics
- View logs: Vercel dashboard → Logs
- View deployments: Vercel dashboard → Deployments

---

## 🆘 Troubleshooting

### **Backend not responding:**
```bash
# Check Railway logs
railway logs

# Check health endpoint
curl https://YOUR-RAILWAY-URL.up.railway.app/api/health
```

### **Frontend CORS error:**
- Check Railway environment variables
- Verify ALLOWED_ORIGINS includes your domain
- Redeploy backend

### **Domain not working:**
- Check DNS propagation: https://dnschecker.org
- Verify CNAME record in Hostinger
- Wait 5-60 minutes for DNS to update

### **Upload fails:**
- Check browser console (F12)
- Verify API_URL in App.jsx
- Check Railway logs for errors

---

## 🎯 Quick Commands Summary

```bash
# Deploy Backend (Railway)
git push origin main

# Deploy Frontend (Vercel)
cd frontend
npm run build
vercel --prod

# Check Backend Health
curl https://YOUR-RAILWAY-URL.up.railway.app/api/health

# View Railway Logs
railway logs

# View Vercel Logs
vercel logs
```

---

## ✅ Checklist

**Backend (Railway):**
- [ ] GitHub repo created
- [ ] Deployed to Railway
- [ ] Environment variables added
- [ ] Domain generated
- [ ] Health check passes

**Frontend (Vercel):**
- [ ] API_URL updated in App.jsx
- [ ] Built successfully
- [ ] Deployed to Vercel
- [ ] Domain added
- [ ] Site loads correctly

**DNS (Hostinger):**
- [ ] CNAME record added
- [ ] DNS propagated
- [ ] Domain resolves correctly

**Testing:**
- [ ] Backend health check works
- [ ] Frontend loads
- [ ] File upload works
- [ ] Data appears in Supabase

---

## 🚀 You're Live!

Your CSV upload system is now live at:
- **Frontend:** https://www.infignity.com/supabase_csv_upload
- **Backend:** https://YOUR-RAILWAY-URL.up.railway.app

**Completely FREE and production-ready!** 🎉

---

## 📞 Need Help?

If you get stuck, tell me:
1. Which step you're on
2. Any error messages
3. Screenshots if helpful

I'll help you debug! 🛠️
