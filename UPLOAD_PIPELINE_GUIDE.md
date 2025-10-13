# CSV Upload Pipeline - Complete Guide

## Overview

The CSV upload pipeline automatically uploads tick-by-tick data from CSV files to Supabase with:

✅ **Auto-detection** - Automatically detects date range from CSV  
✅ **Duplicate Prevention** - Skips rows that already exist in database  
✅ **Batch Processing** - Handles large files (100MB+) efficiently  
✅ **Progress Tracking** - Shows real-time upload progress  
✅ **Error Handling** - Continues on errors, reports at end  
✅ **Verification** - Confirms data uploaded correctly  

## Quick Start

### Basic Usage

```bash
# Run the upload script
python3 upload_tick_data.py

# Follow the prompts:
Enter CSV file path: ~/Downloads/es.csv
Enter instrument (ES or NQ): ES
Skip duplicate rows? (y/n) [default: y]: y
```

### Example with Default Path

```bash
# Place your CSV file at ~/Downloads/es.csv
python3 upload_tick_data.py

# Press Enter to use default path
Enter CSV file path (or press Enter for default): [Press Enter]
Enter instrument (ES or NQ): ES
Skip duplicate rows? (y/n): y
```

## CSV File Requirements

### Required Columns

Your CSV must have at least:
- **ts** (or timestamp/time/datetime) - Timestamp column
- **last** (or price/last_price) - Price column

### Optional Columns

- **bid** (or bid_price) - Bid price
- **ask** (or ask_price) - Ask price
- **vol** (or volume) - Volume

### Supported CSV Formats

#### Format 1: Standard Format
```csv
ts,bid,ask,last,vol
2025-10-09 09:30:00+00,5900.00,5900.50,5900.25,10
2025-10-09 09:30:01+00,5900.25,5900.75,5900.50,5
```

#### Format 2: Minimal Format
```csv
timestamp,price
2025-10-09 09:30:00,5900.25
2025-10-09 09:30:01,5900.50
```

#### Format 3: Alternative Names
```csv
datetime,bid_price,ask_price,last_price,volume
2025-10-09 09:30:00,5900.00,5900.50,5900.25,10
```

**The script automatically detects and maps column names!**

## How It Works

### Step-by-Step Process

```
1. Read CSV File
   ↓
2. Detect Date Range
   - Read first row → start_date
   - Read last row → end_date
   ↓
3. Load Existing Data
   - Query Supabase for existing timestamps
   - Build set of existing timestamps
   ↓
4. Process in Batches
   - Read 1000 rows at a time
   - Filter out duplicates
   - Upload to Supabase
   ↓
5. Verify Upload
   - Count rows in database
   - Show sample data
```

### Duplicate Detection

The pipeline prevents duplicates by:

1. **Loading existing timestamps** from Supabase for the date range
2. **Comparing each row** against existing timestamps
3. **Skipping duplicates** automatically
4. **Reporting** how many duplicates were found

**Example:**
```
File has: 10,000 rows
Database has: 5,000 rows (same date range)
Duplicates: 5,000 rows
Uploaded: 5,000 new rows
```

## Example Output

### Successful Upload

```
======================================================================
CSV TICK DATA UPLOAD
======================================================================
Target table: ticks_es
File size: 285.5 MB
Total rows: 1,239,632
Columns: ['ts', 'bid', 'ask', 'last', 'vol']

✅ Date range detected:
   Start: 2025-10-01 09:30:00
   End:   2025-10-10 16:00:00
   Total rows: 1,239,632

Loading existing timestamps from ticks_es...
Found 500,000 existing timestamps

Uploading data in batches of 1000...
  ✅ Batch 1: Uploaded 1000 rows (Total: 1,000/1,239,632)
  ✅ Batch 2: Uploaded 1000 rows (Total: 2,000/1,239,632)
  Batch 3: All rows are duplicates, skipping...
  ✅ Batch 4: Uploaded 800 rows (Total: 2,800/1,239,632)
  ...

======================================================================
UPLOAD COMPLETE
======================================================================
Total rows processed: 1,239,632
Uploaded rows:        739,632
Skipped (duplicates): 500,000
Errors:               0
======================================================================

Verifying uploaded data in ticks_es...
✅ Found 1,239,632 rows in Supabase

Sample data:
  {'ts': '2025-10-01T09:30:00+00:00', 'last': 5900.25, 'bid': 5900.0, 'ask': 5900.5, 'vol': 10}
  {'ts': '2025-10-01T09:30:01+00:00', 'last': 5900.5, 'bid': 5900.25, 'ask': 5900.75, 'vol': 5}
```

## Advanced Usage

### Programmatic Usage

```python
from upload_tick_data import TickDataUploader

# Initialize uploader
uploader = TickDataUploader()

# Upload CSV
result = uploader.upload_csv(
    csv_file="/path/to/es_data.csv",
    instrument="ES",
    skip_duplicates=True
)

# Check result
if result['success']:
    print(f"Uploaded {result['uploaded_rows']} rows")
    print(f"Skipped {result['skipped_rows']} duplicates")
else:
    print(f"Error: {result['error']}")
```

### Batch Upload Multiple Files

```python
import os
from upload_tick_data import TickDataUploader

uploader = TickDataUploader()

# Upload all CSV files in a directory
csv_dir = "/path/to/csv_files"
for filename in os.listdir(csv_dir):
    if filename.endswith('.csv'):
        csv_path = os.path.join(csv_dir, filename)
        
        # Detect instrument from filename
        instrument = 'ES' if 'es' in filename.lower() else 'NQ'
        
        print(f"Uploading {filename}...")
        result = uploader.upload_csv(csv_path, instrument)
        
        if result['success']:
            print(f"  ✅ Success: {result['uploaded_rows']} rows")
        else:
            print(f"  ❌ Failed: {result['error']}")
```

### Upload Without Duplicate Check (Faster)

```python
# Skip duplicate detection for faster upload
# Use only if you're sure there are no duplicates
result = uploader.upload_csv(
    csv_file="es_data.csv",
    instrument="ES",
    skip_duplicates=False  # Faster but may create duplicates
)
```

## Performance

### Upload Speed

| File Size | Rows | Time | Speed |
|-----------|------|------|-------|
| 10 MB | 50,000 | ~30 sec | 1,666 rows/sec |
| 100 MB | 500,000 | ~5 min | 1,666 rows/sec |
| 300 MB | 1,500,000 | ~15 min | 1,666 rows/sec |

### Optimization Tips

1. **Use batch size 1000** (default) for best balance
2. **Skip duplicate check** if you're sure there are no duplicates
3. **Upload during off-peak hours** for faster Supabase response
4. **Split very large files** (>500MB) into smaller chunks

## Troubleshooting

### Issue 1: "File not found"

**Problem**: CSV file path is incorrect

**Solution**:
```bash
# Use absolute path
python3 upload_tick_data.py
Enter CSV file path: /Users/yourname/Downloads/es.csv

# Or use ~ for home directory
Enter CSV file path: ~/Downloads/es.csv
```

### Issue 2: "Required column 'ts' not found"

**Problem**: CSV doesn't have timestamp column

**Solution**: Rename your timestamp column to one of:
- `ts`
- `timestamp`
- `time`
- `datetime`

Or edit the CSV:
```csv
# Before
date,price
2025-10-09 09:30:00,5900.25

# After
ts,last
2025-10-09 09:30:00,5900.25
```

### Issue 3: "Could not detect date range"

**Problem**: Timestamp format not recognized

**Solution**: Convert timestamps to standard format:
```python
import pandas as pd

df = pd.read_csv('your_file.csv')
df['ts'] = pd.to_datetime(df['timestamp']).dt.strftime('%Y-%m-%d %H:%M:%S+00')
df.to_csv('formatted_file.csv', index=False)
```

### Issue 4: Upload is slow

**Problem**: Large file or slow network

**Solutions**:
1. Increase batch size:
   ```python
   # Edit upload_tick_data.py
   BATCH_SIZE = 5000  # Increase from 1000
   ```

2. Skip duplicate check:
   ```bash
   Skip duplicate rows? (y/n): n
   ```

3. Split file into smaller chunks:
   ```python
   import pandas as pd
   
   df = pd.read_csv('large_file.csv')
   chunk_size = 500000
   
   for i in range(0, len(df), chunk_size):
       chunk = df[i:i+chunk_size]
       chunk.to_csv(f'chunk_{i//chunk_size}.csv', index=False)
   ```

### Issue 5: "Error uploading batch"

**Problem**: Network error or Supabase limit

**Solution**: The script continues on errors. Check the error count at the end:
```
Errors: 5
```

Re-run the script with duplicate detection enabled - it will only upload the missing rows.

## Verifying Uploads

### Check in Supabase Dashboard

1. Go to: https://supabase.com/dashboard/project/dcoukhtfcloqpfmijock
2. Click **Table Editor** → **ticks_es** (or ticks_nq)
3. View your data

### SQL Queries

```sql
-- Count total rows
SELECT COUNT(*) FROM ticks_es;

-- Count rows for specific date
SELECT COUNT(*) 
FROM ticks_es 
WHERE DATE(ts) = '2025-10-09';

-- View date range
SELECT 
    MIN(ts) as first_tick,
    MAX(ts) as last_tick,
    COUNT(*) as total_ticks
FROM ticks_es;

-- Check for duplicates
SELECT ts, COUNT(*) as count
FROM ticks_es
GROUP BY ts
HAVING COUNT(*) > 1;

-- View sample data
SELECT * FROM ticks_es 
ORDER BY ts DESC 
LIMIT 10;
```

## Best Practices

### 1. Always Use Duplicate Detection

```bash
Skip duplicate rows? (y/n): y  # Always say yes
```

This ensures you can:
- Re-upload files without creating duplicates
- Upload overlapping date ranges
- Fix failed uploads

### 2. Verify After Upload

Always check the upload was successful:
```sql
SELECT COUNT(*) FROM ticks_es WHERE DATE(ts) = '2025-10-09';
```

### 3. Keep Original Files

Don't delete CSV files after upload - keep them as backup.

### 4. Upload in Order

Upload files in chronological order for easier tracking:
```
es_2025-10-01.csv
es_2025-10-02.csv
es_2025-10-03.csv
```

### 5. Test with Small File First

Before uploading a 300MB file, test with a small sample:
```bash
# Create test file with first 1000 rows
head -n 1001 large_file.csv > test_file.csv

# Upload test file
python3 upload_tick_data.py
```

## Integration with Backtester

After uploading data, you can immediately backtest:

```bash
# 1. Upload tick data
python3 upload_tick_data.py
# Upload es_2025-10-09.csv

# 2. Run backtest
python3 backtest.py
# Enter date: 2025-10-09
# Enter instrument: ESZ5

# 3. View results!
```

## Automation

### Daily Upload Script

Create `daily_upload.sh`:

```bash
#!/bin/bash

# Upload today's tick data
DATE=$(date +%Y-%m-%d)
CSV_FILE="~/Downloads/es_${DATE}.csv"

if [ -f "$CSV_FILE" ]; then
    echo "Uploading $CSV_FILE..."
    python3 upload_tick_data.py <<EOF
$CSV_FILE
ES
y
EOF
else
    echo "File not found: $CSV_FILE"
fi
```

Make it executable:
```bash
chmod +x daily_upload.sh
```

Run daily via cron:
```bash
# Edit crontab
crontab -e

# Add this line (runs at 5 PM daily)
0 17 * * * /path/to/daily_upload.sh
```

## Summary

✅ **Easy to use** - Just provide file path and instrument  
✅ **Automatic** - Detects date range and column names  
✅ **Safe** - Prevents duplicates automatically  
✅ **Fast** - Batch processing for large files  
✅ **Reliable** - Error handling and verification  

**Your tick data upload pipeline is ready to use!** 🚀

---

## Quick Reference

```bash
# Basic upload
python3 upload_tick_data.py

# Programmatic upload
from upload_tick_data import TickDataUploader
uploader = TickDataUploader()
result = uploader.upload_csv("file.csv", "ES")

# Verify upload
SELECT COUNT(*) FROM ticks_es WHERE DATE(ts) = '2025-10-09';

# Run backtest
python3 backtest.py
```
