# Codebase Reorganization Plan

## New Structure

```
orca-ven-backend/
├── automated_trading/          # Live trading system
│   ├── automated_trading_daemon.py
│   ├── order_processor.py
│   ├── supabase_order_listener.py
│   ├── first_hour_breakout_strategy.py
│   ├── strategy_config.py
│   └── send_trading_signal.py
│
├── backtesting/               # Backtesting system
│   ├── backtest.py
│   └── results/
│       └── backtest_2025-10-08_ES.txt
│
├── data_upload/               # Data management
│   ├── upload_tick_data.py
│   ├── api_server.py
│   ├── fix_duplicates.py
│   └── frontend/
│
├── app/                       # Core services (keep as is)
│   ├── api/
│   ├── core/
│   ├── middlewares/
│   └── services/
│
├── scripts/                   # Utility scripts
│   ├── get_trading_token.py
│   ├── setup_github.sh
│   └── deploy.sh
│
├── tests/                     # All test files
│   ├── test_broker_implementation.py
│   ├── test_order_placement.py
│   └── test_redis_connection.py
│
├── docs/                      # Documentation
│   ├── guides/
│   └── sql/
│
├── archived/                  # Old/duplicate files
│   └── (move duplicates here)
│
├── CREDENTIALS.md            # All credentials
├── README.md                 # Main documentation
└── .env                      # Environment variables
```
