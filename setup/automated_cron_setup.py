#!/usr/bin/env python3
"""
Fully Automated Cron Job Creation via Supabase API
Creates all 16 cron jobs automatically - no manual steps needed!
"""

import requests
import json
import time

# Configuration
SUPABASE_PROJECT_ID = "dcoukhtfcloqpfmijock"
SUPABASE_URL = f"https://{SUPABASE_PROJECT_ID}.supabase.co"
SUPABASE_TOKEN = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.ewogICJyb2xlIjogInNlcnZpY2Vfcm9sZSIsCiAgImlzcyI6ICJzdXBhYmFzZSIsCiAgImlhdCI6IDE3Mjc4MDc0MDAsCiAgImV4cCI6IDE4ODU1NzM4MDAKfQ.OycUXKTNplHa5qAUj6-RByHhAQ6Fqh4tLI2quSKo6y4"
SERVICE_ROLE_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6ImRjb3VraHRmY2xvcXBmbWlqb2NrIiwicm9sZSI6InNlcnZpY2Vfcm9sZSIsImlhdCI6MTc1MzcwMTgwMywiZXhwIjoyMDY5Mjc3ODAzfQ.iNzNrB0z64m8cINx0DeVCuAbcStWpMPx_bDos_vgO7w"

# All 16 cron jobs configuration (skip the first one that was already created)
CRON_JOBS = [
    # NQ - Skip first one already created
    {"name": "fetch-nq-15min", "schedule": "*/15 * * * *", "symbol": "NQZ5", "timeframe": 15},
    {"name": "fetch-nq-30min", "schedule": "*/30 * * * *", "symbol": "NQZ5", "timeframe": 30},
    {"name": "fetch-nq-60min", "schedule": "0 * * * *", "symbol": "NQZ5", "timeframe": 60},
    
    # MNQ
    {"name": "fetch-mnq-5min", "schedule": "*/5 * * * *", "symbol": "MNQZ5", "timeframe": 5},
    {"name": "fetch-mnq-15min", "schedule": "*/15 * * * *", "symbol": "MNQZ5", "timeframe": 15},
    {"name": "fetch-mnq-30min", "schedule": "*/30 * * * *", "symbol": "MNQZ5", "timeframe": 30},
    {"name": "fetch-mnq-60min", "schedule": "0 * * * *", "symbol": "MNQZ5", "timeframe": 60},
    
    # ES
    {"name": "fetch-es-5min", "schedule": "*/5 * * * *", "symbol": "ESZ5", "timeframe": 5},
    {"name": "fetch-es-15min", "schedule": "*/15 * * * *", "symbol": "ESZ5", "timeframe": 15},
    {"name": "fetch-es-30min", "schedule": "*/30 * * * *", "symbol": "ESZ5", "timeframe": 30},
    {"name": "fetch-es-60min", "schedule": "0 * * * *", "symbol": "ESZ5", "timeframe": 60},
    
    # MES
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
    return sql.strip()

def execute_sql_via_api(sql):
    """Execute SQL via Supabase Management API"""
    url = f"https://api.supabase.com/v1/projects/{SUPABASE_PROJECT_ID}/database/query"
    
    headers = {
        'Authorization': f'Bearer {SUPABASE_TOKEN}',
        'Content-Type': 'application/json'
    }
    
    payload = {
        'query': sql
    }
    
    try:
        response = requests.post(url, headers=headers, json=payload, timeout=30)
        return response.status_code, response.json() if response.text else None
    except requests.Timeout:
        return 408, {"error": "Request timed out"}
    except Exception as e:
        return 500, {"error": str(e)}

def main():
    print("=" * 70)
    print("🚀 AUTOMATED CRON JOB CREATION")
    print("=" * 70)
    print()
    print("Creating 15 remaining cron jobs (1 already exists)...")
    print()
    
    created = 0
    failed = 0
    errors = []
    
    for i, job in enumerate(CRON_JOBS, 1):
        print(f"[{i}/15] Creating {job['name']}... ", end='', flush=True)
        
        sql = create_cron_job_sql(job)
        status_code, result = execute_sql_via_api(sql)
        
        if status_code == 200:
            print("✅")
            created += 1
        else:
            print(f"❌ (Status: {status_code})")
            failed += 1
            errors.append({
                'job': job['name'],
                'status': status_code,
                'error': result
            })
        
        # Small delay to avoid overwhelming the API
        time.sleep(0.5)
    
    print()
    print("=" * 70)
    print("📊 RESULTS")
    print("=" * 70)
    print(f"✅ Successfully created: {created + 1}/16 jobs (including first one)")
    print(f"❌ Failed: {failed}/15")
    
    if errors:
        print()
        print("Errors:")
        for err in errors:
            print(f"  - {err['job']}: {err['error']}")
    
    print()
    print("=" * 70)
    print("🔍 VERIFICATION")
    print("=" * 70)
    print()
    print("Run this SQL in Supabase to verify all jobs:")
    print()
    print("SELECT jobname, schedule, active FROM cron.job")
    print("WHERE jobname LIKE 'fetch-%' ORDER BY jobname;")
    print()
    print("Expected: 16 rows")
    print()

if __name__ == "__main__":
    main()
