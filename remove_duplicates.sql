-- ============================================================================
-- REMOVE DUPLICATE ROWS FROM ticks_es
-- ============================================================================
-- This SQL script will:
-- 1. Identify EXACT duplicate rows (same ts, bid, ask, last, vol)
-- 2. Keep only the FIRST occurrence (smallest id) of each unique row
-- 3. Delete all other duplicates
-- 4. Add a UNIQUE constraint on (ts, bid, ask, last, vol) to prevent future duplicates
--
-- NOTE: Multiple ticks can have the same timestamp but different prices!
-- We only remove rows where ALL fields are identical.
-- ============================================================================

-- Step 1: Check how many EXACT duplicates exist (OPTIONAL - for information only)
SELECT 
    'Total exact duplicate rows' as description,
    COUNT(*) as count
FROM (
    SELECT ts, bid, ask, last, vol
    FROM ticks_es
    GROUP BY ts, bid, ask, last, vol
    HAVING COUNT(*) > 1
) duplicates;

-- Step 2: Check total duplicate rows to be deleted (OPTIONAL - for information only)
SELECT 
    'Total duplicate rows to be deleted' as description,
    COUNT(*) - COUNT(DISTINCT (ts, bid, ask, last, vol)) as count
FROM ticks_es;

-- Step 3: Delete EXACT duplicates (keeps the row with smallest id for each unique combination)
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

-- Step 4: Add UNIQUE constraint on all tick fields to prevent future duplicates
ALTER TABLE ticks_es
ADD CONSTRAINT ticks_es_unique_tick UNIQUE (ts, bid, ask, last, vol);

-- Step 5: Verify no EXACT duplicates remain
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

-- Delete EXACT duplicates from ticks_nq
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

-- Add UNIQUE constraint to ticks_nq (all fields)
ALTER TABLE ticks_nq
ADD CONSTRAINT ticks_nq_unique_tick UNIQUE (ts, bid, ask, last, vol);

-- ============================================================================
-- DONE!
-- ============================================================================
-- After running this SQL:
-- - All duplicate timestamps will be removed
-- - Only the first occurrence of each timestamp will remain
-- - Future uploads will automatically reject duplicates
-- - The upload script will handle duplicates gracefully
-- ============================================================================
