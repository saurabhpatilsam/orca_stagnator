#!/usr/bin/env python3
"""
Verify all instruments and timeframes are collecting data
Checks:
1. Cron jobs exist for all 16 combinations
2. Edge functions work for all instruments
3. Data exists in all database tables
"""

import requests
import json
from datetime import datetime
import os
from dotenv import load_dotenv

load_dotenv('.env.configured')

SUPABASE_URL = "https://dcoukhtfcloqpfmijock.supabase.co"
SERVICE_ROLE_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6ImRjb3VraHRmY2xvcXBmbWlqb2NrIiwicm9sZSI6InNlcnZpY2Vfcm9sZSIsImlhdCI6MTc1MzcwMTgwMywiZXhwIjoyMDY5Mjc3ODAzfQ.iNzNrB0z64m8cINx0DeVCuAbcStWpMPx_bDos_vgO7w"

# Test configuration
INSTRUMENTS = {
    'NQ': 'NQZ5',
    'MNQ': 'MNQZ5', 
    'ES': 'ESZ5',
    'MES': 'MESZ5'
}

TIMEFRAMES = [5, 15, 30, 60]

def check_cron_jobs():
    """Check if all cron jobs exist in Supabase"""
    print("\n" + "="*60)
    print("📅 CHECKING CRON JOBS")
    print("="*60)
    
    query = """
    SELECT jobname, schedule, active, created_at
    FROM cron.job 
    WHERE jobname LIKE 'fetch-%'
    ORDER BY jobname;
    """
    
    headers = {
        'apikey': SERVICE_ROLE_KEY,
        'Authorization': f'Bearer {SERVICE_ROLE_KEY}',
        'Content-Type': 'application/json',
        'Prefer': 'return=representation'
    }
    
    response = requests.post(
        f'{SUPABASE_URL}/rest/v1/rpc/exec_sql',
        headers=headers,
        json={'query': query}
    )
    
    if response.status_code == 404:
        # Try direct SQL query
        print("⚠️  Cannot query cron jobs via API")
        print("   Run this SQL in Supabase SQL Editor to check cron jobs:")
        print()
        print("   SELECT jobname, schedule, active FROM cron.job WHERE jobname LIKE 'fetch-%';")
        print()
        return None
    
    print(f"Response: {response.status_code}")
    print(response.text[:500])
    return None

def test_edge_function(instrument, symbol, timeframe):
    """Test edge function for specific instrument and timeframe"""
    
    headers = {
        'Authorization': f'Bearer {SERVICE_ROLE_KEY}',
        'Content-Type': 'application/json'
    }
    
    payload = {
        'timeframe': timeframe,
        'symbol': symbol
    }
    
    try:
        response = requests.post(
            f'{SUPABASE_URL}/functions/v1/fetch-candles',
            headers=headers,
            json=payload,
            timeout=30
        )
        
        data = response.json()
        
        success = data.get('success', False)
        candles_fetched = data.get('candles_fetched', 0)
        candles_stored = data.get('candles_stored', 0)
        
        status = "✅" if success else "❌"
        
        return {
            'success': success,
            'candles_fetched': candles_fetched,
            'candles_stored': candles_stored,
            'error': data.get('error'),
            'status': status
        }
        
    except Exception as e:
        return {
            'success': False,
            'candles_fetched': 0,
            'candles_stored': 0,
            'error': str(e),
            'status': "❌"
        }

def check_table_data(instrument, timeframe):
    """Check if data exists in database table"""
    
    # Map timeframe to table suffix
    timeframe_map = {
        5: '5min',
        15: '15min',
        30: '30min',
        60: '1hour'
    }
    
    table_name = f"{instrument.lower()}_candles_{timeframe_map[timeframe]}"
    
    headers = {
        'apikey': SERVICE_ROLE_KEY,
        'Authorization': f'Bearer {SERVICE_ROLE_KEY}',
        'Content-Type': 'application/json'
    }
    
    try:
        # Query table for count
        response = requests.get(
            f'{SUPABASE_URL}/rest/v1/{table_name}?select=count',
            headers=headers,
            timeout=10
        )
        
        if response.status_code == 200:
            # Get count from Content-Range header
            content_range = response.headers.get('Content-Range', '0-0/0')
            total = int(content_range.split('/')[-1]) if '/' in content_range else 0
            return total
        else:
            return -1  # Table might not exist
            
    except Exception as e:
        return -1

def main():
    print("\n" + "="*60)
    print("🔍 COMPREHENSIVE INSTRUMENT & TIMEFRAME VERIFICATION")
    print("="*60)
    print(f"Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print()
    
    # Check cron jobs
    check_cron_jobs()
    
    # Test all combinations
    print("\n" + "="*60)
    print("🧪 TESTING EDGE FUNCTIONS (All Instruments × Timeframes)")
    print("="*60)
    
    results = {}
    
    for instrument, symbol in INSTRUMENTS.items():
        print(f"\n📊 {instrument} ({symbol})")
        print("-" * 60)
        
        results[instrument] = {}
        
        for timeframe in TIMEFRAMES:
            print(f"  Testing {timeframe}min... ", end='', flush=True)
            
            # Test edge function
            result = test_edge_function(instrument, symbol, timeframe)
            results[instrument][timeframe] = result
            
            # Check table data
            row_count = check_table_data(instrument, timeframe)
            
            # Display result
            status = result['status']
            fetched = result['candles_fetched']
            stored = result['candles_stored']
            
            print(f"{status} Fetched: {fetched}, Stored: {stored}, DB Rows: {row_count}")
            
            if not result['success'] and result['error']:
                print(f"     Error: {result['error']}")
    
    # Summary
    print("\n" + "="*60)
    print("📊 SUMMARY")
    print("="*60)
    
    total_tests = len(INSTRUMENTS) * len(TIMEFRAMES)
    successful = sum(
        1 for inst in results.values() 
        for tf_result in inst.values() 
        if tf_result['success']
    )
    
    print(f"\nTotal Tests: {total_tests}")
    print(f"Successful: {successful} ✅")
    print(f"Failed: {total_tests - successful} ❌")
    print(f"Success Rate: {(successful/total_tests)*100:.1f}%")
    
    # Detailed breakdown
    print("\n" + "-"*60)
    print("INSTRUMENT BREAKDOWN:")
    print("-"*60)
    
    for instrument, symbol in INSTRUMENTS.items():
        inst_results = results[instrument]
        inst_success = sum(1 for r in inst_results.values() if r['success'])
        status = "✅" if inst_success == len(TIMEFRAMES) else "⚠️"
        print(f"{status} {instrument:4s} ({symbol:6s}): {inst_success}/{len(TIMEFRAMES)} timeframes working")
    
    print("\n" + "-"*60)
    print("TIMEFRAME BREAKDOWN:")
    print("-"*60)
    
    for timeframe in TIMEFRAMES:
        tf_success = sum(
            1 for inst_results in results.values() 
            if inst_results[timeframe]['success']
        )
        status = "✅" if tf_success == len(INSTRUMENTS) else "⚠️"
        print(f"{status} {timeframe:2d}min: {tf_success}/{len(INSTRUMENTS)} instruments working")
    
    # Database tables check
    print("\n" + "-"*60)
    print("DATABASE TABLES STATUS:")
    print("-"*60)
    
    for instrument in INSTRUMENTS.keys():
        for timeframe in TIMEFRAMES:
            row_count = check_table_data(instrument, timeframe)
            timeframe_map = {5: '5min', 15: '15min', 30: '30min', 60: '1hour'}
            table_name = f"{instrument.lower()}_candles_{timeframe_map[timeframe]}"
            
            if row_count > 0:
                print(f"✅ {table_name:25s}: {row_count:6d} rows")
            elif row_count == 0:
                print(f"⚠️  {table_name:25s}: 0 rows (empty)")
            else:
                print(f"❌ {table_name:25s}: Table not found or error")
    
    print("\n" + "="*60)
    print("✅ VERIFICATION COMPLETE")
    print("="*60)
    print()

if __name__ == "__main__":
    main()
