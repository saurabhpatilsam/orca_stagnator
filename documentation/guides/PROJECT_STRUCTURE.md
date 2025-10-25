# 📁 ORCA PROJECT STRUCTURE

## Organized Directory Layout

```
orca-ven-backend-main/
│
├── 📂 setup/                        # All setup and configuration
│   ├── database/                    # Database setup scripts
│   │   ├── 01_create_schema_and_tables.sql
│   │   ├── 02_create_rpc_functions.sql
│   │   ├── 03_create_cron_jobs.sql
│   │   ├── 04_verify_setup.sql
│   │   └── README.md
│   ├── environment/                 # Environment configuration
│   │   ├── .env.example
│   │   └── setup_environment.sh
│   └── deployment/                  # Deployment scripts
│       └── deploy_all.sh
│
├── 📂 edge-functions/               # Edge functions code
│   ├── fetch-candles/              # Main candlestick fetcher
│   ├── fetch-historical/           # Historical data fetcher
│   ├── scheduler/                  # Scheduler function
│   └── token-manager/              # Token management
│
├── 📂 data-collection/              # Data collection scripts
│   ├── token-management/           # Token generation and refresh
│   │   ├── token_generator.py
│   │   ├── auto_refresh_tokens.sh
│   │   └── redis_sync.py
│   ├── verification/               # Testing and verification
│   │   ├── test_all_functions.sh
│   │   ├── verify_data.py
│   │   └── health_check.sh
│   └── monitoring/                 # Monitoring scripts
│       └── monitor_data.py
│
├── 📂 trading/                      # Trading system
│   ├── automated/                  # Automated trading
│   ├── backtesting/               # Backtesting system
│   └── strategies/                # Trading strategies
│
├── 📂 api/                         # API backend
│   ├── app/                       # Main application
│   └── frontend/                  # Frontend code
│
├── 📂 documentation/               # All documentation
│   ├── setup/                    # Setup guides
│   ├── api/                      # API documentation
│   └── guides/                   # User guides
│
├── 📂 scripts/                     # Utility scripts
│   ├── cleanup/                  # Cleanup scripts
│   ├── migration/                # Migration scripts
│   └── utilities/                # General utilities
│
├── 📂 logs/                        # Log files
│
└── 📂 archived/                    # Old/archived files
```

## File Organization Plan

### Phase 1: Core Edge Functions (Priority: High)
**Location**: `edge-functions/`
- Move all Supabase edge functions
- Keep each function in its own folder
- Include README for each function

### Phase 2: Data Collection (Priority: High)
**Location**: `data-collection/`
- Token management scripts
- Verification and testing scripts
- Monitoring tools

### Phase 3: Trading System (Priority: Medium)
**Location**: `trading/`
- Automated trading bots
- Backtesting system
- Strategy implementations

### Phase 4: Documentation (Priority: Medium)
**Location**: `documentation/`
- Setup guides
- API documentation
- User manuals

### Phase 5: Cleanup (Priority: Low)
**Location**: `archived/`
- Move old/unused files
- Keep for reference only

## Current Issues to Fix

1. **Database Setup**: ❌ Not deployed
   - Solution: Run SQL scripts in `setup/database/`

2. **Cron Jobs**: ⚠️ Unknown status
   - Solution: Verify with `04_verify_setup.sql`

3. **Data Storage**: ❌ 0 candles being stored
   - Solution: Deploy database infrastructure

4. **File Organization**: ❌ Files scattered
   - Solution: Reorganize as per structure above

## Quick Actions Required

1. **Deploy Database** (5 minutes)
   ```bash
   # Open Supabase SQL Editor
   # Run files in setup/database/ folder
   ```

2. **Test System** (2 minutes)
   ```bash
   bash scripts/test_all_edge_functions.sh
   ```

3. **Verify Data Collection** (1 minute)
   ```bash
   # Check if data is being stored
   python3 scripts/verify_all_instruments.py
   ```

## Benefits of New Structure

✅ **Clear Separation**: Each component in its own folder
✅ **Easy Navigation**: Logical grouping of related files
✅ **Better Maintenance**: Easy to find and update files
✅ **Professional**: Industry-standard organization
✅ **Scalable**: Easy to add new components

## Next Steps

1. Create folder structure
2. Move files to appropriate locations
3. Update import paths if needed
4. Create README for each major folder
5. Archive old/unused files
