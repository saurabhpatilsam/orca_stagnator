# 🚀 Deployment Guide - CSV Upload Frontend

## 📋 Overview

Deploy your CSV upload system at: **www.infignity.com/supabase_csv_upload**

---

## 🏗️ Architecture

```
┌─────────────────────────────────────────────────────────────┐
│  www.infignity.com/supabase_csv_upload (React Frontend)    │
└─────────────────────────────────────────────────────────────┘
                           ↓
┌─────────────────────────────────────────────────────────────┐
│  api.infignity.com/api/upload-tick-data (FastAPI Backend)  │
└─────────────────────────────────────────────────────────────┘
                           ↓
┌─────────────────────────────────────────────────────────────┐
│  Supabase (PostgreSQL Database)                             │
└─────────────────────────────────────────────────────────────┘
```

---

## 📁 Project Structure

```
orca-ven-backend-main/
├── frontend/                    # React frontend
│   ├── src/
│   │   ├── App.jsx             # Main component
│   │   ├── App.css             # Styles
│   │   └── main.jsx            # Entry point
│   ├── index.html
│   ├── package.json
│   └── vite.config.js
├── api_server.py               # FastAPI backend
├── upload_tick_data.py         # Upload logic
└── DEPLOYMENT_GUIDE.md         # This file
```

---

## 🛠️ Prerequisites

Before deployment, I need to know:

### **1. Hosting Platform**
Where do you want to host?
- [ ] Vercel (Recommended for frontend)
- [ ] Netlify
- [ ] AWS (S3 + CloudFront)
- [ ] Your own server (VPS/Dedicated)
- [ ] Other: ___________

### **2. Backend Hosting**
Where will the API run?
- [ ] Railway (Recommended - easy Python deployment)
- [ ] Heroku
- [ ] AWS EC2/Lambda
- [ ] DigitalOcean
- [ ] Your own server
- [ ] Other: ___________

### **3. Domain Configuration**
- [ ] Do you already own infignity.com?
- [ ] Do you have access to DNS settings?
- [ ] Do you want a subdomain (api.infignity.com) for the backend?

### **4. SSL Certificate**
- [ ] Do you need SSL (HTTPS)? (Recommended: Yes)
- [ ] Will you use Let's Encrypt (free)?
- [ ] Or do you have your own certificate?

---

## 🚀 Deployment Steps

### **Option 1: Vercel (Frontend) + Railway (Backend)** ⭐ Recommended

This is the easiest and fastest option!

#### **Step 1: Deploy Backend to Railway**

1. **Install Railway CLI:**
   ```bash
   npm install -g @railway/cli
   ```

2. **Login to Railway:**
   ```bash
   railway login
   ```

3. **Create new project:**
   ```bash
   cd /Users/stagnator/Downloads/orca-ven-backend-main
   railway init
   ```

4. **Add environment variables:**
   ```bash
   railway variables set SUPABASE_URL="your_supabase_url"
   railway variables set SUPABASE_KEY="your_supabase_key"
   ```

5. **Deploy:**
   ```bash
   railway up
   ```

6. **Get your backend URL:**
   ```bash
   railway domain
   # Example: https://your-app.railway.app
   ```

#### **Step 2: Deploy Frontend to Vercel**

1. **Install Vercel CLI:**
   ```bash
   npm install -g vercel
   ```

2. **Navigate to frontend:**
   ```bash
   cd frontend
   npm install
   ```

3. **Update API endpoint in App.jsx:**
   ```javascript
   // Replace '/api' with your Railway backend URL
   const API_URL = 'https://your-app.railway.app';
   ```

4. **Build frontend:**
   ```bash
   npm run build
   ```

5. **Deploy to Vercel:**
   ```bash
   vercel --prod
   ```

6. **Configure custom domain:**
   - Go to Vercel dashboard
   - Click on your project
   - Go to "Settings" → "Domains"
   - Add: `infignity.com/supabase_csv_upload`

---

### **Option 2: AWS (S3 + CloudFront + Lambda)**

#### **Frontend (S3 + CloudFront):**

1. **Build frontend:**
   ```bash
   cd frontend
   npm install
   npm run build
   ```

2. **Upload to S3:**
   ```bash
   aws s3 sync dist/ s3://infignity.com/supabase_csv_upload/ --acl public-read
   ```

3. **Configure CloudFront:**
   - Create CloudFront distribution
   - Set origin to S3 bucket
   - Set path pattern: `/supabase_csv_upload/*`
   - Enable HTTPS

4. **Update DNS:**
   - Add CNAME record: `www.infignity.com` → CloudFront domain

#### **Backend (Lambda + API Gateway):**

1. **Create Lambda function:**
   ```bash
   cd /Users/stagnator/Downloads/orca-ven-backend-main
   pip install -t ./package -r requirements.txt
   cd package
   zip -r ../deployment.zip .
   cd ..
   zip -g deployment.zip api_server.py upload_tick_data.py
   ```

2. **Upload to Lambda:**
   ```bash
   aws lambda create-function \
     --function-name csv-upload-api \
     --runtime python3.9 \
     --handler api_server.handler \
     --zip-file fileb://deployment.zip
   ```

3. **Create API Gateway:**
   - Create REST API
   - Add resource: `/api/upload-tick-data`
   - Link to Lambda function
   - Deploy to stage

---

### **Option 3: Your Own Server (VPS/Dedicated)**

#### **Frontend (Nginx):**

1. **Build frontend:**
   ```bash
   cd frontend
   npm install
   npm run build
   ```

2. **Copy to server:**
   ```bash
   scp -r dist/* user@your-server:/var/www/infignity.com/supabase_csv_upload/
   ```

3. **Configure Nginx:**
   ```nginx
   server {
       listen 80;
       server_name www.infignity.com;
       
       location /supabase_csv_upload {
           alias /var/www/infignity.com/supabase_csv_upload;
           try_files $uri $uri/ /supabase_csv_upload/index.html;
       }
       
       location /api {
           proxy_pass http://localhost:8000;
           proxy_set_header Host $host;
           proxy_set_header X-Real-IP $remote_addr;
       }
   }
   ```

4. **Enable SSL (Let's Encrypt):**
   ```bash
   sudo certbot --nginx -d www.infignity.com
   ```

#### **Backend (Systemd Service):**

1. **Copy files to server:**
   ```bash
   scp api_server.py upload_tick_data.py user@your-server:/opt/csv-upload/
   ```

2. **Install dependencies:**
   ```bash
   ssh user@your-server
   cd /opt/csv-upload
   pip3 install -r requirements.txt
   ```

3. **Create systemd service:**
   ```bash
   sudo nano /etc/systemd/system/csv-upload.service
   ```

   ```ini
   [Unit]
   Description=CSV Upload API
   After=network.target

   [Service]
   Type=simple
   User=www-data
   WorkingDirectory=/opt/csv-upload
   Environment="SUPABASE_URL=your_url"
   Environment="SUPABASE_KEY=your_key"
   ExecStart=/usr/bin/python3 api_server.py
   Restart=always

   [Install]
   WantedBy=multi-user.target
   ```

4. **Start service:**
   ```bash
   sudo systemctl daemon-reload
   sudo systemctl enable csv-upload
   sudo systemctl start csv-upload
   ```

---

## 🔧 Configuration

### **Environment Variables**

Create `.env` file:

```bash
# Supabase
SUPABASE_URL=https://your-project.supabase.co
SUPABASE_KEY=your_supabase_anon_key

# Redis (if needed)
REDIS_HOST=your-redis-host
REDIS_PORT=6380
REDIS_PASSWORD=your-redis-password

# API
API_PORT=8000
API_HOST=0.0.0.0
```

### **CORS Configuration**

Update `api_server.py`:

```python
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "https://www.infignity.com",
        "https://infignity.com"
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
```

---

## 📦 Dependencies

### **Frontend:**
```json
{
  "react": "^18.2.0",
  "react-dom": "^18.2.0",
  "lucide-react": "^0.263.1",
  "vite": "^4.4.5"
}
```

### **Backend:**
```txt
fastapi==0.104.1
uvicorn==0.24.0
python-multipart==0.0.6
supabase-py==2.0.0
pandas==2.1.3
loguru==0.7.2
python-dotenv==1.0.0
```

---

## 🧪 Testing

### **Local Testing:**

1. **Start backend:**
   ```bash
   python3 api_server.py
   # Runs on http://localhost:8000
   ```

2. **Start frontend:**
   ```bash
   cd frontend
   npm run dev
   # Runs on http://localhost:3000
   ```

3. **Test upload:**
   - Open http://localhost:3000
   - Upload a CSV file
   - Check Supabase for data

### **Production Testing:**

1. **Test frontend:**
   ```bash
   curl https://www.infignity.com/supabase_csv_upload
   ```

2. **Test API:**
   ```bash
   curl https://api.infignity.com/api/health
   ```

3. **Test upload:**
   ```bash
   curl -X POST https://api.infignity.com/api/upload-tick-data \
     -F "file=@test.csv" \
     -F "instrument=ES" \
     -F "has_header=true" \
     -F "skip_duplicates=true"
   ```

---

## 🔒 Security

### **Checklist:**

- [ ] Enable HTTPS (SSL certificate)
- [ ] Set up CORS properly (whitelist your domain)
- [ ] Use environment variables for secrets
- [ ] Add rate limiting to API
- [ ] Implement authentication (optional)
- [ ] Set up firewall rules
- [ ] Enable DDoS protection
- [ ] Regular security updates

### **Rate Limiting (Optional):**

```python
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address

limiter = Limiter(key_func=get_remote_address)
app.state.limiter = limiter

@app.post("/api/upload-tick-data")
@limiter.limit("10/minute")
async def upload_tick_data(...):
    ...
```

---

## 📊 Monitoring

### **Health Checks:**

```bash
# Backend health
curl https://api.infignity.com/api/health

# Frontend health
curl https://www.infignity.com/supabase_csv_upload
```

### **Logs:**

```bash
# Railway
railway logs

# Your server
sudo journalctl -u csv-upload -f
```

---

## 🎯 Next Steps

**Tell me:**

1. **Which hosting option do you prefer?**
   - Vercel + Railway (easiest)
   - AWS (most scalable)
   - Your own server (most control)

2. **Do you already have:**
   - Domain registered? (infignity.com)
   - DNS access?
   - Hosting account?

3. **Do you need help with:**
   - Domain setup?
   - SSL certificate?
   - DNS configuration?
   - Deployment scripts?

**Once you tell me your preferences, I'll provide exact step-by-step commands for your specific setup!** 🚀
