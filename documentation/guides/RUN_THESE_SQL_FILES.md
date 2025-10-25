# 🚀 Setup Instructions - Run These SQL Files

Your Supabase CLI doesn't support the `--file` flag. No problem! Just run the SQL files manually in Supabase.

## 📋 Quick 3-Step Setup (5 minutes)

### Step 1: Open Supabase SQL Editor

Go to: **https://supabase.com/dashboard/project/dcoukhtfcloqpfmijock/sql/new**

---

### Step 2: Run These 3 SQL Files (in order)

#### File 1: Create Tables (16 tables)

1. Open `scripts/create_all_instrument_tables.sql`
2. Copy ALL contents (Cmd+A, Cmd+C)
3. Paste in Supabase SQL Editor
4. Click **"Run"**
5. Wait ~10 seconds
6. ✅ Should see: "Success. No rows returned"

---

#### File 2: Create Functions (16 functions)

1. Open `scripts/create_all_insert_functions.sql`
2. Copy ALL contents (Cmd+A, Cmd+C)
3. Paste in Supabase SQL Editor
4. Click **"Run"**
5. Wait ~15 seconds
6. ✅ Should see: "Success. No rows returned"

---

#### File 3: Setup Cron Jobs (16 cron jobs)

1. Open `scripts/setup_all_instruments_cron.sql`
2. Copy ALL contents (Cmd+A, Cmd+C)
3. Paste in Supabase SQL Editor
4. Click **"Run"**
5. Wait ~20 seconds
6. ✅ Should see a table showing 16 cron jobs

---

### Step 3: Test Everything Works

Run this command in terminal:

```bash
bash scripts/init_all_instruments.sh
```

This will test all 16 combinations and fetch initial data.

---

## ✅ Verification

After running all 3 SQL files, verify in Supabase SQL Editor:

**Check tables:**
```sql
SELECT tablename FROM pg_tables 
WHERE schemaname = 'orca' AND tablename LIKE '%_candles_%'
ORDER BY tablename;
```
**Should return 16 rows**

**Check functions:**
```sql
SELECT routine_name FROM information_schema.routines
WHERE routine_schema = 'public' AND routine_name LIKE 'insert_%_candles_%'
ORDER BY routine_name;
```
**Should return 16 rows**

**Check cron jobs:**
```sql
SELECT jobname, schedule, active FROM cron.job 
WHERE jobname LIKE 'fetch-%'
ORDER BY jobname;
```
**Should return 16 rows**

---

## 🎯 After Setup

Once all 3 SQL files are run and tested:

```bash
# Test all instruments
bash scripts/init_all_instruments.sh

# Check everything is working
bash scripts/test_all.sh
```

You should see:
```
✅ Found 16/16 tables
✅ Found 16/16 functions
✅ Found 16/16 cron jobs
```

---

## 📁 SQL Files Location

The 3 files you need are in:
- `scripts/create_all_instrument_tables.sql`
- `scripts/create_all_insert_functions.sql`
- `scripts/setup_all_instruments_cron.sql`

---

## 💡 Pro Tip

Open all 3 files side by side, then:
1. Copy File 1 → Run in Supabase
2. Copy File 2 → Run in Supabase
3. Copy File 3 → Run in Supabase
4. Run test: `bash scripts/init_all_instruments.sh`

**Total time: ~5 minutes**

---

## 🚨 If You Get Errors

### "Extension not found"
Run this first in Supabase SQL Editor:
```sql
CREATE EXTENSION IF NOT EXISTS pg_cron;
CREATE EXTENSION IF NOT EXISTS http;
```

### "Schema does not exist"
Run this first:
```sql
CREATE SCHEMA IF NOT EXISTS orca;
```

### "Permission denied"
Make sure you're using your **Supabase account that owns the project**

---

## 🎉 Success Looks Like

After running all SQL + test script:

```
✅ 16 tables created
✅ 16 RPC functions created
✅ 16 cron jobs scheduled
✅ NQ: 10 candles stored
✅ MNQ: 10 candles stored
✅ ES: 10 candles stored
✅ MES: 10 candles stored
```

Then data auto-updates every 5/15/30/60 minutes! 🚀
