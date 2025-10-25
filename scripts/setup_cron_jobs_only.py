#!/usr/bin/env python3
"""
Setup Cron Jobs Only - Simple & Fast
Just creates the 16 cron jobs, no backfilling
"""

import subprocess
import sys

# Colors
GREEN = '\033[0;32m'
YELLOW = '\033[1;33m'
BLUE = '\033[0;34m'
CYAN = '\033[0;36m'
NC = '\033[0m'

PROJECT_REF = "dcoukhtfcloqpfmijock"
SERVICE_ROLE_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6ImRjb3VraHRmY2xvcXBmbWlqb2NrIiwicm9sZSI6InNlcnZpY2Vfcm9sZSIsImlhdCI6MTc1MzcwMTgwMywiZXhwIjoyMDY5Mjc3ODAzfQ.iNzNrB0z64m8cINx0DeVCuAbcStWpMPx_bDos_vgO7w"
SUPABASE_URL = f"https://{PROJECT_REF}.supabase.co"

INSTRUMENTS = {
    'NQ': 'NQZ5',
    'MNQ': 'MNQZ5',
    'ES': 'ESZ5',
    'MES': 'MESZ5'
}

SCHEDULES = {
    5: "*/5 * * * *",
    15: "*/15 * * * *",
    30: "*/30 * * * *",
    60: "0 * * * *"
}

print(f"{BLUE}╔════════════════════════════════════════════════════════╗")
print(f"║  ⏰ Cron Jobs Setup (16 jobs)                         ║")
print(f"╚════════════════════════════════════════════════════════╝{NC}\n")

# Generate SQL
sql_parts = [
    "-- 16 Cron Jobs for All Instruments",
    "CREATE EXTENSION IF NOT EXISTS pg_cron;",
    "CREATE EXTENSION IF NOT EXISTS http;",
    "",
    "-- Remove old jobs",
    "DO $$ DECLARE r RECORD; BEGIN",
    "  FOR r IN SELECT jobid FROM cron.job WHERE jobname LIKE 'fetch-%' LOOP",
    "    PERFORM cron.unschedule(r.jobid);",
    "  END LOOP;",
    "END $$;",
    ""
]

for inst_code, symbol in INSTRUMENTS.items():
    sql_parts.append(f"\n-- {inst_code} ({symbol})")
    
    for tf in [5, 15, 30, 60]:
        job_name = f"fetch-{inst_code.lower()}-{tf}min"
        schedule = SCHEDULES[tf]
        
        sql_parts.append(f"""SELECT cron.schedule('{job_name}', '{schedule}', $$
SELECT status FROM http(('POST', '{SUPABASE_URL}/functions/v1/fetch-candles',
ARRAY[http_header('Content-Type','application/json'), http_header('Authorization','Bearer {SERVICE_ROLE_KEY}')],
'application/json', '{{"timeframe":{tf},"symbol":"{symbol}"}}')::http_request);
$$);""")

sql_content = '\n'.join(sql_parts)

# Save
with open('scripts/cron_jobs_final.sql', 'w') as f:
    f.write(sql_content)

print(f"{GREEN}✅ Generated: scripts/cron_jobs_final.sql{NC}\n")

# Copy to clipboard
subprocess.run('cat scripts/cron_jobs_final.sql | pbcopy', shell=True)
print(f"{GREEN}✅ Copied to clipboard!{NC}\n")

# Open Supabase
subprocess.run(['open', f'https://supabase.com/dashboard/project/{PROJECT_REF}/sql/new'])
print(f"{BLUE}🌐 Supabase SQL Editor opened!{NC}\n")

print(f"{CYAN}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━{NC}")
print(f"{YELLOW}Next Steps:{NC}")
print(f"  1. Supabase is open - just press {GREEN}Cmd+V{NC} to paste")
print(f"  2. Click {GREEN}'Run'{NC}")
print(f"  3. Should see 16 cron jobs created!")
print(f"{CYAN}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━{NC}\n")

print(f"{YELLOW}Verify with:{NC}")
print(f"{GREEN}SELECT jobname, schedule FROM cron.job WHERE jobname LIKE 'fetch-%';{NC}\n")

print(f"{GREEN}✅ Ready! Paste and run in Supabase!{NC}")
