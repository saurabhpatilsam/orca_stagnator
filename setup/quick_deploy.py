#!/usr/bin/env python3
"""
Quick Deploy - Install RPC Functions and Cron Jobs
Since tables already exist, we just need to add the functions.
"""

import os
import sys

print("=" * 70)
print("🚀 QUICK DEPLOY - RPC FUNCTIONS & CRON JOBS")
print("=" * 70)
print()

# Read the SQL files
print("📖 Reading SQL files...")
try:
    with open('setup/database/02_create_rpc_functions.sql', 'r') as f:
        rpc_sql = f.read()
    
    with open('setup/database/03_create_cron_jobs.sql', 'r') as f:
        cron_sql = f.read()
    
    print("✅ SQL files loaded")
    print(f"   - RPC Functions SQL: {len(rpc_sql)} characters")
    print(f"   - Cron Jobs SQL: {len(cron_sql)} characters")
except Exception as e:
    print(f"❌ Error reading SQL files: {e}")
    sys.exit(1)

print()
print("=" * 70)
print("📋 DEPLOYMENT OPTIONS")
print("=" * 70)
print()
print("Choose one:")
print()
print("Option 1 - Copy SQL to Clipboard (Recommended)")
print("   I'll copy the SQL, you paste in Supabase SQL Editor")
print()
print("Option 2 - Save to single file")
print("   I'll create one file with both RPC functions and cron jobs")
print()
print("Option 3 - Show SQL content")
print("   I'll display the SQL so you can copy it manually")
print()

choice = input("Enter choice (1/2/3): ").strip()

if choice == '1':
    try:
        import pyperclip
        combined_sql = rpc_sql + "\n\n" + cron_sql
        pyperclip.copy(combined_sql)
        print()
        print("✅ SQL copied to clipboard!")
        print()
        print("Next steps:")
        print("1. Open: https://supabase.com/dashboard/project/dcoukhtfcloqpfmijock/sql/new")
        print("2. Paste (Cmd+V)")
        print("3. Click 'Run'")
        print("4. Test: bash data-collection/verification/test_all_edge_functions.sh")
    except ImportError:
        print()
        print("⚠️  pyperclip not installed")
        print("   Run: pip install pyperclip")
        print("   Or choose option 2 or 3")

elif choice == '2':
    output_file = 'setup/database/DEPLOY_NOW.sql'
    combined_sql = f"""-- ========================================
-- QUICK DEPLOY - RPC FUNCTIONS & CRON JOBS
-- ========================================
-- Tables already exist, this adds functions and automation
-- Run this in Supabase SQL Editor

{rpc_sql}

{cron_sql}

-- ========================================
-- DONE! Test with:
-- bash data-collection/verification/test_all_edge_functions.sh
-- ========================================
"""
    
    with open(output_file, 'w') as f:
        f.write(combined_sql)
    
    print()
    print(f"✅ SQL saved to: {output_file}")
    print()
    print("Next steps:")
    print(f"1. Open the file: {output_file}")
    print("2. Copy all content")
    print("3. Open: https://supabase.com/dashboard/project/dcoukhtfcloqpfmijock/sql/new")
    print("4. Paste and click 'Run'")
    print("5. Test: bash data-collection/verification/test_all_edge_functions.sh")

elif choice == '3':
    print()
    print("=" * 70)
    print("📄 RPC FUNCTIONS SQL")
    print("=" * 70)
    print()
    print(rpc_sql[:1000])
    print("\n... (truncated, see setup/database/02_create_rpc_functions.sql for full content) ...\n")
    print()
    print("=" * 70)
    print("📄 CRON JOBS SQL")
    print("=" * 70)
    print()
    print(cron_sql[:1000])
    print("\n... (truncated, see setup/database/03_create_cron_jobs.sql for full content) ...\n")
    
else:
    print()
    print("❌ Invalid choice")
    sys.exit(1)

print()
print("=" * 70)
print("🎯 MANUAL DEPLOYMENT LINK")
print("=" * 70)
print()
print("Open this link and paste the SQL:")
print("https://supabase.com/dashboard/project/dcoukhtfcloqpfmijock/sql/new")
print()
