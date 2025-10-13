-- ============================================================================
-- ONE-CLICK FIX FOR DUPLICATE TICK DATA
-- ============================================================================
-- Copy this entire file and paste into Supabase SQL Editor, then click RUN
-- URL: https://supabase.com/dashboard/project/dcoukhtfcloqpfmijock
-- ============================================================================

-- ============================================================================
-- STEP 1: Remove exact duplicates from ticks_es
-- ============================================================================
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

-- ============================================================================
-- STEP 2: Add UNIQUE constraint to ticks_es
-- ============================================================================
ALTER TABLE ticks_es
ADD CONSTRAINT ticks_es_unique_tick UNIQUE (ts, bid, ask, last, vol);

-- ============================================================================
-- STEP 3: Remove exact duplicates from ticks_nq
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

-- ============================================================================
-- STEP 4: Add UNIQUE constraint to ticks_nq
-- ============================================================================
ALTER TABLE ticks_nq
ADD CONSTRAINT ticks_nq_unique_tick UNIQUE (ts, bid, ask, last, vol);

-- ============================================================================
-- DONE! Your tables are now protected from duplicates
-- ============================================================================
-- What this did:
-- ✅ Removed all exact duplicate rows (same ts, bid, ask, last, vol)
-- ✅ Kept only the first occurrence of each unique row
-- ✅ Added UNIQUE constraints to prevent future duplicates
-- ✅ Multiple ticks at same timestamp with different prices are preserved
-- ============================================================================
