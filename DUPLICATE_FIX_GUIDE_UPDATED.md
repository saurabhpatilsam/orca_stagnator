# Duplicate Data Fix Guide (UPDATED)

## 🎯 **Important: Tick-by-Tick Data Uniqueness**

You made an excellent point! In tick-by-tick data:

### ✅ **SAME Timestamp, DIFFERENT Prices = NOT Duplicates**

```
Example: Multiple ticks at the same timestamp
┌────────────────────┬────────┬────────┬────────┬─────┐
│ Timestamp          │ Bid    │ Ask    │ Last   │ Vol │
├────────────────────┼────────┼────────┼────────┼─────┤
│ 2025-10-09 14:30:00│ 6800.00│ 6800.25│ 6800.00│  5  │ ✅ Unique
│ 2025-10-09 14:30:00│ 6800.25│ 6800.50│ 6800.25│  3  │ ✅ Unique (different prices)
│ 2025-10-09 14:30:00│ 6800.50│ 6800.75│ 6800.50│  2  │ ✅ Unique (different prices)
└────────────────────┴────────┴────────┴────────┴─────┘
```

### ❌ **SAME Timestamp, SAME Prices = Duplicate**

```
Example: Exact duplicate rows
┌────────────────────┬────────┬────────┬────────┬─────┐
│ Timestamp          │ Bid    │ Ask    │ Last   │ Vol │
├────────────────────┼────────┼────────┼────────┼─────┤
│ 2025-10-09 14:30:00│ 6800.00│ 6800.25│ 6800.00│  5  │ ✅ Keep
│ 2025-10-09 14:30:00│ 6800.00│ 6800.25│ 6800.00│  5  │ ❌ Duplicate (exact match)
└────────────────────┴────────┴────────┴────────┴─────┘
```

---

## ✅ **Updated Solution**

### **Uniqueness Definition:**

A row is unique if **ANY** of these fields differ:
- `ts` (timestamp)
- `bid` (bid price)
- `ask` (ask price)
- `last` (last price)
- `vol` (volume)

Only rows where **ALL 5 fields are identical** are considered duplicates.

---

## 🔧 **Step 1: Clean Existing Duplicates**

### **Updated SQL Script:**

```sql
-- ============================================================================
-- REMOVE EXACT DUPLICATE ROWS FROM ticks_es
-- ============================================================================
-- Only removes rows where ALL fields are identical: ts, bid, ask, last, vol
-- Multiple ticks with same timestamp but different prices are KEPT!
-- ============================================================================

-- Step 1: Check how many EXACT duplicates exist
SELECT 
    'Total exact duplicate rows' as description,
    COUNT(*) as count
FROM (
    SELECT ts, bid, ask, last, vol
    FROM ticks_es
    GROUP BY ts, bid, ask, last, vol
    HAVING COUNT(*) > 1
) duplicates;

-- Step 2: Delete EXACT duplicates (keeps first occurrence)
DELETE FROM ticks_es
WHERE id IN (
    SELECT id
    FROM (
        SELECT 
            id,
            ROW_NUMBER() OVER (
                PARTITION BY ts, bid, ask, last, vol 
                ORDER BY id ASC
            ) as row_num
        FROM ticks_es
    ) ranked
    WHERE row_num > 1
);

-- Step 3: Add UNIQUE constraint on ALL tick fields
ALTER TABLE ticks_es
ADD CONSTRAINT ticks_es_unique_tick UNIQUE (ts, bid, ask, last, vol);

-- Step 4: Verify no exact duplicates remain
SELECT 
    'Remaining exact duplicates (should be 0)' as description,
    COUNT(*) as count
FROM (
    SELECT ts, bid, ask, last, vol
    FROM ticks_es
    GROUP BY ts, bid, ask, last, vol
    HAVING COUNT(*) > 1
) check_duplicates;

-- ============================================================================
-- REPEAT FOR ticks_nq TABLE
-- ============================================================================

DELETE FROM ticks_nq
WHERE id IN (
    SELECT id
    FROM (
        SELECT 
            id,
            ROW_NUMBER() OVER (
                PARTITION BY ts, bid, ask, last, vol 
                ORDER BY id ASC
            ) as row_num
        FROM ticks_nq
    ) ranked
    WHERE row_num > 1
);

ALTER TABLE ticks_nq
ADD CONSTRAINT ticks_nq_unique_tick UNIQUE (ts, bid, ask, last, vol);
```

### **How to Run:**

1. Go to: https://supabase.com/dashboard/project/dcoukhtfcloqpfmijock
2. Click **"SQL Editor"** → **"New Query"**
3. Copy and paste the SQL above
4. Click **"Run"**

---

## 🔧 **Step 2: Updated Upload Script**

The upload script now checks for **exact row matches**, not just timestamps.

### **What Changed:**

**Before (WRONG):**
```python
# Only checked timestamp - WRONG for tick data!
.upsert(records, on_conflict='ts', ignore_duplicates=True)
```

**After (CORRECT):**
```python
# Checks ALL fields - CORRECT for tick data!
.upsert(records, on_conflict='ts,bid,ask,last,vol', ignore_duplicates=True)
```

### **Duplicate Detection Logic:**

```python
# Creates a hash of the complete row
row_hash = f"{ts}|{bid}|{ask}|{last}|{vol}"

# Only marks as duplicate if EXACT match
if row_hash in existing_rows:
    # This is an exact duplicate - skip it
else:
    # This is unique - upload it
```

---

## 📊 **Examples**

### **Example 1: Same Timestamp, Different Prices**

**Upload File:**
```csv
ts,bid,ask,last,vol
2025-10-09 14:30:00,6800.00,6800.25,6800.00,5
2025-10-09 14:30:00,6800.25,6800.50,6800.25,3
2025-10-09 14:30:00,6800.50,6800.75,6800.50,2
```

**Result:**
```
✅ All 3 rows uploaded
✅ 0 duplicates (different prices)
```

### **Example 2: Exact Duplicate Rows**

**Upload File:**
```csv
ts,bid,ask,last,vol
2025-10-09 14:30:00,6800.00,6800.25,6800.00,5
2025-10-09 14:30:00,6800.00,6800.25,6800.00,5  ← Exact duplicate
2025-10-09 14:30:00,6800.25,6800.50,6800.25,3
```

**Result:**
```
✅ 2 rows uploaded
❌ 1 duplicate skipped (exact match of row 1)
```

### **Example 3: Re-uploading Same File**

**First Upload:**
```
File: ES_Oct_9.csv (1M rows)
Result: 1,000,000 rows uploaded
```

**Second Upload (same file):**
```
File: ES_Oct_9.csv (1M rows)
Result: 0 rows uploaded, 1,000,000 duplicates skipped ✅
```

---

## 🧪 **Testing**

### **Test 1: Multiple Ticks at Same Timestamp**

```bash
# Create test file with same timestamp, different prices
cat > test_same_timestamp.csv << EOF
ts,bid,ask,last,vol
2025-10-09 14:30:00,6800.00,6800.25,6800.00,5
2025-10-09 14:30:00,6800.25,6800.50,6800.25,3
2025-10-09 14:30:00,6800.50,6800.75,6800.50,2
EOF

# Upload
python3 upload_tick_data.py
# File: test_same_timestamp.csv
# Result: All 3 rows uploaded ✅
```

### **Test 2: Exact Duplicates**

```bash
# Create test file with exact duplicates
cat > test_duplicates.csv << EOF
ts,bid,ask,last,vol
2025-10-09 14:30:00,6800.00,6800.25,6800.00,5
2025-10-09 14:30:00,6800.00,6800.25,6800.00,5
2025-10-09 14:30:00,6800.00,6800.25,6800.00,5
EOF

# Upload
python3 upload_tick_data.py
# File: test_duplicates.csv
# Result: 1 row uploaded, 2 duplicates skipped ✅
```

---

## 📝 **Summary**

### **Uniqueness Check:**

| Field | Must Match for Duplicate? |
|-------|---------------------------|
| `ts` (timestamp) | ✅ Yes |
| `bid` (bid price) | ✅ Yes |
| `ask` (ask price) | ✅ Yes |
| `last` (last price) | ✅ Yes |
| `vol` (volume) | ✅ Yes |

**All 5 fields must be identical for a row to be considered a duplicate.**

### **What's Protected:**

✅ Multiple ticks at same timestamp with different prices → **ALLOWED**  
✅ Same timestamp, different bid/ask spread → **ALLOWED**  
✅ Same timestamp, different volume → **ALLOWED**  
❌ Exact same row uploaded twice → **BLOCKED**  

---

## 🎯 **Action Items**

1. ✅ **Run the updated SQL script** to clean existing duplicates and add composite UNIQUE constraint
2. ✅ **Use the updated upload script** (already fixed in `upload_tick_data.py`)
3. ✅ **Test with your data** to verify correct behavior
4. ✅ **Upload with confidence** - exact duplicates will be automatically skipped!

---

**Your tick-by-tick data integrity is now properly protected!** 🎉
