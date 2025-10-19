# 🚀 Supabase Serverless Candle Fetcher

## 🎯 **Perfect Solution: No Laptop Required!**

This setup runs **entirely on Supabase's infrastructure**:
- ✅ **Runs 24/7** even when your laptop is off
- ✅ **Auto-scaling** serverless functions
- ✅ **Built-in scheduling** with pg_cron
- ✅ **No maintenance** required
- ✅ **Cost-effective** (free tier available)

---

## 🏗️ **Architecture Overview**

```
┌─────────────────┐    ┌──────────────────┐    ┌─────────────────┐
│   pg_cron       │───▶│   Scheduler      │───▶│  Fetch Candles  │
│  (every minute) │    │  Edge Function   │    │  Edge Function  │
└─────────────────┘    └──────────────────┘    └─────────────────┘
                              │                         │
                              ▼                         ▼
                       ┌──────────────┐         ┌──────────────┐
                       │ Fetch Log    │         │ Tradovate    │
                       │ Table        │         │ WebSocket    │
                       └──────────────┘         └──────────────┘
                                                        │
                                                        ▼
                                                ┌──────────────┐
                                                │ Candle Tables│
                                                │ (orca schema)│
                                                └──────────────┘
```

### **How It Works:**
1. **pg_cron** calls **Scheduler** every minute
2. **Scheduler** checks if it's time to fetch each timeframe
3. **Scheduler** calls **Fetch Candles** function when needed
4. **Fetch Candles** connects to Tradovate and stores data
5. **Everything runs in Supabase cloud** ☁️

---

## 📦 **What's Included**

### **Edge Functions:**
- **`scheduler`** - Manages timing for all timeframes
- **`fetch-candles`** - Fetches and stores candle data

### **Database:**
- **`candle_fetch_log`** - Tracks last fetch times
- **Cron job** - Calls scheduler every minute
- **All existing candle tables** (orca schema)

### **Scripts:**
- **`deploy_supabase_functions.sh`** - One-click deployment
- **`test_functions.sh`** - Test all functions

---

## 🚀 **Quick Deployment**

### **Step 1: Stop Local Daemon**
```bash
./stop_daemon.sh
```

### **Step 2: Deploy to Supabase**
```bash
./deploy_supabase_functions.sh
```

This will:
- ✅ Install Supabase CLI (if needed)
- ✅ Login to Supabase
- ✅ Link to your project
- ✅ Deploy database migration
- ✅ Deploy both Edge Functions
- ✅ Test the functions

### **Step 3: Set Environment Variables**

Go to: **Supabase Dashboard → Project Settings → Edge Functions**

Add these variables:
```
SUPABASE_URL=https://your-project.supabase.co
SUPABASE_SERVICE_ROLE_KEY=your-service-role-key
REDIS_API_URL=your-redis-api-url  
REDIS_API_KEY=your-redis-api-key
```

### **Step 4: Enable pg_cron**

In **Supabase SQL Editor**, run:
```sql
-- Enable pg_cron extension
CREATE EXTENSION IF NOT EXISTS pg_cron;

-- Setup the scheduler cron job
SELECT setup_candle_scheduler();
```

### **Step 5: Verify It's Working**
```bash
./test_functions.sh
```

---

## 🎮 **Management Commands**

### **Deploy Functions:**
```bash
./deploy_supabase_functions.sh
```

### **Test Functions:**
```bash
./test_functions.sh
```

### **View Logs:**
```bash
# Scheduler logs
supabase functions logs scheduler --follow

# Fetch candles logs  
supabase functions logs fetch-candles --follow
```

### **Manual Function Calls:**
```bash
# Test scheduler
supabase functions invoke scheduler --method POST --body '{}'

# Test 5-minute fetch
supabase functions invoke fetch-candles --method POST --body '{"timeframe": 5}'
```

---

## 📊 **Monitoring & Verification**

### **Check Function Status:**
```sql
-- In Supabase SQL Editor
SELECT 
    timeframe,
    last_fetch,
    EXTRACT(EPOCH FROM (NOW() - last_fetch))/60 as minutes_ago
FROM public.candle_fetch_log 
ORDER BY timeframe;
```

### **Check Recent Candles:**
```sql
SELECT 
    '5min' as timeframe,
    COUNT(*) as total,
    MAX(candle_time) as latest,
    EXTRACT(EPOCH FROM (NOW() - MAX(candle_time)))/60 as minutes_old
FROM orca.nq_candles_5min
UNION ALL
SELECT '15min', COUNT(*), MAX(candle_time), EXTRACT(EPOCH FROM (NOW() - MAX(candle_time)))/60 FROM orca.nq_candles_15min
UNION ALL  
SELECT '30min', COUNT(*), MAX(candle_time), EXTRACT(EPOCH FROM (NOW() - MAX(candle_time)))/60 FROM orca.nq_candles_30min
UNION ALL
SELECT '1hour', COUNT(*), MAX(candle_time), EXTRACT(EPOCH FROM (NOW() - MAX(candle_time)))/60 FROM orca.nq_candles_1hour;
```

**Healthy System:**
- 5min candles: < 10 minutes old
- 15min candles: < 20 minutes old
- 30min candles: < 35 minutes old
- 1hour candles: < 65 minutes old

### **Function URLs:**
- **Scheduler**: `https://your-project.supabase.co/functions/v1/scheduler`
- **Fetch Candles**: `https://your-project.supabase.co/functions/v1/fetch-candles`

---

## 🔧 **Configuration**

### **Modify Fetch Intervals:**

Edit the scheduler function (`supabase/functions/scheduler/index.ts`):
```typescript
const SCHEDULES: ScheduleConfig[] = [
  { timeframe: 5, interval_minutes: 5, name: '5min' },     // Every 5 min
  { timeframe: 15, interval_minutes: 15, name: '15min' },  // Every 15 min
  { timeframe: 30, interval_minutes: 30, name: '30min' },  // Every 30 min
  { timeframe: 60, interval_minutes: 60, name: '1hour' }   // Every 60 min
];
```

Then redeploy:
```bash
supabase functions deploy scheduler
```

### **Add New Timeframes:**

1. Add to `SCHEDULES` array in scheduler
2. Add function mapping in fetch-candles
3. Create new RPC function in database
4. Create new table in orca schema

---

## 💰 **Cost Analysis**

### **Supabase Pricing:**
- **Free Tier**: 500,000 Edge Function invocations/month
- **Pro Tier**: $25/month + $2 per 1M invocations

### **Your Usage:**
- **Scheduler**: ~43,800 calls/month (every minute)
- **Fetch Functions**: ~8,760 calls/month (4 timeframes)
- **Total**: ~52,560 calls/month

**Result**: Fits comfortably in **FREE TIER**! 🎉

### **Compared to Alternatives:**
- **Railway**: ~$5/month
- **AWS Lambda**: ~$0.20/month  
- **Vercel**: ~$20/month
- **Supabase**: **FREE** ✅

---

## 🔄 **Migration from Local Daemon**

### **Before Migration:**
```bash
# Check current daemon status
./check_daemon.sh

# Stop daemon
./stop_daemon.sh
```

### **After Migration:**
```bash
# Deploy to Supabase
./deploy_supabase_functions.sh

# Test functions
./test_functions.sh

# Monitor logs
supabase functions logs scheduler --follow
```

### **Rollback (if needed):**
```bash
# Start local daemon again
./start_daemon.sh
```

---

## 🆘 **Troubleshooting**

### **Functions Not Deploying:**
```bash
# Check Supabase CLI
supabase --version

# Re-login
supabase logout
supabase login

# Check project link
supabase projects list
```

### **Scheduler Not Running:**
```sql
-- Check if pg_cron is enabled
SELECT * FROM pg_extension WHERE extname = 'pg_cron';

-- Check cron jobs
SELECT * FROM cron.job WHERE jobname = 'candle-scheduler';

-- Manually setup scheduler
SELECT setup_candle_scheduler();
```

### **No Data Being Fetched:**
```bash
# Check function logs
supabase functions logs fetch-candles

# Test manually
supabase functions invoke fetch-candles --method POST --body '{"timeframe": 5}'

# Check environment variables in dashboard
```

### **Environment Variables Missing:**
1. Go to Supabase Dashboard
2. Project Settings → Edge Functions  
3. Add required variables
4. Redeploy functions

---

## 🎯 **Advantages Over Local Daemon**

| Feature | Local Daemon | Supabase Functions |
|---------|--------------|-------------------|
| **Runs when laptop off** | ❌ No | ✅ Yes |
| **Auto-restart on crash** | ⚠️ Manual | ✅ Automatic |
| **Scaling** | ❌ Single instance | ✅ Auto-scaling |
| **Maintenance** | ❌ Manual updates | ✅ Managed |
| **Cost** | Free (electricity) | ✅ Free tier |
| **Reliability** | ⚠️ Depends on laptop | ✅ Enterprise SLA |
| **Monitoring** | ⚠️ Manual logs | ✅ Built-in dashboard |
| **Global availability** | ❌ Single location | ✅ Global edge |

---

## 📈 **Next Steps After Deployment**

### **Immediate (Today):**
1. ✅ Deploy functions
2. ✅ Set environment variables  
3. ✅ Enable pg_cron
4. ✅ Test functions

### **This Week:**
1. Monitor function logs
2. Verify data consistency
3. Set up alerts (optional)

### **Ongoing:**
1. Check Supabase dashboard monthly
2. Monitor function usage
3. Update functions as needed

---

## 🎊 **Summary**

**Perfect serverless solution:**
- ✅ **TRUE 24/7** operation (laptop independent)
- ✅ **FREE** on Supabase free tier
- ✅ **Auto-scaling** and **auto-restart**
- ✅ **Enterprise reliability**
- ✅ **Built-in monitoring**
- ✅ **Global edge network**

**One command deployment:**
```bash
./deploy_supabase_functions.sh
```

**Your candle data will flow continuously without any laptop dependency!** 🚀

---

## 📞 **Quick Commands Reference**

```bash
# Deploy everything
./deploy_supabase_functions.sh

# Test functions  
./test_functions.sh

# View logs
supabase functions logs scheduler --follow

# Manual test
supabase functions invoke scheduler --method POST --body '{}'
```

**Ready to deploy? Run: `./deploy_supabase_functions.sh`** 🎯
