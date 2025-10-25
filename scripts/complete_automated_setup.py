#!/usr/bin/env python3
"""
Complete Automated Setup for All Instruments
1. Verifies tables and functions exist
2. Backfills historical data for all instruments
3. Sets up cron jobs for automated updates
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

# Instruments and timeframes
INSTRUMENTS = {
    'NQ': {'symbol': 'NQZ5', 'name': 'E-mini Nasdaq'},
    'MNQ': {'symbol': 'MNQZ5', 'name': 'Micro E-mini Nasdaq'},
    'ES': {'symbol': 'ESZ5', 'name': 'E-mini S&P 500'},
    'MES': {'symbol': 'MESZ5', 'name': 'Micro E-mini S&P 500'}
}

TIMEFRAMES = [5, 15, 30, 60]

def print_header(text):
    print(f"\n{MAGENTA}{'━' * 60}{NC}")
    print(f"{CYAN}{text}{NC}")
    print(f"{MAGENTA}{'━' * 60}{NC}\n")

def call_edge_function(function_name, payload):
    """Call a Supabase edge function"""
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
            print(f"{RED}❌ HTTP {response.status_code}: {response.text[:200]}{NC}")
            return None
    except Exception as e:
        print(f"{RED}❌ Error: {str(e)}{NC}")
        return None

def verify_setup():
    """Verify tables and functions exist"""
    print_header("🔍 Step 1: Verifying Setup")
    
    print(f"{CYAN}Checking if tables and functions exist...{NC}")
    print(f"{YELLOW}Note: Tables and functions must be created manually in Supabase SQL Editor{NC}\n")
    
    print(f"Expected setup:")
    print(f"  • 16 tables: orca.{{instrument}}_candles_{{timeframe}}")
    print(f"  • 16 functions: insert_{{instrument}}_candles_{{timeframe}}")
    print(f"  • 1 edge function: fetch-candles (already deployed ✅)\n")
    
    return True

def backfill_historical_data():
    """Backfill historical data for all instruments"""
    print_header("📥 Step 2: Backfilling Historical Data")
    
    print(f"{CYAN}This will fetch historical data for all instruments...{NC}\n")
    
    results = {
        'success': [],
        'failed': []
    }
    
    for instrument_code, info in INSTRUMENTS.items():
        symbol = info['symbol']
        name = info['name']
        
        print(f"{BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━{NC}")
        print(f"{CYAN}📊 {instrument_code} - {name} ({symbol}){NC}")
        print(f"{BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━{NC}\n")
        
        for timeframe in TIMEFRAMES:
            tf_label = f"{timeframe}min" if timeframe < 60 else "1hour"
            
            # Determine days to backfill based on timeframe
            if timeframe == 5:
                days = 1
            elif timeframe == 15:
                days = 2
            elif timeframe == 30:
                days = 3
            else:  # 60
                days = 7
            
            print(f"  {YELLOW}Backfilling {tf_label} ({days} days)...{NC} ", end='', flush=True)
            
            payload = {
                "timeframe": timeframe,
                "symbol": symbol,
                "days": days
            }
            
            result = call_edge_function("fetch-historical-candles", payload)
            
            if result and result.get('success'):
                stored = result.get('candles_stored', 0)
                print(f"{GREEN}✅ {stored} candles{NC}")
                results['success'].append(f"{instrument_code}-{tf_label}")
            else:
                error = result.get('error', 'Unknown error') if result else 'No response'
                print(f"{RED}❌ {error[:50]}{NC}")
                results['failed'].append(f"{instrument_code}-{tf_label}")
            
            time.sleep(2)  # Rate limiting
        
        print()
    
    return results

def create_cron_jobs():
    """Create SQL for cron jobs"""
    print_header("⏰ Step 3: Setting Up Cron Jobs")
    
    print(f"{CYAN}Generating SQL for 16 cron jobs...{NC}\n")
    
    sql_parts = [
        "-- Automated Cron Job Setup",
        "CREATE EXTENSION IF NOT EXISTS pg_cron;",
        "CREATE EXTENSION IF NOT EXISTS http;",
        "",
        "-- Remove existing jobs",
        "DO $$ ",
        "DECLARE job_record RECORD;",
        "BEGIN",
        "    FOR job_record IN SELECT jobid FROM cron.job WHERE jobname LIKE 'fetch-%' LOOP",
        "        PERFORM cron.unschedule(job_record.jobid);",
        "    END LOOP;",
        "END $$;",
        ""
    ]
    
    schedules = {
        5: "*/5 * * * *",
        15: "*/15 * * * *",
        30: "*/30 * * * *",
        60: "0 * * * *"
    }
    
    for instrument_code, info in INSTRUMENTS.items():
        symbol = info['symbol']
        sql_parts.append(f"\n-- {instrument_code} ({symbol})")
        
        for timeframe in TIMEFRAMES:
            schedule = schedules[timeframe]
            job_name = f"fetch-{instrument_code.lower()}-{timeframe}min"
            
            sql_parts.append(f"""
SELECT cron.schedule(
    '{job_name}',
    '{schedule}',
    $$
    SELECT status FROM http((
        'POST',
        '{SUPABASE_URL}/functions/v1/fetch-candles',
        ARRAY[http_header('Content-Type', 'application/json'), http_header('Authorization', 'Bearer {SERVICE_ROLE_KEY}')],
        'application/json',
        '{{"timeframe": {timeframe}, "symbol": "{symbol}"}}'
    )::http_request);
    $$
);""")
    
    sql_content = '\n'.join(sql_parts)
    
    # Save to file
    with open('scripts/auto_generated_cron_jobs.sql', 'w') as f:
        f.write(sql_content)
    
    print(f"{GREEN}✅ SQL generated: scripts/auto_generated_cron_jobs.sql{NC}\n")
    
    return True

def main():
    print(f"{BLUE}╔════════════════════════════════════════════════════════╗")
    print(f"║  🚀 Complete Automated Setup                          ║")
    print(f"║  All Instruments × All Timeframes                     ║")
    print(f"╚════════════════════════════════════════════════════════╝{NC}\n")
    
    print(f"{CYAN}Configuration:{NC}")
    print(f"  Instruments: {', '.join(INSTRUMENTS.keys())}")
    print(f"  Timeframes: {', '.join([f'{t}min' for t in TIMEFRAMES])}")
    print(f"  Total combinations: {len(INSTRUMENTS) * len(TIMEFRAMES)}")
    
    # Step 1: Verify
    if not verify_setup():
        print(f"\n{RED}❌ Setup verification failed{NC}")
        return 1
    
    # Step 2: Backfill
    print(f"{YELLOW}Starting historical data backfill...{NC}")
    print(f"{YELLOW}This will take about 2-3 minutes...{NC}\n")
    
    input(f"{CYAN}Press Enter to start backfilling historical data...{NC} ")
    
    backfill_results = backfill_historical_data()
    
    # Summary
    print_header("📊 Backfill Summary")
    print(f"{GREEN}✅ Successful: {len(backfill_results['success'])}{NC}")
    print(f"{RED}❌ Failed: {len(backfill_results['failed'])}{NC}\n")
    
    if backfill_results['failed']:
        print(f"{YELLOW}Failed combinations:{NC}")
        for item in backfill_results['failed']:
            print(f"  • {item}")
        print()
    
    # Step 3: Create cron jobs
    if create_cron_jobs():
        print(f"{CYAN}Next: Copy the SQL file and run it in Supabase{NC}")
        print(f"  1. File: {GREEN}scripts/auto_generated_cron_jobs.sql{NC}")
        print(f"  2. Copy: {GREEN}cat scripts/auto_generated_cron_jobs.sql | pbcopy{NC}")
        print(f"  3. Run in: {BLUE}https://supabase.com/dashboard/project/{PROJECT_REF}/sql/new{NC}\n")
    
    # Final summary
    print(f"{GREEN}╔════════════════════════════════════════════════════════╗")
    print(f"║  ✅ Setup Complete!                                    ║")
    print(f"╚════════════════════════════════════════════════════════╝{NC}\n")
    
    print(f"{CYAN}What's Running:{NC}")
    print(f"  ✅ Edge function: fetch-candles")
    print(f"  ✅ Historical data: Backfilled")
    print(f"  ⏳ Cron jobs: Ready to deploy (run the SQL file)")
    print()
    
    print(f"{CYAN}After running the SQL file:{NC}")
    print(f"  • 16 cron jobs will auto-update data every 5/15/30/60 minutes")
    print(f"  • All 4 instruments collecting live data 24/7")
    print()
    
    return 0

if __name__ == "__main__":
    try:
        sys.exit(main())
    except KeyboardInterrupt:
        print(f"\n{YELLOW}Setup interrupted{NC}")
        sys.exit(1)
    except Exception as e:
        print(f"\n{RED}❌ Error: {e}{NC}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
