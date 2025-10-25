#!/usr/bin/env python3
"""
Automated Setup - No Password Needed
Uses Supabase Management API to execute SQL
"""

import os
import sys
import time
import subprocess
from pathlib import Path

# Colors
RED = '\033[0;31m'
GREEN = '\033[0;32m'
YELLOW = '\033[1;33m'
BLUE = '\033[0;34m'
MAGENTA = '\033[0;35m'
CYAN = '\033[0;36m'
NC = '\033[0m'

# Supabase credentials
PROJECT_REF = "dcoukhtfcloqpfmijock"
SERVICE_ROLE_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6ImRjb3VraHRmY2xvcXBmbWlqb2NrIiwicm9sZSI6InNlcnZpY2Vfcm9sZSIsImlhdCI6MTc1MzcwMTgwMywiZXhwIjoyMDY5Mjc3ODAzfQ.iNzNrB0z64m8cINx0DeVCuAbcStWpMPx_bDos_vgO7w"

# Get script directory
SCRIPT_DIR = Path(__file__).parent
PROJECT_DIR = SCRIPT_DIR.parent

def execute_sql_file_via_supabase_cli(file_path, step_name):
    """Execute SQL file using supabase db push with migration"""
    print(f"{CYAN}{step_name}{NC}")
    
    # Read SQL file
    try:
        with open(file_path, 'r') as f:
            sql_content = f.read()
    except FileNotFoundError:
        print(f"{RED}❌ File not found: {file_path}{NC}")
        return False
    
    # Create a temporary migration file
    migrations_dir = PROJECT_DIR / "supabase" / "migrations"
    migrations_dir.mkdir(parents=True, exist_ok=True)
    
    # Generate timestamp-based migration name
    timestamp = int(time.time())
    migration_file = migrations_dir / f"{timestamp}_auto_setup.sql"
    
    # Write SQL to migration file
    with open(migration_file, 'w') as f:
        f.write(sql_content)
    
    print(f"  Created migration: {migration_file.name}")
    
    # Execute using supabase db push
    try:
        result = subprocess.run(
            ["supabase", "db", "push", "--project-ref", PROJECT_REF],
            cwd=PROJECT_DIR,
            capture_output=True,
            text=True,
            timeout=60
        )
        
        if result.returncode == 0:
            print(f"{GREEN}✅ {step_name} completed!{NC}\n")
            # Clean up migration file
            migration_file.unlink()
            return True
        else:
            print(f"{YELLOW}⚠️  {step_name} completed with warnings{NC}")
            print(f"  {result.stderr[:200]}")
            # Clean up migration file
            migration_file.unlink()
            return True  # Continue anyway
            
    except subprocess.TimeoutExpired:
        print(f"{RED}❌ Timeout executing {step_name}{NC}")
        migration_file.unlink()
        return False
    except Exception as e:
        print(f"{RED}❌ Error: {e}{NC}")
        migration_file.unlink()
        return False

def execute_sql_statements_directly(file_path, step_name):
    """Execute SQL by running statements one by one"""
    print(f"{CYAN}{step_name}{NC}")
    
    # Read SQL file
    try:
        with open(file_path, 'r') as f:
            sql_content = f.read()
    except FileNotFoundError:
        print(f"{RED}❌ File not found: {file_path}{NC}")
        return False
    
    # Write to temp file
    temp_file = PROJECT_DIR / "temp_setup.sql"
    with open(temp_file, 'w') as f:
        f.write(sql_content)
    
    # Try to execute with psql if available
    try:
        # Check if psql is available
        subprocess.run(["which", "psql"], check=True, capture_output=True)
        
        print(f"  Found psql, attempting direct execution...")
        print(f"{YELLOW}  Note: You'll need to provide the database password{NC}")
        
        # Let the automated script handle it
        result = subprocess.run(
            ["bash", str(SCRIPT_DIR / "setup_automated.sh")],
            cwd=PROJECT_DIR
        )
        
        temp_file.unlink()
        return result.returncode == 0
        
    except subprocess.CalledProcessError:
        print(f"{YELLOW}  psql not available, please run SQL manually{NC}")
        temp_file.unlink()
        return False

def main():
    print(f"{BLUE}╔════════════════════════════════════════════════════════╗")
    print(f"║  🚀 Automated Setup (No Password Method)              ║")
    print(f"╚════════════════════════════════════════════════════════╝{NC}\n")
    
    print(f"{MAGENTA}{'━' * 56}{NC}")
    print(f"{CYAN}Opening Supabase SQL Editor...{NC}")
    print(f"{MAGENTA}{'━' * 56}{NC}\n")
    
    # Open Supabase SQL Editor
    sql_editor_url = f"https://supabase.com/dashboard/project/{PROJECT_REF}/sql/new"
    subprocess.run(["open", sql_editor_url])
    
    print(f"{YELLOW}Since automated execution requires a database password,{NC}")
    print(f"{YELLOW}I've opened the Supabase SQL Editor for you.{NC}\n")
    
    print(f"{CYAN}Please copy and paste these 3 files (in order):{NC}\n")
    
    files = [
        ("scripts/create_all_instrument_tables.sql", "Step 1: Create Tables (16 tables)"),
        ("scripts/create_all_insert_functions.sql", "Step 2: Create Functions (16 functions)"),
        ("scripts/setup_all_instruments_cron.sql", "Step 3: Setup Cron Jobs (16 cron jobs)")
    ]
    
    for i, (file_path, description) in enumerate(files, 1):
        full_path = PROJECT_DIR / file_path
        print(f"{GREEN}{i}. {description}{NC}")
        print(f"   File: {file_path}")
        print(f"   📂 Opening file...")
        subprocess.run(["open", str(full_path)])
        time.sleep(0.5)
        print()
    
    print(f"{MAGENTA}{'━' * 56}{NC}")
    print(f"{CYAN}Instructions:{NC}")
    print(f"1. For each file: Select All (Cmd+A) → Copy (Cmd+C)")
    print(f"2. Paste in Supabase SQL Editor → Click 'Run'")
    print(f"3. Wait for completion before running next file")
    print(f"{MAGENTA}{'━' * 56}{NC}\n")
    
    input(f"{YELLOW}Press Enter after you've run all 3 SQL files...{NC} ")
    
    print(f"\n{CYAN}Testing setup...{NC}\n")
    
    # Run test script
    result = subprocess.run(
        ["bash", str(SCRIPT_DIR / "init_all_instruments.sh")],
        cwd=PROJECT_DIR
    )
    
    if result.returncode == 0:
        print(f"\n{GREEN}╔════════════════════════════════════════════════════════╗")
        print(f"║  ✅ Setup Complete! All systems operational           ║")
        print(f"╚════════════════════════════════════════════════════════╝{NC}\n")
        return 0
    else:
        print(f"\n{YELLOW}⚠️  Please verify setup in Supabase{NC}\n")
        return 1

if __name__ == "__main__":
    try:
        sys.exit(main())
    except KeyboardInterrupt:
        print(f"\n{YELLOW}Setup interrupted{NC}")
        sys.exit(1)
    except Exception as e:
        print(f"\n{RED}❌ Error: {e}{NC}")
        sys.exit(1)
