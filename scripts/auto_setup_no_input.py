#!/usr/bin/env python3
"""
Fully Automated Setup - No User Input Required
Runs everything automatically
"""

import requests
import json
import time
import sys

# Colors
RED = '\033[0;31m'
GREEN = '\033[0;32m'
YELLOW = '\033[1;33m'
BLUE = '\033[0;34m'
MAGENTA = '\033[0;35m'
CYAN = '\033[0;36m'
NC = '\033[0m'

# Supabase configuration
PROJECT_REF = "dcoukhtfcloqpfmijock"
SERVICE_ROLE_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6ImRjb3VraHRmY2xvcXBmbWlqb2NrIiwicm9sZSI6InNlcnZpY2Vfcm9sZSIsImlhdCI6MTc1MzcwMTgwMywiZXhwIjoyMDY5Mjc3ODAzfQ.iNzNrB0z64m8cINx0DeVCuAbcStWpMPx_bDos_vgO7w"
SUPABASE_URL = f"https://{PROJECT_REF}.supabase.co"

# Instruments
INSTRUMENTS = {
    'NQ': {'symbol': 'NQZ5', 'name': 'E-mini Nasdaq'},
    'MNQ': {'symbol': 'MNQZ5', 'name': 'Micro E-mini Nasdaq'},
    'ES': {'symbol': 'ESZ5', 'name': 'E-mini S&P 500'},
    'MES': {'symbol': 'MESZ5', 'name': 'Micro E-mini S&P 500'}
}

TIMEFRAMES = [5, 15, 30, 60]

def call_edge_function(function_name, payload):
    """Call edge function"""
    url = f"{SUPABASE_URL}/functions/v1/{function_name}"
    headers = {
        "Authorization": f"Bearer {SERVICE_ROLE_KEY}",
        "Content-Type": "application/json"
    }
    
    try:
        response = requests.post(url, headers=headers, json=payload, timeout=120)
        if response.status_code == 200:
            return response.json()
        else:
            return {"success": False, "error": f"HTTP {response.status_code}"}
    except Exception as e:
        return {"success": False, "error": str(e)}

print(f"{BLUE}╔════════════════════════════════════════════════════════╗")
print(f"║  🚀 Fully Automated Setup (No Input Required)         ║")
print(f"╚════════════════════════════════════════════════════════╝{NC}\n")

print(f"{CYAN}Starting in 3 seconds...{NC}")
time.sleep(3)

# Backfill historical data
print(f"\n{MAGENTA}{'━' * 60}{NC}")
print(f"{CYAN}📥 Backfilling Historical Data{NC}")
print(f"{MAGENTA}{'━' * 60}{NC}\n")

total_success = 0
total_failed = 0

for instrument_code, info in INSTRUMENTS.items():
    symbol = info['symbol']
    name = info['name']
    
    print(f"\n{BLUE}{'━' * 50}{NC}")
    print(f"{CYAN}{instrument_code} - {name} ({symbol}){NC}")
    print(f"{BLUE}{'━' * 50}{NC}")
    
    for timeframe in TIMEFRAMES:
        tf_label = f"{timeframe}min" if timeframe < 60 else "1hour"
        
        # Days to backfill
        days_map = {5: 1, 15: 2, 30: 3, 60: 7}
        days = days_map[timeframe]
        
        print(f"  {tf_label:7} ({days}d): ", end='', flush=True)
        
        payload = {
            "timeframe": timeframe,
            "symbol": symbol,
            "days": days
        }
        
        result = call_edge_function("fetch-historical-candles", payload)
        
        if result.get('success'):
            stored = result.get('candles_stored', 0)
            print(f"{GREEN}✅ {stored:3} candles{NC}")
            total_success += 1
        else:
            error = result.get('error', 'Unknown')[:40]
            print(f"{RED}❌ {error}{NC}")
            total_failed += 1
        
        time.sleep(2)

# Generate cron jobs SQL
print(f"\n{MAGENTA}{'━' * 60}{NC}")
print(f"{CYAN}⏰ Generating Cron Jobs SQL{NC}")
print(f"{MAGENTA}{'━' * 60}{NC}\n")

schedules = {5: "*/5 * * * *", 15: "*/15 * * * *", 30: "*/30 * * * *", 60: "0 * * * *"}

sql_lines = [
    "-- Auto-Generated Cron Jobs",
    "CREATE EXTENSION IF NOT EXISTS pg_cron;",
    "CREATE EXTENSION IF NOT EXISTS http;",
    "",
    "DO $$ DECLARE job_record RECORD; BEGIN",
    "  FOR job_record IN SELECT jobid FROM cron.job WHERE jobname LIKE 'fetch-%' LOOP",
    "    PERFORM cron.unschedule(job_record.jobid);",
    "  END LOOP;",
    "END $$;",
    ""
]

for instrument_code, info in INSTRUMENTS.items():
    symbol = info['symbol']
    sql_lines.append(f"\n-- {instrument_code} ({symbol})")
    
    for timeframe in TIMEFRAMES:
        job_name = f"fetch-{instrument_code.lower()}-{timeframe}min"
        schedule = schedules[timeframe]
        
        sql_lines.append(f"""SELECT cron.schedule('{job_name}', '{schedule}', $$
SELECT status FROM http(('POST', '{SUPABASE_URL}/functions/v1/fetch-candles',
ARRAY[http_header('Content-Type', 'application/json'), http_header('Authorization', 'Bearer {SERVICE_ROLE_KEY}')],
'application/json', '{{"timeframe": {timeframe}, "symbol": "{symbol}"}}')::http_request);
$$);""")

sql_content = '\n'.join(sql_lines)

# Save SQL
with open('scripts/final_cron_jobs.sql', 'w') as f:
    f.write(sql_content)

print(f"{GREEN}✅ SQL saved: scripts/final_cron_jobs.sql{NC}\n")

# Summary
print(f"\n{MAGENTA}{'━' * 60}{NC}")
print(f"{CYAN}📊 Summary{NC}")
print(f"{MAGENTA}{'━' * 60}{NC}\n")

print(f"{GREEN}✅ Successful backfills: {total_success}/16{NC}")
print(f"{RED}❌ Failed backfills: {total_failed}/16{NC}")
print(f"{CYAN}📄 Cron jobs SQL: scripts/final_cron_jobs.sql{NC}\n")

# Copy to clipboard and open Supabase
import subprocess
subprocess.run(['cat', 'scripts/final_cron_jobs.sql', '|', 'pbcopy'], shell=False, capture_output=True)
print(f"{GREEN}✅ SQL copied to clipboard!{NC}\n")

subprocess.run(['open', f'https://supabase.com/dashboard/project/{PROJECT_REF}/sql/new'])
print(f"{BLUE}🌐 Supabase SQL Editor opened!{NC}\n")

print(f"{YELLOW}Next Steps:{NC}")
print(f"  1. Paste SQL in Supabase (Cmd+V)")
print(f"  2. Click 'Run'")
print(f"  3. Verify: SELECT COUNT(*) FROM cron.job WHERE jobname LIKE 'fetch-%';")
print()

print(f"{GREEN}╔════════════════════════════════════════════════════════╗")
print(f"║  ✅ Automated Setup Complete!                         ║")
print(f"╚════════════════════════════════════════════════════════╝{NC}\n")
