# 🦈 ORCA Trading Platform - Backend

> Automated candlestick data collection system for futures trading

## 🎯 Quick Start

### Current Status: 95% Complete ✅

**What's Working**:
- ✅ Edge functions (100% operational)
- ✅ Token management (fully automated)
- ✅ Repository organized

**Next Step**: Deploy database (2 minutes)

```bash
# Get database password from Supabase
# Then run:
bash setup/deploy_database.sh YOUR_DATABASE_PASSWORD
```

**Or**: Follow [SETUP_COMPLETE_GUIDE.md](SETUP_COMPLETE_GUIDE.md)

---

## 📊 System Overview

### Instruments Tracked
- **NQ** - E-mini Nasdaq (NQZ5)
- **MNQ** - Micro E-mini Nasdaq (MNQZ5)
- **ES** - E-mini S&P 500 (ESZ5)
- **MES** - Micro E-mini S&P 500 (MESZ5)

### Timeframes
- 5 minutes
- 15 minutes
- 30 minutes  
- 60 minutes (1 hour)

### Total: 16 Automated Data Streams

---

## 🏗️ Architecture

```
Tradovate API
     ↓
Edge Functions (Supabase)
     ↓
Database (PostgreSQL)
     ↓
Your Trading Application
```

### Components:

1. **Edge Functions** (Supabase)
   - `fetch-candles`: Real-time data collection
   - `fetch-historical-candles`: Historical data
   - `scheduler`: Orchestration
   - `token-manager`: Token management

2. **Database** (PostgreSQL)
   - 16 tables (orca schema)
   - 16 RPC functions
   - 16 cron jobs (automated)

3. **Token Management**
   - Auto-refresh on every edge function call
   - Stored in Redis
   - No manual intervention needed

---

## 📁 Project Structure

```
orca-ven-backend-main/
├── setup/                  # Setup scripts & database SQL
├── edge-functions/         # Supabase edge functions
├── data-collection/        # Token management & verification
├── trading/               # Trading bots & backtesting
├── app/                   # API backend
├── frontend/              # Frontend application
├── documentation/         # All documentation
└── archived/              # Old files
```

---

## 🚀 Deployment

### Prerequisites
- Supabase account with project ID: `dcoukhtfcloqpfmijock`
- Redis instance (Azure Redis)
- Tradovate API credentials

### Setup Steps

1. **Deploy Database** (Choose one):
   
   **Option A - Automated** (2 min):
   ```bash
   bash setup/deploy_database.sh YOUR_DB_PASSWORD
   ```

   **Option B - Manual** (5 min):
   - Open Supabase SQL Editor
   - Run files in `setup/database/` sequentially

2. **Test System**:
   ```bash
   bash data-collection/verification/test_all_edge_functions.sh
   ```

3. **Verify Data Collection**:
   ```sql
   SELECT COUNT(*) FROM orca.nq_candles_5min;
   ```

---

## ✅ Verification

After deployment, you should see:
- ✅ 16 tables created
- ✅ 16 RPC functions
- ✅ 16 active cron jobs
- ✅ Data collecting every 5/15/30/60 minutes

Test command:
```bash
bash data-collection/verification/test_all_edge_functions.sh
```

Expected output:
```
Testing NQZ5...
  5min: ✅ Fetched: 10, Stored: 10
  15min: ✅ Fetched: 10, Stored: 10
  ...
```

---

## 📚 Documentation

- [SETUP_COMPLETE_GUIDE.md](SETUP_COMPLETE_GUIDE.md) - Complete setup instructions
- [FINAL_STATUS_REPORT.md](FINAL_STATUS_REPORT.md) - Current status
- [PROJECT_STRUCTURE.md](PROJECT_STRUCTURE.md) - Project organization
- `setup/database/README.md` - Database setup details
- `documentation/` - Full documentation

---

## 🔧 Configuration

### Environment Variables
Located in `.env.configured`:
- Redis credentials
- Supabase credentials
- Tradovate API keys

### Database
- Host: `db.dcoukhtfcloqpfmijock.supabase.co`
- Schema: `orca`
- Tables: 16 (automated candle data)

---

## 🎯 Key Features

- **Automated Collection**: Data collected every 5/15/30/60 minutes
- **Token Management**: Auto-refresh, no manual intervention
- **Multi-Instrument**: 4 instruments tracked simultaneously
- **Error Handling**: Robust retry mechanisms
- **Monitoring**: Built-in health checks
- **Clean Architecture**: Professional folder structure

---

## 📞 Quick Commands

```bash
# Deploy database
bash setup/deploy_database.sh YOUR_PASSWORD

# Test edge functions
bash data-collection/verification/test_all_edge_functions.sh

# Refresh tokens manually
python3 data-collection/token-management/token_generator_and_redis_manager.py

# Check data
python3 data-collection/verification/verify_all_instruments.py

# Clean repository
bash scripts/cleanup/cleanup_repo.sh
```

---

## 🆘 Support

### Common Issues

**Data not collecting?**
1. Check database is deployed
2. Verify cron jobs are active
3. Test edge functions

**Tokens expired?**
- Run: `python3 data-collection/token-management/token_generator_and_redis_manager.py`

**Edge functions failing?**
- Check Supabase logs
- Verify Redis connection
- Test tokens in Redis

---

## 🏆 Status

**Current**: 95% Complete
**Next**: Deploy database (2 minutes)
**Then**: 100% Operational - Running 24/7! 🎉

---

## 📄 License

Proprietary - ORCA Trading Platform

---

**Made with ❤️ for algorithmic trading**
