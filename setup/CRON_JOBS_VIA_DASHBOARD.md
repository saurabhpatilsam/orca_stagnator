# 🚀 Setup Cron Jobs via Supabase Dashboard (No SQL Errors!)

## ✅ Easier Method - Use the UI

Instead of SQL, we'll use Supabase's Dashboard UI which is easier and avoids permission errors!

---

## 📋 Step-by-Step Instructions

### 1. Open Supabase Cron Jobs Dashboard

**Link**: https://supabase.com/dashboard/project/dcoukhtfcloqpfmijock/database/cron-jobs

### 2. Create Each Cron Job (16 total)

Click **"Create a new cron job"** for each one below:

---

## 📊 NQ (E-mini Nasdaq) - 4 Jobs

### Job 1: NQ 5-minute
- **Name**: `fetch-nq-5min`
- **Schedule**: `*/5 * * * *`
- **SQL Command**:
```sql
SELECT net.http_post(
    url:='https://dcoukhtfcloqpfmijock.supabase.co/functions/v1/fetch-candles',
    headers:='{"Content-Type": "application/json", "Authorization": "Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6ImRjb3VraHRmY2xvcXBmbWlqb2NrIiwicm9sZSI6InNlcnZpY2Vfcm9sZSIsImlhdCI6MTc1MzcwMTgwMywiZXhwIjoyMDY5Mjc3ODAzfQ.iNzNrB0z64m8cINx0DeVCuAbcStWpMPx_bDos_vgO7w"}'::jsonb,
    body:='{"timeframe": 5, "symbol": "NQZ5"}'::jsonb
) AS request_id;
```

### Job 2: NQ 15-minute
- **Name**: `fetch-nq-15min`
- **Schedule**: `*/15 * * * *`
- **SQL Command**:
```sql
SELECT net.http_post(
    url:='https://dcoukhtfcloqpfmijock.supabase.co/functions/v1/fetch-candles',
    headers:='{"Content-Type": "application/json", "Authorization": "Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6ImRjb3VraHRmY2xvcXBmbWlqb2NrIiwicm9sZSI6InNlcnZpY2Vfcm9sZSIsImlhdCI6MTc1MzcwMTgwMywiZXhwIjoyMDY5Mjc3ODAzfQ.iNzNrB0z64m8cINx0DeVCuAbcStWpMPx_bDos_vgO7w"}'::jsonb,
    body:='{"timeframe": 15, "symbol": "NQZ5"}'::jsonb
) AS request_id;
```

### Job 3: NQ 30-minute
- **Name**: `fetch-nq-30min`
- **Schedule**: `*/30 * * * *`
- **SQL Command**:
```sql
SELECT net.http_post(
    url:='https://dcoukhtfcloqpfmijock.supabase.co/functions/v1/fetch-candles',
    headers:='{"Content-Type": "application/json", "Authorization": "Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6ImRjb3VraHRmY2xvcXBmbWlqb2NrIiwicm9sZSI6InNlcnZpY2Vfcm9sZSIsImlhdCI6MTc1MzcwMTgwMywiZXhwIjoyMDY5Mjc3ODAzfQ.iNzNrB0z64m8cINx0DeVCuAbcStWpMPx_bDos_vgO7w"}'::jsonb,
    body:='{"timeframe": 30, "symbol": "NQZ5"}'::jsonb
) AS request_id;
```

### Job 4: NQ 60-minute
- **Name**: `fetch-nq-60min`
- **Schedule**: `0 * * * *`
- **SQL Command**:
```sql
SELECT net.http_post(
    url:='https://dcoukhtfcloqpfmijock.supabase.co/functions/v1/fetch-candles',
    headers:='{"Content-Type": "application/json", "Authorization": "Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6ImRjb3VraHRmY2xvcXBmbWlqb2NrIiwicm9sZSI6InNlcnZpY2Vfcm9sZSIsImlhdCI6MTc1MzcwMTgwMywiZXhwIjoyMDY5Mjc3ODAzfQ.iNzNrB0z64m8cINx0DeVCuAbcStWpMPx_bDos_vgO7w"}'::jsonb,
    body:='{"timeframe": 60, "symbol": "NQZ5"}'::jsonb
) AS request_id;
```

---

## 📊 MNQ (Micro E-mini Nasdaq) - 4 Jobs

### Job 5: MNQ 5-minute
- **Name**: `fetch-mnq-5min`
- **Schedule**: `*/5 * * * *`
- **SQL**: Same as NQ but change `"symbol": "MNQZ5"`

### Job 6: MNQ 15-minute
- **Name**: `fetch-mnq-15min`
- **Schedule**: `*/15 * * * *`
- **SQL**: Same as NQ but change `"symbol": "MNQZ5"`

### Job 7: MNQ 30-minute
- **Name**: `fetch-mnq-30min`
- **Schedule**: `*/30 * * * *`
- **SQL**: Same as NQ but change `"symbol": "MNQZ5"`

### Job 8: MNQ 60-minute
- **Name**: `fetch-mnq-60min`
- **Schedule**: `0 * * * *`
- **SQL**: Same as NQ but change `"symbol": "MNQZ5"`

---

## 📊 ES (E-mini S&P 500) - 4 Jobs

### Job 9-12: ES (All timeframes)
Same pattern, use `"symbol": "ESZ5"`

---

## 📊 MES (Micro E-mini S&P 500) - 4 Jobs

### Job 13-16: MES (All timeframes)
Same pattern, use `"symbol": "MESZ5"`

---

## ⏱️ Quick Reference - Schedules

| Timeframe | Schedule Cron | Meaning |
|-----------|--------------|---------|
| 5 min | `*/5 * * * *` | Every 5 minutes |
| 15 min | `*/15 * * * *` | Every 15 minutes |
| 30 min | `*/30 * * * *` | Every 30 minutes |
| 60 min | `0 * * * *` | Every hour (on the hour) |

---

## 🎯 Complete SQL Template

For each job, use this template and change the **symbol** and **timeframe**:

```sql
SELECT net.http_post(
    url:='https://dcoukhtfcloqpfmijock.supabase.co/functions/v1/fetch-candles',
    headers:='{"Content-Type": "application/json", "Authorization": "Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6ImRjb3VraHRmY2xvcXBmbWlqb2NrIiwicm9sZSI6InNlcnZpY2Vfcm9sZSIsImlhdCI6MTc1MzcwMTgwMywiZXhwIjoyMDY5Mjc3ODAzfQ.iNzNrB0z64m8cINx0DeVCuAbcStWpMPx_bDos_vgO7w"}'::jsonb,
    body:='{"timeframe": [5|15|30|60], "symbol": "[NQZ5|MNQZ5|ESZ5|MESZ5]"}'::jsonb
) AS request_id;
```

---

## ✅ After Creating All 16 Jobs

You should see all jobs listed:
- ✅ 4 NQ jobs
- ✅ 4 MNQ jobs
- ✅ 4 ES jobs
- ✅ 4 MES jobs

**Total**: 16 automated data collection streams running 24/7!

---

## 🔍 Verify

After 5-10 minutes, check data is collecting:

```sql
SELECT 
    'NQ 5min' as stream, COUNT(*) as rows FROM orca.nq_candles_5min
UNION ALL
SELECT 'MNQ 5min', COUNT(*) FROM orca.mnq_candles_5min
UNION ALL
SELECT 'ES 5min', COUNT(*) FROM orca.es_candles_5min
UNION ALL
SELECT 'MES 5min', COUNT(*) FROM orca.mes_candles_5min;
```

Rows should be growing!
