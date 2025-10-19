# Duplicate Data Fix Guide

## 🔴 Problem Identified

You uploaded the same ES tick data twice:
- **First upload**: 7.9M rows
- **Second upload**: 1M rows (from the same file)
- **Result**: 8.9M total rows (should be 7.9M)
- **Issue**: ~1M duplicate rows exist in the database

## 🎯 Root Cause

The duplicate detection in the upload script had two issues:

1. **No database-level constraint**: The `ticks_es` table didn't have a UNIQUE constraint on the `ts` (timestamp) column
2. **Upload script used INSERT instead of UPSERT**: Regular INSERT allows duplicates

## ✅ Solution (2 Steps)

### **Step 1: Clean Existing Duplicates**

Run the SQL script to remove duplicates and add constraints.

#### **How to Execute:**

1. Go to Supabase SQL Editor:
   ```
   https://supabase.com/dashboard/project/dcoukhtfcloqpfmijock
   ```

2. Click **"SQL Editor"** in the left sidebar

3. Click **"New Query"**

4. Copy and paste this SQL:

```sql
-- Remove duplicates from ticks_es (keeps first occurrence)
DELETE FROM ticks_es
WHERE id IN (
    SELECT id
    FROM (
        SELECT 
            id,
            ROW_NUMBER() OVER (PARTITION BY ts ORDER BY id ASC) as row_num
        FROM ticks_es
    ) ranked
    WHERE row_num > 1
);

-- Add UNIQUE constraint to prevent future duplicates
ALTER TABLE ticks_es
ADD CONSTRAINT ticks_es_ts_unique UNIQUE (ts);

-- Do the same for ticks_nq
DELETE FROM ticks_nq
WHERE id IN (
    SELECT id
    FROM (
        SELECT 
            id,
            ROW_NUMBER() OVER (PARTITION BY ts ORDER BY id ASC) as row_num
        FROM ticks_nq
    ) ranked
    WHERE row_num > 1
);

ALTER TABLE ticks_nq
ADD CONSTRAINT ticks_nq_ts_unique UNIQUE (ts);
```

5. Click **"Run"** to execute

6. Wait for completion (may take a few minutes for large tables)

#### **What This Does:**

- ✅ Removes all duplicate timestamps
- ✅ Keeps only the FIRST occurrence of each timestamp (smallest `id`)
- ✅ Adds a UNIQUE constraint on `ts` column
- ✅ Prevents future duplicates at the database level

#### **Expected Result:**

```
Before: 8.9M rows (with ~1M duplicates)
After:  7.9M rows (no duplicates)
```

---

### **Step 2: Use Updated Upload Script**

The upload script has been fixed to handle duplicates automatically.

#### **What Changed:**

**Before (OLD):**
```python
# Regular INSERT - allows duplicates
response = supabase.table(table_name).insert(records).execute()
```

**After (NEW):**
```python
# UPSERT with conflict handling - skips duplicates
response = supabase.table(table_name)\
    .upsert(records, on_conflict='ts', ignore_duplicates=True)\
    .execute()
```

#### **How It Works Now:**

1. **Database-level protection**: UNIQUE constraint on `ts` column
2. **Upload-level protection**: UPSERT skips rows with existing timestamps
3. **Automatic detection**: Script reports how many duplicates were skipped

#### **Example Output:**

```
Uploading data in batches of 1000...
  ✅ Batch 1: Uploaded 1000 rows (Total: 1,000/1,000,000)
  ✅ Batch 2: Uploaded 800 rows, skipped 200 duplicates (Total: 1,800/1,000,000)
  ✅ Batch 3: Uploaded 0 rows, skipped 1000 duplicates (Total: 1,800/1,000,000)
  ...

======================================================================
UPLOAD COMPLETE
======================================================================
Total rows processed: 1,000,000
Uploaded rows:        500,000
Skipped (duplicates): 500,000
Errors:               0
======================================================================
```

---

## 🧪 Testing the Fix

### **Test 1: Upload Same File Twice**

```bash
# First upload
python3 upload_tick_data.py
# File: ~/Downloads/ES_data.txt
# Result: 1,000,000 rows uploaded

# Second upload (same file)
python3 upload_tick_data.py
# File: ~/Downloads/ES_data.txt
# Result: 0 rows uploaded, 1,000,000 skipped (duplicates)
```

### **Test 2: Upload Overlapping Data**

```bash
# Upload Oct 1-5 data
python3 upload_tick_data.py
# File: ES_Oct_1-5.txt
# Result: 500,000 rows uploaded

# Upload Oct 3-7 data (overlaps Oct 3-5)
python3 upload_tick_data.py
# File: ES_Oct_3-7.txt
# Result: 300,000 rows uploaded, 200,000 skipped (Oct 3-5 duplicates)
```

---

## 📊 Verification

### **Check for Duplicates:**

```sql
-- Should return 0 rows
SELECT ts, COUNT(*) as count
FROM ticks_es
GROUP BY ts
HAVING COUNT(*) > 1;
```

### **Check Total Rows:**

```sql
SELECT COUNT(*) as total_rows FROM ticks_es;
```

### **Check Constraint Exists:**

```sql
SELECT 
    conname as constraint_name,
    contype as constraint_type
FROM pg_constraint
WHERE conrelid = 'ticks_es'::regclass
AND conname = 'ticks_es_ts_unique';
```

---

## 🎯 Summary

### **Before Fix:**
- ❌ No duplicate prevention
- ❌ Same data uploaded multiple times
- ❌ Database grows unnecessarily
- ❌ Wasted storage and upload time

### **After Fix:**
- ✅ Database-level UNIQUE constraint
- ✅ Upload script uses UPSERT
- ✅ Automatic duplicate detection
- ✅ Clear reporting of skipped rows
- ✅ Safe to upload same file multiple times

---

## 🚀 Next Steps

1. **Run the SQL script** in Supabase to clean existing duplicates
2. **Use the updated upload script** for all future uploads
3. **Verify** no duplicates exist
4. **Upload with confidence** - duplicates will be automatically skipped!

---

## 📝 Files

- `remove_duplicates.sql` - SQL script to clean duplicates
- `upload_tick_data.py` - Updated upload script (already fixed)
- `DUPLICATE_FIX_GUIDE.md` - This guide

---

**Your data is now protected from duplicates!** 🎉
