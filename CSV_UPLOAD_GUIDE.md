# CSV Upload Guide for Tick Data

## Overview

This guide shows you how to upload historical tick data CSV files to Supabase for backtesting.

## Table Structure

You have two tick data tables in Supabase:

### 1. `ticks_nq` (NQ/Nasdaq data) ✅ Already exists
### 2. `ticks_es` (ES/S&P 500 data) ✅ Just created

Both tables have the same structure:

| Column | Type | Description |
|--------|------|-------------|
| `id` | BIGSERIAL | Auto-generated ID |
| `ts` | TIMESTAMP WITH TIME ZONE | Timestamp of the tick |
| `bid` | DOUBLE PRECISION | Bid price |
| `ask` | DOUBLE PRECISION | Ask price |
| `last` | DOUBLE PRECISION | Last traded price |
| `vol` | INTEGER | Volume |

## CSV File Format

Your CSV file should have these columns (in any order):

```csv
ts,bid,ask,last,vol
2025-10-09 09:30:00+00,21000.25,21000.50,21000.25,10
2025-10-09 09:30:01+00,21000.50,21000.75,21000.50,5
2025-10-09 09:30:02+00,21000.75,21001.00,21000.75,8
...
```

### Column Details:

- **ts**: Timestamp in format `YYYY-MM-DD HH:MM:SS+00` (UTC timezone)
- **bid**: Bid price (decimal)
- **ask**: Ask price (decimal)
- **last**: Last traded price (decimal) - **This is the main price used in backtesting**
- **vol**: Volume (integer)

## Method 1: Upload via Supabase Dashboard (Easiest)

### Step 1: Prepare Your CSV

Make sure your CSV has the correct columns:
```csv
ts,bid,ask,last,vol
2025-10-09 09:30:00+00,21000.25,21000.50,21000.25,10
2025-10-09 09:30:01+00,21000.50,21000.75,21000.50,5
```

### Step 2: Go to Supabase Dashboard

1. Open: https://supabase.com/dashboard/project/dcoukhtfcloqpfmijock
2. Click **Table Editor** in the left sidebar
3. Select the table:
   - For ES data: Select `ticks_es`
   - For NQ data: Select `ticks_nq`

### Step 3: Import CSV

1. Click the **"Insert"** dropdown → **"Import data from CSV"**
2. Upload your CSV file
3. Map the columns:
   - CSV `ts` → Table `ts`
   - CSV `bid` → Table `bid`
   - CSV `ask` → Table `ask`
   - CSV `last` → Table `last`
   - CSV `vol` → Table `vol`
4. Click **"Import"**

### Step 4: Verify Upload

```sql
-- Check how many rows were imported
SELECT COUNT(*) FROM ticks_es;

-- View sample data
SELECT * FROM ticks_es ORDER BY ts DESC LIMIT 10;

-- Check date range
SELECT 
    MIN(ts) as first_tick,
    MAX(ts) as last_tick,
    COUNT(*) as total_ticks
FROM ticks_es;
```

## Method 2: Upload via Python Script

Create a file `upload_tick_data.py`:

```python
import pandas as pd
from supabase import create_client
import os
from dotenv import load_dotenv

load_dotenv()

# Initialize Supabase
supabase = create_client(
    os.getenv("SUPABASE_URL"),
    os.getenv("SUPABASE_KEY")
)

# Read CSV file
csv_file = "es_tick_data_2025-10-09.csv"
df = pd.read_csv(csv_file)

print(f"Loaded {len(df)} rows from {csv_file}")

# Convert to list of dicts
records = df.to_dict('records')

# Upload in batches (Supabase has a limit per request)
batch_size = 1000
total_uploaded = 0

for i in range(0, len(records), batch_size):
    batch = records[i:i+batch_size]
    
    try:
        response = supabase.table('ticks_es').insert(batch).execute()
        total_uploaded += len(batch)
        print(f"Uploaded {total_uploaded}/{len(records)} rows...")
    except Exception as e:
        print(f"Error uploading batch {i}: {e}")

print(f"✅ Upload complete! Total rows: {total_uploaded}")
```

Run it:
```bash
python3 upload_tick_data.py
```

## Method 3: Using Staging Table (For Large Files)

For very large CSV files, use the staging table approach:

### Step 1: Upload to Staging Table

```sql
-- Upload CSV to staging_ticks_es via Supabase dashboard
-- This table accepts all columns as TEXT (no validation)
```

### Step 2: Transform and Insert

```sql
-- Transform and insert into main table
INSERT INTO ticks_es (ts, bid, ask, last, vol)
SELECT 
    raw_ts::timestamp with time zone,
    bid::double precision,
    ask::double precision,
    last::double precision,
    vol::integer
FROM staging_ticks_es
WHERE raw_ts IS NOT NULL
  AND last IS NOT NULL;

-- Clear staging table
TRUNCATE staging_ticks_es;
```

## CSV Format Examples

### Example 1: Minimal Format (Only Required Fields)

```csv
ts,last
2025-10-09 09:30:00+00,21000.25
2025-10-09 09:30:01+00,21000.50
2025-10-09 09:30:02+00,21000.75
```

### Example 2: Full Format (All Fields)

```csv
ts,bid,ask,last,vol
2025-10-09 09:30:00+00,21000.00,21000.50,21000.25,10
2025-10-09 09:30:01+00,21000.25,21000.75,21000.50,5
2025-10-09 09:30:02+00,21000.50,21001.00,21000.75,8
```

### Example 3: Different Timestamp Format

If your CSV has timestamps in a different format, convert them:

```python
import pandas as pd

# Read CSV
df = pd.read_csv('tick_data.csv')

# Convert timestamp format
df['ts'] = pd.to_datetime(df['timestamp']).dt.tz_localize('America/New_York').dt.tz_convert('UTC')

# Save with correct format
df[['ts', 'bid', 'ask', 'last', 'vol']].to_csv('tick_data_formatted.csv', index=False)
```

## Verifying Your Upload

### Check Data Quality

```sql
-- Check for missing prices
SELECT COUNT(*) as missing_prices
FROM ticks_es
WHERE last IS NULL;

-- Check date range
SELECT 
    DATE(ts) as date,
    COUNT(*) as tick_count,
    MIN(last) as min_price,
    MAX(last) as max_price
FROM ticks_es
GROUP BY DATE(ts)
ORDER BY date;

-- Check for duplicates
SELECT ts, COUNT(*) as count
FROM ticks_es
GROUP BY ts
HAVING COUNT(*) > 1;
```

### Test with Backtester

```bash
# Run backtest to verify data works
python3 backtest.py

# Enter the date you uploaded
Enter test date (YYYY-MM-DD): 2025-10-09
Enter instrument: ESZ5
```

## Common Issues and Solutions

### Issue 1: "Timestamp format error"

**Problem**: CSV timestamp format doesn't match expected format

**Solution**: Convert timestamps to ISO format with timezone:
```python
df['ts'] = pd.to_datetime(df['ts']).dt.strftime('%Y-%m-%d %H:%M:%S+00')
```

### Issue 2: "No data found for date"

**Problem**: Timestamps are in wrong timezone

**Solution**: Make sure timestamps are in UTC or properly timezone-aware:
```python
# If your data is in ET (Eastern Time)
df['ts'] = pd.to_datetime(df['ts']).dt.tz_localize('America/New_York').dt.tz_convert('UTC')
```

### Issue 3: "Upload too slow"

**Problem**: Large CSV file takes too long

**Solution**: Use batch upload with larger batches:
```python
batch_size = 5000  # Increase from 1000
```

### Issue 4: "Duplicate key error"

**Problem**: Trying to upload data that already exists

**Solution**: Delete existing data first:
```sql
-- Delete data for specific date
DELETE FROM ticks_es WHERE DATE(ts) = '2025-10-09';

-- Or truncate entire table
TRUNCATE ticks_es;
```

## Data Requirements for Backtesting

For the backtester to work properly, you need:

### Minimum Requirements:
- ✅ Tick data from **10:30 AM ET** (first hour close) to **4:00 PM ET** (market close)
- ✅ At least the `ts` and `last` columns
- ✅ Continuous data (no large gaps)

### Recommended:
- ✅ Tick data from **9:30 AM ET** (market open) onwards
- ✅ All columns: `ts`, `bid`, `ask`, `last`, `vol`
- ✅ Tick frequency: Every second or better

## Example: Complete Upload Workflow

```bash
# 1. Prepare your CSV file
# File: es_2025-10-09.csv
# Format: ts,bid,ask,last,vol

# 2. Upload via Supabase Dashboard
# - Go to Table Editor → ticks_es
# - Click Insert → Import CSV
# - Upload file
# - Map columns
# - Click Import

# 3. Verify upload
# Run in Supabase SQL Editor:
SELECT COUNT(*) FROM ticks_es WHERE DATE(ts) = '2025-10-09';

# 4. Run backtest
python3 backtest.py
# Enter date: 2025-10-09
# Enter instrument: ESZ5

# 5. View results!
```

## Sample Data Download

If you need sample data for testing, you can generate it:

```python
import pandas as pd
from datetime import datetime, timedelta
import random

# Generate sample tick data
start_time = datetime(2025, 10, 9, 9, 30, 0)
end_time = datetime(2025, 10, 9, 16, 0, 0)

ticks = []
current_time = start_time
current_price = 21000.0

while current_time < end_time:
    # Simulate price movement
    price_change = random.uniform(-2, 2)
    current_price += price_change
    
    tick = {
        'ts': current_time.strftime('%Y-%m-%d %H:%M:%S+00'),
        'bid': round(current_price - 0.25, 2),
        'ask': round(current_price + 0.25, 2),
        'last': round(current_price, 2),
        'vol': random.randint(1, 100)
    }
    ticks.append(tick)
    
    # Next tick (every second)
    current_time += timedelta(seconds=1)

# Save to CSV
df = pd.DataFrame(ticks)
df.to_csv('sample_es_ticks_2025-10-09.csv', index=False)
print(f"Generated {len(ticks)} sample ticks")
```

## Next Steps

1. ✅ Prepare your CSV file with tick data
2. ✅ Upload to `ticks_es` (for ES) or `ticks_nq` (for NQ)
3. ✅ Verify the upload with SQL queries
4. ✅ Run backtest with `python3 backtest.py`
5. ✅ Analyze results and optimize strategy!

---

**Your backtester is now ready to use real historical data from Supabase!** 🚀
