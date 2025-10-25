#!/usr/bin/env python3
"""
Automated Cron Job Setup for All Instruments
Creates 16 cron jobs (4 instruments × 4 timeframes) in Supabase
"""

import subprocess
import sys
import time

# Colors
RED = '\033[0;31m'
GREEN = '\033[0;32m'
YELLOW = '\033[1;33m'
BLUE = '\033[0;34m'
MAGENTA = '\033[0;35m'
CYAN = '\033[0;36m'
NC = '\033[0m'

# Supabase connection details
PROJECT_REF = "dcoukhtfcloqpfmijock"
SERVICE_ROLE_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6ImRjb3VraHRmY2xvcXBmbWlqb2NrIiwicm9sZSI6InNlcnZpY2Vfcm9sZSIsImlhdCI6MTc1MzcwMTgwMywiZXhwIjoyMDY5Mjc3ODAzfQ.iNzNrB0z64m8cINx0DeVCuAbcStWpMPx_bDos_vgO7w"
SUPABASE_URL = f"https://{PROJECT_REF}.supabase.co"

# Instruments configuration
INSTRUMENTS = {
    'NQ': 'NQZ5',
    'MNQ': 'MNQZ5',
    'ES': 'ESZ5',
    'MES': 'MESZ5'
}

# Timeframes configuration
TIMEFRAMES = {
    5: '*/5 * * * *',    # Every 5 minutes
    15: '*/15 * * * *',  # Every 15 minutes
    30: '*/30 * * * *',  # Every 30 minutes
    60: '0 * * * *'      # Every hour
}

def create_cron_job_sql(instrument_name, symbol, timeframe_min, schedule):
    """Generate SQL for a single cron job"""
    job_name = f"fetch-{instrument_name.lower()}-{timeframe_min}min"
    
    sql = f"""
-- {instrument_name} {timeframe_min}-minute candles
SELECT cron.schedule(
    '{job_name}',
    '{schedule}',
    $$
    SELECT status, content::json->>'success' as success
    FROM http((
        'POST',
        '{SUPABASE_URL}/functions/v1/fetch-candles',
        ARRAY[http_header('Content-Type', 'application/json'), http_header('Authorization', 'Bearer {SERVICE_ROLE_KEY}')],
        'application/json',
        '{{"timeframe": {timeframe_min}, "symbol": "{symbol}"}}'
    )::http_request);
    $$
);
"""
    return sql

def generate_full_sql():
    """Generate complete SQL for all cron jobs"""
    
    sql_parts = []
    
    # Header
    sql_parts.append("""
-- ============================================
-- Automated Cron Job Setup for All Instruments
-- Total: 16 cron jobs (4 instruments × 4 timeframes)
-- ============================================

-- Enable required extensions
CREATE EXTENSION IF NOT EXISTS pg_cron;
CREATE EXTENSION IF NOT EXISTS http;

-- Remove existing jobs to avoid duplicates
DO $$ 
DECLARE
    job_record RECORD;
BEGIN
    FOR job_record IN 
        SELECT jobid FROM cron.job 
        WHERE jobname LIKE 'fetch-nq-%'
           OR jobname LIKE 'fetch-mnq-%'
           OR jobname LIKE 'fetch-es-%'
           OR jobname LIKE 'fetch-mes-%'
    LOOP
        PERFORM cron.unschedule(job_record.jobid);
    END LOOP;
END $$;

""")
    
    # Generate cron job for each instrument and timeframe
    for instrument_name, symbol in INSTRUMENTS.items():
        sql_parts.append(f"\n-- ============================================")
        sql_parts.append(f"-- {instrument_name} ({symbol})")
        sql_parts.append(f"-- ============================================\n")
        
        for timeframe_min, schedule in TIMEFRAMES.items():
            sql_parts.append(create_cron_job_sql(instrument_name, symbol, timeframe_min, schedule))
    
    # Verification query
    sql_parts.append("""
-- ============================================
-- Verification - List All Cron Jobs
-- ============================================
SELECT 
    jobid,
    jobname,
    schedule,
    active,
    CASE 
        WHEN schedule = '*/5 * * * *' THEN 'Every 5 minutes'
        WHEN schedule = '*/15 * * * *' THEN 'Every 15 minutes'
        WHEN schedule = '*/30 * * * *' THEN 'Every 30 minutes'
        WHEN schedule = '0 * * * *' THEN 'Every hour'
    END as frequency
FROM cron.job 
WHERE jobname LIKE 'fetch-%'
ORDER BY 
    CASE 
        WHEN jobname LIKE 'fetch-nq-%' THEN 1
        WHEN jobname LIKE 'fetch-mnq-%' THEN 2
        WHEN jobname LIKE 'fetch-es-%' THEN 3
        WHEN jobname LIKE 'fetch-mes-%' THEN 4
    END,
    jobname;

-- Summary by instrument
SELECT 
    CASE 
        WHEN jobname LIKE 'fetch-nq-%' THEN 'NQ (E-mini Nasdaq)'
        WHEN jobname LIKE 'fetch-mnq-%' THEN 'MNQ (Micro E-mini Nasdaq)'
        WHEN jobname LIKE 'fetch-es-%' THEN 'ES (E-mini S&P 500)'
        WHEN jobname LIKE 'fetch-mes-%' THEN 'MES (Micro E-mini S&P 500)'
    END as instrument,
    COUNT(*) as cron_jobs_count
FROM cron.job 
WHERE jobname LIKE 'fetch-%'
GROUP BY 
    CASE 
        WHEN jobname LIKE 'fetch-nq-%' THEN 'NQ (E-mini Nasdaq)'
        WHEN jobname LIKE 'fetch-mnq-%' THEN 'MNQ (Micro E-mini Nasdaq)'
        WHEN jobname LIKE 'fetch-es-%' THEN 'ES (E-mini S&P 500)'
        WHEN jobname LIKE 'fetch-mes-%' THEN 'MES (Micro E-mini S&P 500)'
    END
ORDER BY instrument;
""")
    
    return '\n'.join(sql_parts)

def main():
    print(f"{BLUE}╔════════════════════════════════════════════════════════╗")
    print(f"║  🚀 Automated Cron Job Setup                          ║")
    print(f"║  Creating 16 cron jobs for all instruments           ║")
    print(f"╚════════════════════════════════════════════════════════╝{NC}\n")
    
    print(f"{CYAN}📋 Configuration:{NC}")
    print(f"  Instruments: {', '.join(INSTRUMENTS.keys())}")
    print(f"  Timeframes: {', '.join([f'{t}min' for t in TIMEFRAMES.keys()])}")
    print(f"  Total cron jobs: 16\n")
    
    # Generate SQL
    print(f"{YELLOW}📝 Generating SQL...{NC}")
    sql_content = generate_full_sql()
    
    # Save to file
    output_file = 'scripts/generated_cron_jobs.sql'
    with open(output_file, 'w') as f:
        f.write(sql_content)
    
    print(f"{GREEN}✅ SQL file generated: {output_file}{NC}\n")
    
    # Show summary
    print(f"{MAGENTA}{'━' * 56}{NC}")
    print(f"{CYAN}📊 Cron Jobs to be Created:{NC}")
    print(f"{MAGENTA}{'━' * 56}{NC}\n")
    
    for instrument_name in INSTRUMENTS.keys():
        print(f"{BLUE}{instrument_name}:{NC}")
        for timeframe_min in TIMEFRAMES.keys():
            schedule_desc = TIMEFRAMES[timeframe_min]
            if timeframe_min == 60:
                freq = "Every hour"
            else:
                freq = f"Every {timeframe_min} minutes"
            print(f"  • {timeframe_min}min - {freq}")
        print()
    
    # Instructions
    print(f"{MAGENTA}{'━' * 56}{NC}")
    print(f"{CYAN}📝 Next Steps:{NC}")
    print(f"{MAGENTA}{'━' * 56}{NC}\n")
    
    print(f"1. Open Supabase SQL Editor:")
    print(f"   {BLUE}https://supabase.com/dashboard/project/{PROJECT_REF}/sql/new{NC}\n")
    
    print(f"2. Copy the generated SQL file:")
    print(f"   {GREEN}open {output_file}{NC}")
    print(f"   Or run: {GREEN}cat {output_file} | pbcopy{NC}\n")
    
    print(f"3. Paste in Supabase SQL Editor and click 'Run'\n")
    
    print(f"4. Verify cron jobs are created:")
    print(f"   SELECT jobname FROM cron.job WHERE jobname LIKE 'fetch-%';\n")
    
    # Offer to open files
    response = input(f"{YELLOW}Open the SQL file now? (y/n): {NC}")
    if response.lower() == 'y':
        subprocess.run(['open', output_file])
        time.sleep(1)
        subprocess.run(['open', f'https://supabase.com/dashboard/project/{PROJECT_REF}/sql/new'])
        print(f"\n{GREEN}✅ Files opened! Copy the SQL and run it in Supabase.{NC}\n")
    
    print(f"{GREEN}╔════════════════════════════════════════════════════════╗")
    print(f"║  ✅ Setup Ready!                                       ║")
    print(f"╚════════════════════════════════════════════════════════╝{NC}\n")
    
    return 0

if __name__ == "__main__":
    try:
        sys.exit(main())
    except KeyboardInterrupt:
        print(f"\n{YELLOW}Setup cancelled{NC}")
        sys.exit(1)
    except Exception as e:
        print(f"\n{RED}❌ Error: {e}{NC}")
        sys.exit(1)
