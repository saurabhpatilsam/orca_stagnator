# 🐋 ORCA Trading System

**Automated Algo Trading & Backtesting Platform**

A complete production-ready trading system for ES & NQ futures with tick-by-tick data management, backtesting, and automated execution via Tradovate.

---

## 📁 Project Structure

```
orca-ven-backend/
├── automated_trading/          # Live automated trading system
│   ├── automated_trading_daemon.py      # Main trading daemon
│   ├── first_hour_breakout_strategy.py # Trading strategy
│   ├── order_processor.py               # Order execution
│   ├── supabase_order_listener.py       # Signal listener
│   ├── strategy_config.py               # Strategy parameters
│   └── send_trading_signal.py           # Signal generator
│
├── backtesting/               # Strategy backtesting
│   └── backtest.py            # Backtesting engine
│
├── data_upload/               # Tick data management
│   ├── api_server.py          # Upload API (deployed on Railway)
│   ├── upload_tick_data.py    # Upload processor
│   ├── fix_duplicates.py      # Data cleanup
│   └── frontend/              # React upload UI (deployed on Vercel)
│
├── app/                       # Core services
│   ├── services/
│   │   ├── tradingview/       # Tradovate broker integration
│   │   ├── orca_redis/        # Redis token management
│   │   └── orca_max/          # Order schemas
│   ├── api/                   # API routes
│   ├── core/                  # Configuration
│   └── middlewares/           # Logging & middleware
│
├── scripts/                   # Utility scripts
├── tests/                     # All test files
├── docs/                      # Documentation
│   ├── guides/                # Setup & deployment guides
│   └── sql/                   # Database schemas
│
├── CREDENTIALS.md             # 🔐 All API keys & credentials
└── .env                       # Environment variables
```

---

## 🚀 Quick Start

### 1. Environment Setup
```bash
cp .env.example .env
# Edit .env with your credentials (see CREDENTIALS.md)
```

### 2. Install Dependencies
```bash
pip install -r requirements.txt
cd data_upload/frontend && npm install
```

### 3. Run Components

**Data Upload API:**
```bash
python data_upload/api_server.py
```

**Automated Trading:**
```bash
python automated_trading/automated_trading_daemon.py
```

**Backtesting:**
```bash
python backtesting/backtest.py --instrument ES --date 2025-10-08
```

---

## 🔑 Key Features

### ✅ Automated Trading
- 24/7 automated strategy execution
- Real-time order placement via Tradovate API
- Redis-based token management
- Supabase signal integration

### ✅ Backtesting
- Tick-by-tick historical data replay
- Strategy performance metrics
- P&L tracking and reporting

### ✅ Data Management
- Dual Supabase support (self-hosted + cloud)
- Batch upload with real-time progress (10k rows/batch)
- Duplicate detection and filtering
- 7.9M+ tick records uploaded

### ✅ Web Interface
- Modern React UI with Tailwind CSS
- Real-time batch progress streaming
- Drag & drop file upload
- Live deployment on Vercel

---

## 🌐 Deployments

### Frontend (Vercel)
- **URL:** https://orcastagnator.vercel.app
- **Framework:** React + Vite + Tailwind CSS
- **Build:** `cd data_upload/frontend && npm run build`

### Backend API (Railway)
- **URL:** https://orca-ven-backend-production.up.railway.app
- **Entry:** `data_upload/api_server.py`
- **Auto-deploy:** Push to main branch

---

## 📊 Supported Instruments

- **ES** - E-mini S&P 500 Futures
- **NQ** - E-mini NASDAQ-100 Futures

---

## 🔐 Security

All credentials are stored in `CREDENTIALS.md` (gitignored). Includes:
- Supabase API keys (self-hosted + cloud)
- Azure Redis credentials
- Tradovate API credentials
- MCP server configurations
- GitHub access tokens

---

## 📚 Documentation

See `docs/` folder for:
- System architecture
- Deployment guides
- Strategy guides
- Database schemas
- MCP setup

---

## 🛠️ Technology Stack

- **Backend:** Python, FastAPI, Pandas
- **Frontend:** React, Vite, Tailwind CSS
- **Databases:** PostgreSQL (Supabase), Redis (Azure)
- **Trading API:** Tradovate
- **Deployment:** Railway, Vercel
- **Version Control:** GitHub

---

## 📈 Performance

- ✅ 66.67% win rate (Oct 8, 2025 backtest)
- ✅ 7.9M+ tick records managed
- ✅ Real-time order execution
- ✅ Batch uploads: 10k rows at a time

---

**Version:** 1.0.0  
**Last Updated:** 2025-10-14  
**Status:** ✅ Production Ready
