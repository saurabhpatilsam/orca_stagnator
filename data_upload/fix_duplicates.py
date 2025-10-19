"""
Fix Duplicate Tick Data
========================
This script:
1. Identifies duplicate timestamps in ticks_es table
2. Removes duplicates (keeps only the first occurrence)
3. Adds a UNIQUE constraint to prevent future duplicates

Author: Automated Trading System
Date: 2025-10-12
"""

import os
from supabase import create_client
from dotenv import load_dotenv
from loguru import logger

load_dotenv()

# Initialize Supabase
supabase = create_client(
    os.getenv("SUPABASE_URL"),
    os.getenv("SUPABASE_KEY")
)

def count_total_rows(table_name: str) -> int:
    """Count total rows in table"""
    logger.info(f"Counting total rows in {table_name}...")
    
    # Use a simple count query
    response = supabase.table(table_name).select('id', count='exact').limit(1).execute()
    total = response.count if hasattr(response, 'count') else 0
    
    logger.info(f"Total rows: {total:,}")
    return total

def remove_duplicates_sql(table_name: str):
    """
    Generate SQL to remove duplicates.
    This keeps the row with the smallest ID for each timestamp.
    """
    
    sql = f"""
-- Step 1: Find duplicate timestamps
WITH duplicates AS (
    SELECT ts, COUNT(*) as count
    FROM {table_name}
    GROUP BY ts
    HAVING COUNT(*) > 1
),

-- Step 2: For each duplicate timestamp, keep only the first row (smallest id)
rows_to_keep AS (
    SELECT DISTINCT ON (ts) id, ts
    FROM {table_name}
    WHERE ts IN (SELECT ts FROM duplicates)
    ORDER BY ts, id ASC
),

-- Step 3: Get IDs of rows to delete
rows_to_delete AS (
    SELECT t.id
    FROM {table_name} t
    WHERE t.ts IN (SELECT ts FROM duplicates)
    AND t.id NOT IN (SELECT id FROM rows_to_keep)
)

-- Step 4: Delete duplicate rows
DELETE FROM {table_name}
WHERE id IN (SELECT id FROM rows_to_delete);

-- Step 5: Add unique constraint to prevent future duplicates
ALTER TABLE {table_name}
ADD CONSTRAINT {table_name}_ts_unique UNIQUE (ts);
"""
    
    return sql

def main():
    """Main execution"""
    
    print("\n" + "=" * 70)
    print("DUPLICATE DETECTION AND REMOVAL")
    print("=" * 70)
    print("This will remove duplicate timestamps from ticks_es table")
    print("=" * 70 + "\n")
    
    table_name = 'ticks_es'
    
    # Count current rows
    total_before = count_total_rows(table_name)
    
    # Generate SQL
    logger.info("\n" + "=" * 70)
    logger.info("SQL TO EXECUTE IN SUPABASE")
    logger.info("=" * 70)
    
    sql = remove_duplicates_sql(table_name)
    print(sql)
    
    logger.info("\n" + "=" * 70)
    logger.warning("⚠️  MANUAL ACTION REQUIRED")
    logger.info("=" * 70)
    logger.info("Please execute the above SQL in Supabase SQL Editor:")
    logger.info("1. Go to: https://supabase.com/dashboard/project/dcoukhtfcloqpfmijock")
    logger.info("2. Click 'SQL Editor' in the left sidebar")
    logger.info("3. Click 'New Query'")
    logger.info("4. Copy and paste the SQL above")
    logger.info("5. Click 'Run' to execute")
    logger.info("\nThis will:")
    logger.info("  - Remove all duplicate timestamps")
    logger.info("  - Keep only the first occurrence of each timestamp")
    logger.info("  - Add a UNIQUE constraint to prevent future duplicates")
    logger.info("=" * 70)

if __name__ == "__main__":
    main()
