# ✅ SETUP NOW - Copy/Paste Method (2 Minutes)

## 🚀 Automated Copy Helper

Run this command - it will open everything you need:

```bash
bash scripts/open_all_files.sh
```

This opens:
1. Supabase SQL Editor (in browser)
2. All 3 SQL files (in text editor)

Then just **copy each file → paste in Supabase → click Run**!

---

## 📋 Manual Method (If needed)

### 1. Open Supabase SQL Editor
https://supabase.com/dashboard/project/dcoukhtfcloqpfmijock/sql/new

### 2. Copy/Paste These 3 Files (in order)

#### File 1: Tables
```bash
open scripts/create_all_instrument_tables.sql
```
- Select All (Cmd+A)
- Copy (Cmd+C)
- Paste in Supabase
- Click "Run"
- ✅ Wait 10 seconds

#### File 2: Functions
```bash
open scripts/create_all_insert_functions.sql
```
- Select All (Cmd+A)
- Copy (Cmd+C)
- Paste in Supabase
- Click "Run"
- ✅ Wait 15 seconds

#### File 3: Cron Jobs
```bash
open scripts/setup_all_instruments_cron.sql
```
- Select All (Cmd+A)
- Copy (Cmd+C)
- Paste in Supabase
- Click "Run"
- ✅ Wait 20 seconds

### 3. Test It
```bash
bash scripts/init_all_instruments.sh
```

Should show:
```
✅ NQ: 10 candles
✅ MNQ: 10 candles
✅ ES: 10 candles
✅ MES: 10 candles
```

---

## ✅ Verification

After running all 3 SQL files, check in Supabase:

```sql
-- Should return 16
SELECT COUNT(*) FROM pg_tables 
WHERE schemaname = 'orca' AND tablename LIKE '%_candles_%';

-- Should return 16
SELECT COUNT(*) FROM information_schema.routines
WHERE routine_schema = 'public' AND routine_name LIKE 'insert_%_candles_%';

-- Should return 16
SELECT COUNT(*) FROM cron.job WHERE jobname LIKE 'fetch-%';
```

---

## 🎉 Done!

Once all 3 SQL files are run:
- ✅ 16 tables created (NQ, MNQ, ES, MES × 4 timeframes)
- ✅ 16 RPC functions created
- ✅ 16 cron jobs scheduled
- ✅ Data auto-updates every 5/15/30/60 minutes

**Total time: 2 minutes** ⚡
