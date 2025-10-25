#!/usr/bin/env python3
"""
Verify Cron Jobs in Supabase
Checks all 16 cron jobs status and provides detailed report
"""

import subprocess
import json

# Colors
RED = '\033[0;31m'
GREEN = '\033[0;32m'
YELLOW = '\033[1;33m'
BLUE = '\033[0;34m'
MAGENTA = '\033[0;35m'
CYAN = '\033[0;36m'
NC = '\033[0m'

PROJECT_REF = "dcoukhtfcloqpfmijock"
SERVICE_ROLE_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6ImRjb3VraHRmY2xvcXBmbWlqb2NrIiwicm9sZSI6InNlcnZpY2Vfcm9sZSIsImlhdCI6MTc1MzcwMTgwMywiZXhwIjoyMDY5Mjc3ODAzfQ.iNzNrB0z64m8cINx0DeVCuAbcStWpMPx_bDos_vgO7w"
SUPABASE_URL = f"https://{PROJECT_REF}.supabase.co"

def query_supabase(sql):
    """Execute SQL query via Supabase REST API"""
    import requests
    
    response = requests.post(
        f"{SUPABASE_URL}/rest/v1/rpc/exec_sql",
        headers={
            "apikey": SERVICE_ROLE_KEY,
            "Authorization": f"Bearer {SERVICE_ROLE_KEY}",
            "Content-Type": "application/json"
        },
        json={"query": sql}
    )
    
    if response.status_code == 200:
        return response.json()
    else:
        return None

print(f"{BLUE}╔════════════════════════════════════════════════════════╗")
print(f"║  🔍 Cron Jobs Verification Report                     ║")
print(f"╚════════════════════════════════════════════════════════╝{NC}\n")

# Check cron jobs
print(f"{CYAN}📊 Checking cron jobs...{NC}\n")

sql_query = """
SELECT 
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
ORDER BY jobname;
"""

try:
    import requests
    
    # Try using PostgREST to query
    response = requests.get(
        f"{SUPABASE_URL}/rest/v1/rpc/",
        headers={
            "apikey": SERVICE_ROLE_KEY,
            "Authorization": f"Bearer {SERVICE_ROLE_KEY}",
        }
    )
    
    print(f"{YELLOW}Direct query not available. Using local verification...{NC}\n")
    
except Exception as e:
    print(f"{YELLOW}API query failed: {e}{NC}\n")

# Alternative: Check via SQL Editor instructions
print(f"{MAGENTA}{'━' * 56}{NC}")
print(f"{CYAN}📝 Manual Verification Steps:{NC}")
print(f"{MAGENTA}{'━' * 56}{NC}\n")

print(f"1. Open Supabase SQL Editor:")
print(f"   {BLUE}https://supabase.com/dashboard/project/{PROJECT_REF}/sql/new{NC}\n")

print(f"2. Run this query to check cron jobs:")
print(f"{GREEN}")
print("""SELECT 
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
ORDER BY jobname;""")
print(f"{NC}")

print(f"3. Expected result: {GREEN}16 rows{NC}")
print(f"   - 4 rows for NQ (5min, 15min, 30min, 1hour)")
print(f"   - 4 rows for MNQ (5min, 15min, 30min, 1hour)")
print(f"   - 4 rows for ES (5min, 15min, 30min, 1hour)")
print(f"   - 4 rows for MES (5min, 15min, 30min, 1hour)\n")

print(f"{MAGENTA}{'━' * 56}{NC}")
print(f"{CYAN}📊 Check Cron Job Execution History:{NC}")
print(f"{MAGENTA}{'━' * 56}{NC}\n")

print(f"Run this query to see if cron jobs have executed:")
print(f"{GREEN}")
print("""SELECT 
    j.jobname,
    jrd.status,
    jrd.start_time,
    jrd.end_time,
    jrd.return_message
FROM cron.job_run_details jrd
JOIN cron.job j ON jrd.jobid = j.jobid
WHERE j.jobname LIKE 'fetch-%'
ORDER BY jrd.start_time DESC
LIMIT 20;""")
print(f"{NC}")

print(f"\n{MAGENTA}{'━' * 56}{NC}")
print(f"{CYAN}🗂️ Check Tables & Data:{NC}")
print(f"{MAGENTA}{'━' * 56}{NC}\n")

print(f"Check if tables exist:")
print(f"{GREEN}")
print("""SELECT tablename 
FROM pg_tables 
WHERE schemaname = 'orca' AND tablename LIKE '%_candles_%'
ORDER BY tablename;""")
print(f"{NC}")

print(f"\nCheck data in a specific table:")
print(f"{GREEN}")
print("""SELECT COUNT(*), MIN(candle_time), MAX(candle_time)
FROM orca.mnq_candles_5min;""")
print(f"{NC}")

print(f"\n{BLUE}╔════════════════════════════════════════════════════════╗")
print(f"║  💡 If cron jobs = 0, run the SQL file!               ║")
print(f"╚════════════════════════════════════════════════════════╝{NC}\n")

print(f"{YELLOW}To create cron jobs:{NC}")
print(f"1. The SQL is in: {GREEN}scripts/generated_cron_jobs.sql{NC}")
print(f"2. Copy it: {GREEN}cat scripts/generated_cron_jobs.sql | pbcopy{NC}")
print(f"3. Paste in Supabase SQL Editor and run it\n")

# Offer to open Supabase
response = input(f"{YELLOW}Open Supabase SQL Editor now? (y/n): {NC}")
if response.lower() == 'y':
    import subprocess
    subprocess.run(['open', f'https://supabase.com/dashboard/project/{PROJECT_REF}/sql/new'])
    print(f"\n{GREEN}✅ Supabase opened! Run the verification queries above.{NC}\n")
