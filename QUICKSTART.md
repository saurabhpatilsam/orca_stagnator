# 🚀 Quick Start Guide - CSV Upload System

## ✅ What You Have Now

A complete, production-ready CSV upload system with:
- ✅ **Modern React Frontend** - Beautiful drag-and-drop interface
- ✅ **FastAPI Backend** - REST API for file uploads
- ✅ **Supabase Integration** - Automatic duplicate detection
- ✅ **Ready for www.infignity.com/supabase_csv_upload**

---

## 📁 Files Created

```
frontend/
├── src/
│   ├── App.jsx          # React component with upload UI
│   ├── App.css          # Modern styling
│   └── main.jsx         # Entry point
├── index.html
├── package.json
└── vite.config.js       # Configured for /supabase_csv_upload path

api_server.py            # FastAPI backend
requirements_api.txt     # Python dependencies
DEPLOYMENT_GUIDE.md      # Full deployment instructions
```

---

## 🧪 Test Locally (5 Minutes)

### **Step 1: Start Backend**

```bash
cd /Users/stagnator/Downloads/orca-ven-backend-main

# Install dependencies
pip3 install -r requirements_api.txt

# Start API server
python3 api_server.py
```

Backend runs at: **http://localhost:8000**

### **Step 2: Start Frontend**

Open a new terminal:

```bash
cd /Users/stagnator/Downloads/orca-ven-backend-main/frontend

# Install dependencies
npm install

# Start dev server
npm run dev
```

Frontend runs at: **http://localhost:3000**

### **Step 3: Test Upload**

1. Open http://localhost:3000 in your browser
2. Drag & drop a CSV file or enter file path
3. Select instrument (ES or NQ)
4. Click "Upload to Supabase"
5. Watch the magic happen! ✨

---

## 🎨 Features

### **Frontend Features:**
- ✅ Drag & drop file upload
- ✅ File path input (for server-side files)
- ✅ Instrument selection (ES/NQ)
- ✅ Header detection toggle
- ✅ Duplicate skip toggle
- ✅ Real-time progress tracking
- ✅ Beautiful success/error messages
- ✅ Upload statistics display
- ✅ Responsive design (mobile-friendly)

### **Backend Features:**
- ✅ REST API endpoint
- ✅ File upload handling
- ✅ Server file path support
- ✅ Automatic date range detection
- ✅ Batch processing (1000 rows/batch)
- ✅ Duplicate detection
- ✅ Error handling
- ✅ CORS support

---

## 🌐 Deploy to Production

### **Option 1: Vercel + Railway** ⭐ Easiest

**Backend (Railway):**
```bash
# Install Railway CLI
npm install -g @railway/cli

# Login and deploy
railway login
railway init
railway up
```

**Frontend (Vercel):**
```bash
# Install Vercel CLI
npm install -g vercel

# Deploy
cd frontend
npm run build
vercel --prod
```

**Set custom domain:** `www.infignity.com/supabase_csv_upload`

### **Option 2: Your Own Server**

See `DEPLOYMENT_GUIDE.md` for detailed instructions.

---

## 🔧 Configuration

### **Update API URL**

When deploying, update the API URL in `frontend/src/App.jsx`:

```javascript
// Line ~30
const API_URL = 'https://your-backend-url.com';

// Change fetch call from:
fetch('/api/upload-tick-data', ...)

// To:
fetch(`${API_URL}/api/upload-tick-data`, ...)
```

### **Update CORS**

In `api_server.py`, update allowed origins:

```python
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "https://www.infignity.com",
        "https://infignity.com"
    ],
    ...
)
```

---

## 📊 API Endpoints

### **POST /api/upload-tick-data**

Upload tick data to Supabase.

**Request:**
```bash
curl -X POST http://localhost:8000/api/upload-tick-data \
  -F "file=@ES_data.csv" \
  -F "instrument=ES" \
  -F "has_header=false" \
  -F "skip_duplicates=true"
```

**Response:**
```json
{
  "success": true,
  "message": "Upload completed successfully",
  "total_rows": 1000000,
  "uploaded_rows": 950000,
  "skipped_rows": 50000,
  "error_rows": 0,
  "date_range": {
    "start": "2025-10-01 09:30:00",
    "end": "2025-10-10 16:00:00"
  }
}
```

### **GET /api/health**

Health check endpoint.

**Response:**
```json
{
  "status": "healthy",
  "service": "csv-upload-api"
}
```

---

## 🎯 What I Need From You

To deploy to **www.infignity.com/supabase_csv_upload**, please tell me:

### **1. Hosting Preference**
Which option do you prefer?
- [ ] **Vercel + Railway** (Easiest - I'll give you exact commands)
- [ ] **AWS** (Most scalable - I'll create deployment scripts)
- [ ] **Your own server** (Most control - I'll create setup scripts)
- [ ] **Other:** ___________

### **2. Domain Status**
- [ ] Do you already own **infignity.com**?
- [ ] Do you have access to DNS settings?
- [ ] Do you want a subdomain for the API? (e.g., api.infignity.com)

### **3. Backend Location**
Where should the API run?
- [ ] **Railway** (Recommended - free tier, easy Python)
- [ ] **Heroku**
- [ ] **AWS Lambda**
- [ ] **Your server** (VPS/Dedicated)
- [ ] **Other:** ___________

### **4. Additional Requirements**
- [ ] Do you need authentication? (login/password)
- [ ] Do you need rate limiting? (prevent abuse)
- [ ] Do you need file size limits?
- [ ] Do you need upload history/logs?

---

## 🚀 Next Steps

**Once you tell me your preferences, I'll provide:**

1. ✅ **Exact deployment commands** for your chosen platform
2. ✅ **DNS configuration** for your domain
3. ✅ **SSL setup** (HTTPS)
4. ✅ **Environment variables** setup
5. ✅ **Testing checklist** for production

---

## 📞 Ready to Deploy?

Just tell me:
1. Your hosting preference
2. Whether you own infignity.com
3. Any additional requirements

And I'll give you **step-by-step commands** to get your system live at **www.infignity.com/supabase_csv_upload**! 🎉

---

## 🎨 Preview

Your frontend will look like this:

```
┌─────────────────────────────────────────────────────────┐
│  🗄️  Supabase Tick Data Upload                         │
│  Upload ES/NQ tick-by-tick data to Supabase            │
├─────────────────────────────────────────────────────────┤
│  [Upload File] [File Path]                             │
│                                                         │
│  ┌───────────────────────────────────────────────┐    │
│  │  📤 Drag & drop your CSV file here            │    │
│  │     or click to browse                        │    │
│  └───────────────────────────────────────────────┘    │
│                                                         │
│  Instrument: [ES ▼]                                    │
│  ☑ File has header row                                │
│  ☑ Skip duplicate rows                                │
│                                                         │
│  [📤 Upload to Supabase]                              │
│                                                         │
│  ✅ Upload completed successfully!                     │
│  Total: 1,000,000 | Uploaded: 950,000 | Skipped: 50,000│
└─────────────────────────────────────────────────────────┘
```

**Beautiful, modern, and production-ready!** 🎉
