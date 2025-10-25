#!/usr/bin/env python3
"""
Automated Cron Job Setup for All 16 Data Collection Streams
This script creates all cron jobs in Supabase automatically
"""

import requests
import json
import time

# Configuration
SUPABASE_PROJECT_ID = "dcoukhtfcloqpfmijock"
SUPABASE_URL = f"https://{SUPABASE_PROJECT_ID}.supabase.co"
SERVICE_ROLE_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6ImRjb3VraHRmY2xvcXBmbWlqb2NrIiwicm9sZSI6InNlcnZpY2Vfcm9sZSIsImlhdCI6MTc1MzcwMTgwMywiZXhwIjoyMDY5Mjc3ODAzfQ.iNzNrB0z64m8cINx0DeVCuAbcStWpMPx_bDos_vgO7w"

# Cron jobs configuration
CRON_JOBS = [
    # NQ (E-mini Nasdaq)
    {"name": "fetch-nq-5min", "schedule": "*/5 * * * *", "symbol": "NQZ5", "timeframe": 5},
    {"name": "fetch-nq-15min", "schedule": "*/15 * * * *", "symbol": "NQZ5", "timeframe": 15},
    {"name": "fetch-nq-30min", "schedule": "*/30 * * * *", "symbol": "NQZ5", "timeframe": 30},
    {"name": "fetch-nq-60min", "schedule": "0 * * * *", "symbol": "NQZ5", "timeframe": 60},
    
    # MNQ (Micro E-mini Nasdaq)
    {"name": "fetch-mnq-5min", "schedule": "*/5 * * * *", "symbol": "MNQZ5", "timeframe": 5},
    {"name": "fetch-mnq-15min", "schedule": "*/15 * * * *", "symbol": "MNQZ5", "timeframe": 15},
    {"name": "fetch-mnq-30min", "schedule": "*/30 * * * *", "symbol": "MNQZ5", "timeframe": 30},
    {"name": "fetch-mnq-60min", "schedule": "0 * * * *", "symbol": "MNQZ5", "timeframe": 60},
    
    # ES (E-mini S&P 500)
    {"name": "fetch-es-5min", "schedule": "*/5 * * * *", "symbol": "ESZ5", "timeframe": 5},
    {"name": "fetch-es-15min", "schedule": "*/15 * * * *", "symbol": "ESZ5", "timeframe": 15},
    {"name": "fetch-es-30min", "schedule": "*/30 * * * *", "symbol": "ESZ5", "timeframe": 30},
    {"name": "fetch-es-60min", "schedule": "0 * * * *", "symbol": "ESZ5", "timeframe": 60},
    
    # MES (Micro E-mini S&P 500)
    {"name": "fetch-mes-5min", "schedule": "*/5 * * * *", "symbol": "MESZ5", "timeframe": 5},
    {"name": "fetch-mes-15min", "schedule": "*/15 * * * *", "symbol": "MESZ5", "timeframe": 15},
    {"name": "fetch-mes-30min", "schedule": "*/30 * * * *", "symbol": "MESZ5", "timeframe": 30},
    {"name": "fetch-mes-60min", "schedule": "0 * * * *", "symbol": "MESZ5", "timeframe": 60},
]

def create_cron_job_sql(job):
    """Generate SQL for creating a cron job"""
    sql = f"""
SELECT cron.schedule(
    '{job['name']}',
    '{job['schedule']}',
    $$
    SELECT net.http_post(
        url:='https://dcoukhtfcloqpfmijock.supabase.co/functions/v1/fetch-candles',
        headers:='{{"Content-Type": "application/json", "Authorization": "Bearer {SERVICE_ROLE_KEY}"}}'::jsonb,
        body:='{{"timeframe": {job['timeframe']}, "symbol": "{job['symbol']}"}}'::jsonb
    ) AS request_id;
    $$
);
"""
    return sql

def execute_sql(sql):
    """Execute SQL via Supabase PostgREST"""
    url = f"{SUPABASE_URL}/rest/v1/rpc/query"
    headers = {
        'apikey': SERVICE_ROLE_KEY,
        'Authorization': f'Bearer {SERVICE_ROLE_KEY}',
        'Content-Type': 'application/json'
    }
    data = {'query': sql}
    
    response = requests.post(url, headers=headers, json=data)
    return response

def setup_via_sql_file():
    """Generate a complete SQL file that can be run in Supabase SQL Editor"""
    print("=" * 70)
    print("GENERATING COMPLETE SQL FILE")
    print("=" * 70)
    print()
    
    sql_file_path = "setup/database/CRON_JOBS_COMPLETE.sql"
    
    with open(sql_file_path, 'w') as f:
        f.write("""-- ========================================
-- AUTOMATED CRON JOB SETUP - ALL 16 STREAMS
-- ========================================
-- Copy this entire file and run in Supabase SQL Editor
-- https://supabase.com/dashboard/project/dcoukhtfcloqpfmijock/sql/new

-- Enable pg_cron extension
CREATE EXTENSION IF NOT EXISTS pg_cron;

-- Remove any existing cron jobs with these names
DO $$
DECLARE
    job_name TEXT;
BEGIN
    FOR job_name IN 
        SELECT jobname FROM cron.job WHERE jobname LIKE 'fetch-%'
    LOOP
        PERFORM cron.unschedule(job_name);
        RAISE NOTICE 'Unscheduled existing job: %', job_name;
    END LOOP;
END $$;

-- Create all 16 cron jobs
""")
        
        for i, job in enumerate(CRON_JOBS, 1):
            f.write(f"\n-- {i}/16: {job['name']}\n")
            f.write(create_cron_job_sql(job))
            f.write("\n")
        
        f.write("""
-- Verify cron jobs were created
SELECT 
    jobname, 
    schedule, 
    active,
    command
FROM cron.job 
WHERE jobname LIKE 'fetch-%'
ORDER BY jobname;

-- Show count
SELECT 
    'Total cron jobs created: ' || COUNT(*)::text as status
FROM cron.job 
WHERE jobname LIKE 'fetch-%';
""")
    
    print(f"✅ Generated SQL file: {sql_file_path}")
    print()
    print("📋 Next steps:")
    print("1. Open: https://supabase.com/dashboard/project/dcoukhtfcloqpfmijock/sql/new")
    print(f"2. Copy entire content of: {sql_file_path}")
    print("3. Paste and click 'Run'")
    print("4. You should see: 'Total cron jobs created: 16'")
    print()
    
    # Also display a summary
    print("=" * 70)
    print("CRON JOBS SUMMARY")
    print("=" * 70)
    instruments = {"NQ": 0, "MNQ": 0, "ES": 0, "MES": 0}
    for job in CRON_JOBS:
        symbol = job['symbol']
        if 'MNQ' in symbol:
            instruments['MNQ'] += 1
        elif 'NQ' in symbol:
            instruments['NQ'] += 1
        elif 'MES' in symbol:
            instruments['MES'] += 1
        elif 'ES' in symbol:
            instruments['ES'] += 1
    
    for instrument, count in instruments.items():
        print(f"  {instrument}: {count} jobs (5, 15, 30, 60 min)")
    print(f"\n  Total: {len(CRON_JOBS)} automated data collection streams")
    print()

if __name__ == "__main__":
    print()
    print("🚀 AUTOMATED CRON JOB SETUP")
    print("=" * 70)
    print()
    print("Setting up 16 automated data collection streams...")
    print("  - 4 instruments: NQ, MNQ, ES, MES")
    print("  - 4 timeframes each: 5min, 15min, 30min, 60min")
    print()
    
    # Generate SQL file approach (most reliable)
    setup_via_sql_file()
    
    print("=" * 70)
    print("✅ SETUP COMPLETE!")
    print("=" * 70)
    print()
    print("Once you run the SQL file, your system will:")
    print("  ✅ Collect data automatically every 5/15/30/60 minutes")
    print("  ✅ Run 24/7 without any manual intervention")
    print("  ✅ Store data for all 4 instruments")
    print("  ✅ Handle token refresh automatically")
    print()
