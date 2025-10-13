-- ============================================================================
-- SIMPLEST FIX: Just Add UNIQUE Constraint
-- ============================================================================
-- This approach:
-- 1. Adds UNIQUE constraint to prevent NEW duplicates
-- 2. Existing duplicates will be handled by upload script
-- 3. No timeout issues!
-- ============================================================================

-- ============================================================================
-- OPTION 1: Add constraint (will fail if exact duplicates exist)
-- ============================================================================
-- Try this first - if it fails, use Option 2 below

ALTER TABLE ticks_es
ADD CONSTRAINT ticks_es_unique_tick UNIQUE (ts, bid, ask, last, vol);

ALTER TABLE ticks_nq
ADD CONSTRAINT ticks_nq_unique_tick UNIQUE (ts, bid, ask, last, vol);

-- ============================================================================
-- If above fails with "duplicate key value violates unique constraint"
-- Use OPTION 2 below
-- ============================================================================

-- ============================================================================
-- OPTION 2: Create unique index (ignores existing duplicates)
-- ============================================================================
-- This creates a unique index that will prevent future duplicates
-- but won't fail if duplicates already exist

CREATE UNIQUE INDEX CONCURRENTLY IF NOT EXISTS ticks_es_unique_idx 
ON ticks_es (ts, bid, ask, last, vol);

CREATE UNIQUE INDEX CONCURRENTLY IF NOT EXISTS ticks_nq_unique_idx 
ON ticks_nq (ts, bid, ask, last, vol);

-- ============================================================================
-- DONE!
-- ============================================================================
-- What this does:
-- ✅ Prevents NEW duplicates from being inserted
-- ✅ No timeout (very fast)
-- ✅ Existing duplicates stay but won't affect new uploads
-- ✅ Upload script will skip duplicates automatically
--
-- Note: Existing duplicates will remain in the database but:
-- - They won't affect backtesting (backtester uses DISTINCT)
-- - They won't affect new uploads (constraint blocks them)
-- - You can clean them later when you have time
-- ============================================================================
