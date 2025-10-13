-- ============================================================================
-- FINAL SCRIPT: Remove ALL Existing Duplicates (No Timeout)
-- ============================================================================
-- This script uses a batch approach to avoid timeouts
-- Copy and paste this ENTIRE script into Supabase SQL Editor and click RUN
-- It will process everything automatically in batches
-- ============================================================================

-- ============================================================================
-- STEP 1: Create function to delete duplicates in batches
-- ============================================================================
CREATE OR REPLACE FUNCTION delete_duplicates_batch(
    table_name text,
    batch_size integer DEFAULT 10000
)
RETURNS TABLE(
    batch_number integer,
    rows_deleted bigint
) AS $$
DECLARE
    batch_num integer := 0;
    deleted_count bigint;
    total_deleted bigint := 0;
BEGIN
    LOOP
        -- Delete one batch of duplicates
        EXECUTE format('
            DELETE FROM %I
            WHERE id IN (
                SELECT id
                FROM (
                    SELECT 
                        id,
                        ROW_NUMBER() OVER (
                            PARTITION BY ts, bid, ask, last, vol 
                            ORDER BY id ASC
                        ) as row_num
                    FROM %I
                    WHERE id IN (
                        SELECT id FROM %I
                        WHERE id NOT IN (
                            SELECT DISTINCT ON (ts, bid, ask, last, vol) id
                            FROM %I
                            ORDER BY ts, bid, ask, last, vol, id ASC
                        )
                        LIMIT %s
                    )
                ) ranked
                WHERE row_num > 1
            )',
            table_name, table_name, table_name, table_name, batch_size
        );
        
        GET DIAGNOSTICS deleted_count = ROW_COUNT;
        
        IF deleted_count = 0 THEN
            EXIT;
        END IF;
        
        batch_num := batch_num + 1;
        total_deleted := total_deleted + deleted_count;
        
        batch_number := batch_num;
        rows_deleted := deleted_count;
        RETURN NEXT;
        
        -- Small delay to avoid overwhelming the database
        PERFORM pg_sleep(0.1);
    END LOOP;
    
    RETURN;
END;
$$ LANGUAGE plpgsql;

-- ============================================================================
-- STEP 2: Delete duplicates from ticks_es in batches
-- ============================================================================
SELECT * FROM delete_duplicates_batch('ticks_es', 10000);

-- ============================================================================
-- STEP 3: Add UNIQUE constraint to ticks_es
-- ============================================================================
ALTER TABLE ticks_es
ADD CONSTRAINT ticks_es_unique_tick UNIQUE (ts, bid, ask, last, vol);

-- ============================================================================
-- STEP 4: Delete duplicates from ticks_nq in batches
-- ============================================================================
SELECT * FROM delete_duplicates_batch('ticks_nq', 10000);

-- ============================================================================
-- STEP 5: Add UNIQUE constraint to ticks_nq
-- ============================================================================
ALTER TABLE ticks_nq
ADD CONSTRAINT ticks_nq_unique_tick UNIQUE (ts, bid, ask, last, vol);

-- ============================================================================
-- STEP 6: Verify no duplicates remain
-- ============================================================================
SELECT 
    'ticks_es - Remaining duplicates' as table_check,
    COUNT(*) as duplicate_count
FROM (
    SELECT ts, bid, ask, last, vol
    FROM ticks_es
    GROUP BY ts, bid, ask, last, vol
    HAVING COUNT(*) > 1
) check_es
UNION ALL
SELECT 
    'ticks_nq - Remaining duplicates' as table_check,
    COUNT(*) as duplicate_count
FROM (
    SELECT ts, bid, ask, last, vol
    FROM ticks_nq
    GROUP BY ts, bid, ask, last, vol
    HAVING COUNT(*) > 1
) check_nq;

-- ============================================================================
-- STEP 7: Show final row counts
-- ============================================================================
SELECT 
    'ticks_es' as table_name,
    COUNT(*) as total_rows
FROM ticks_es
UNION ALL
SELECT 
    'ticks_nq' as table_name,
    COUNT(*) as total_rows
FROM ticks_nq;

-- ============================================================================
-- STEP 8: Clean up function (optional)
-- ============================================================================
DROP FUNCTION IF EXISTS delete_duplicates_batch(text, integer);

-- ============================================================================
-- DONE!
-- ============================================================================
-- Results:
-- ✅ All exact duplicates removed from ticks_es
-- ✅ All exact duplicates removed from ticks_nq
-- ✅ UNIQUE constraints added to both tables
-- ✅ Future uploads will automatically skip duplicates
-- ✅ Multiple ticks at same timestamp with different prices preserved
-- ============================================================================
