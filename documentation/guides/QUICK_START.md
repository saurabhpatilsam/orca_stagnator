# Quick Start - One Command Setup

## 🚀 Setup Everything in One Command

Run this single command to set up all 4 instruments with all 4 timeframes:

```bash
bash scripts/setup_complete.sh
```

This one command will:
1. ✅ Create 16 database tables (NQ, MNQ, ES, MES × 4 timeframes)
2. ✅ Create 16 RPC insert functions
3. ✅ Set up 16 cron jobs (auto-updating every 5/15/30/60 min)
4. ✅ Test all 16 combinations
5. ✅ Fetch initial data for all instruments
6. ✅ Verify everything is working

**Time to complete**: 2-3 minutes

---

## ✅ Test Everything

After setup, test that everything is working:

```bash
bash scripts/test_all.sh
```

This will check:
- ✅ All 16 tables created
- ✅ All 16 RPC functions created
- ✅ All 16 cron jobs scheduled
- ✅ Data is being stored in each table

---

## 📊 What Gets Created

### Instruments (4)
1. **NQ** - E-mini Nasdaq (NQZ5)
2. **MNQ** - Micro E-mini Nasdaq (MNQZ5)
3. **ES** - E-mini S&P 500 (ESZ5)
4. **MES** - Micro E-mini S&P 500 (MESZ5)

### Timeframes (4)
- 5 minutes
- 15 minutes
- 30 minutes
- 1 hour

### Total Data Streams: 16

---

## 🧪 View Data in Supabase

Go to: https://supabase.com/dashboard/project/dcoukhtfcloqpfmijock/sql/new

**Check all tables:**
```sql
SELECT tablename FROM pg_tables 
WHERE schemaname = 'orca' AND tablename LIKE '%_candles_%'
ORDER BY tablename;
```

**View MNQ data:**
```sql
SELECT 
    symbol,
    candle_time,
    open,
    high,
    low,
    close,
    volume
FROM orca.mnq_candles_5min
ORDER BY candle_time DESC
LIMIT 10;
```

**Check NQ data:**
```sql
SELECT * FROM orca.nq_candles_5min ORDER BY candle_time DESC LIMIT 10;
```

**Check ES data:**
```sql
SELECT * FROM orca.es_candles_5min ORDER BY candle_time DESC LIMIT 10;
```

**Check MES data:**
```sql
SELECT * FROM orca.mes_candles_5min ORDER BY candle_time DESC LIMIT 10;
```

**Check all cron jobs:**
```sql
SELECT 
    jobname,
    schedule,
    active,
    CASE 
        WHEN schedule = '*/5 * * * *' THEN 'Every 5 minutes'
        WHEN schedule = '*/15 * * * *' THEN 'Every 15 minutes'
        WHEN schedule = '*/30 * * * *' THEN 'Every 30 minutes'
        WHEN schedule = '0 * * * *' THEN 'Every hour'
    END as frequency
FROM cron.job 
WHERE jobname LIKE 'fetch-%'
ORDER BY jobname;
```

**Check row counts:**
```sql
SELECT 
    'NQ 5min' as table_name, COUNT(*) as rows FROM orca.nq_candles_5min
UNION ALL
SELECT 'MNQ 5min', COUNT(*) FROM orca.mnq_candles_5min
UNION ALL
SELECT 'ES 5min', COUNT(*) FROM orca.es_candles_5min
UNION ALL
SELECT 'MES 5min', COUNT(*) FROM orca.mes_candles_5min
ORDER BY table_name;
```

---

## 🔄 What Happens After Setup

Once setup is complete:

### Automatic Updates
- **5-minute candles**: Update every 5 minutes
- **15-minute candles**: Update every 15 minutes
- **30-minute candles**: Update every 30 minutes
- **1-hour candles**: Update every hour

### For All Instruments
- NQ (E-mini Nasdaq)
- MNQ (Micro E-mini Nasdaq)
- ES (E-mini S&P 500)
- MES (Micro E-mini S&P 500)

### Token Management
- Tokens auto-refresh every 50 minutes (local cron)
- No manual intervention needed

---

## 📈 Expected Data Volume

### Per Day (per instrument)
- 5-minute: ~288 candles
- 15-minute: ~96 candles
- 30-minute: ~48 candles
- 1-hour: ~24 candles

**Total**: ~456 candles per instrument per day
**All instruments**: ~1,824 candles per day

---

## 🚨 Troubleshooting

### If setup fails:

1. **Check Supabase CLI is installed:**
   ```bash
   supabase --version
   ```
   
2. **Login to Supabase:**
   ```bash
   supabase login
   ```

3. **Verify project access:**
   ```bash
   supabase projects list
   ```

4. **Run setup again:**
   ```bash
   bash scripts/setup_complete.sh
   ```

### If no data appears:

1. **Check tokens are valid:**
   ```bash
   python3 token_generator_and_redis_manager.py
   ```

2. **Verify market is open:**
   - Futures market: Sunday 6PM ET to Friday 5PM ET

3. **Test manually:**
   ```bash
   bash scripts/init_all_instruments.sh
   ```

4. **Check cron jobs are running:**
   ```bash
   bash scripts/test_all.sh
   ```

---

## 📁 Files Used

The setup script uses these files:
- `scripts/create_all_instrument_tables.sql` - Creates 16 tables
- `scripts/create_all_insert_functions.sql` - Creates 16 functions
- `scripts/setup_all_instruments_cron.sql` - Creates 16 cron jobs
- `scripts/init_all_instruments.sh` - Tests all instruments

---

## ✅ Success Indicators

After running `bash scripts/setup_complete.sh`, you should see:

```
✅ Tables created successfully
✅ RPC functions created successfully
✅ Cron jobs scheduled successfully
✅ All 16 tables found
✅ All 16 functions found
✅ All 16 cron jobs scheduled
✅ Setup Complete! All systems operational
```

Then check data:
```bash
bash scripts/test_all.sh
```

Should show:
```
✅ Found 16/16 tables
✅ Found 16/16 functions
✅ Found 16/16 cron jobs
NQ: X candles
MNQ: X candles
ES: X candles
MES: X candles
✅ All systems operational!
```

---

## 🎯 That's It!

One command sets up everything:
```bash
bash scripts/setup_complete.sh
```

One command tests everything:
```bash
bash scripts/test_all.sh
```

Your candlestick data is now streaming live for all 4 instruments! 🎉
