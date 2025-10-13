"""
Strategy Configuration File
============================
Centralized configuration for all trading strategies.
Modify these settings to customize your strategy behavior.
"""

import os
from dotenv import load_dotenv

load_dotenv()

# ============================================================================
# INSTRUMENT SETTINGS
# ============================================================================

# Primary instrument to trade
# ES (E-mini S&P 500): ESZ5, ESH6, ESM6, ESU6 (Z=Dec, H=Mar, M=Jun, U=Sep)
# NQ (E-mini Nasdaq): NQZ5, NQH6, NQM6, NQU6
INSTRUMENT = os.getenv("STRATEGY_INSTRUMENT", "ESZ5")

# Alternative instrument (if primary is not available)
ALTERNATIVE_INSTRUMENT = os.getenv("ALTERNATIVE_INSTRUMENT", "NQZ5")

# Tradovate account name
ACCOUNT_NAME = os.getenv("ACCOUNT_NAME", "PAAPEX1361890000010")

# ============================================================================
# MARKET TIMING (US EASTERN TIME)
# ============================================================================

# Market open time (9:30 AM ET for regular session)
MARKET_OPEN_HOUR = 9
MARKET_OPEN_MINUTE = 30

# Duration of first candle in minutes
FIRST_HOUR_DURATION_MINUTES = 60  # 60 minutes = 1 hour

# ============================================================================
# ENTRY RULES
# ============================================================================

# Points spacing between each order
POINTS_SPACING = 9

# Maximum number of orders on each side (long and short)
MAX_ORDERS_PER_SIDE = 5

# ============================================================================
# RISK MANAGEMENT
# ============================================================================

# Stop loss in points
STOP_LOSS_POINTS = 5

# Take profit in points
TAKE_PROFIT_POINTS = 5

# Quantity per order (number of contracts)
QUANTITY_PER_ORDER = 1

# ============================================================================
# ORDER SETTINGS
# ============================================================================

# Order type: "limit", "market", or "stop"
ORDER_TYPE = "limit"

# Strategy name (for tracking in Supabase)
STRATEGY_NAME = "first_hour_breakout"

# ============================================================================
# DATA PROVIDER SETTINGS
# ============================================================================

# Data provider: "tradingview", "interactive_brokers", "manual"
DATA_PROVIDER = os.getenv("DATA_PROVIDER", "manual")

# TradingView settings (if using TradingView)
TRADINGVIEW_USERNAME = os.getenv("TRADINGVIEW_USERNAME", "")
TRADINGVIEW_PASSWORD = os.getenv("TRADINGVIEW_PASSWORD", "")

# ============================================================================
# AUTOMATION SETTINGS
# ============================================================================

# Auto-run strategy at market open
AUTO_RUN = os.getenv("AUTO_RUN", "false").lower() == "true"

# Run in test mode (uses sample data)
TEST_MODE = os.getenv("TEST_MODE", "true").lower() == "true"

# ============================================================================
# LOGGING SETTINGS
# ============================================================================

# Log level: "DEBUG", "INFO", "WARNING", "ERROR"
LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO")

# Log file path
LOG_FILE = os.getenv("LOG_FILE", "strategy.log")

# ============================================================================
# VALIDATION
# ============================================================================

def validate_config():
    """Validate configuration settings"""
    errors = []
    
    if POINTS_SPACING <= 0:
        errors.append("POINTS_SPACING must be greater than 0")
    
    if MAX_ORDERS_PER_SIDE <= 0 or MAX_ORDERS_PER_SIDE > 10:
        errors.append("MAX_ORDERS_PER_SIDE must be between 1 and 10")
    
    if STOP_LOSS_POINTS <= 0:
        errors.append("STOP_LOSS_POINTS must be greater than 0")
    
    if TAKE_PROFIT_POINTS <= 0:
        errors.append("TAKE_PROFIT_POINTS must be greater than 0")
    
    if QUANTITY_PER_ORDER <= 0:
        errors.append("QUANTITY_PER_ORDER must be greater than 0")
    
    if ORDER_TYPE not in ["limit", "market", "stop"]:
        errors.append("ORDER_TYPE must be 'limit', 'market', or 'stop'")
    
    if errors:
        raise ValueError(f"Configuration errors:\n" + "\n".join(f"  - {e}" for e in errors))
    
    return True


if __name__ == "__main__":
    print("\n" + "=" * 70)
    print("STRATEGY CONFIGURATION")
    print("=" * 70)
    print(f"Instrument: {INSTRUMENT}")
    print(f"Alternative: {ALTERNATIVE_INSTRUMENT}")
    print(f"Account: {ACCOUNT_NAME}")
    print(f"Market Open: {MARKET_OPEN_HOUR}:{MARKET_OPEN_MINUTE:02d} ET")
    print(f"First Hour Duration: {FIRST_HOUR_DURATION_MINUTES} minutes")
    print(f"Points Spacing: {POINTS_SPACING}")
    print(f"Max Orders/Side: {MAX_ORDERS_PER_SIDE}")
    print(f"Stop Loss: {STOP_LOSS_POINTS} points")
    print(f"Take Profit: {TAKE_PROFIT_POINTS} points")
    print(f"Quantity: {QUANTITY_PER_ORDER} contract(s)")
    print(f"Order Type: {ORDER_TYPE}")
    print(f"Strategy Name: {STRATEGY_NAME}")
    print(f"Data Provider: {DATA_PROVIDER}")
    print(f"Test Mode: {TEST_MODE}")
    print("=" * 70)
    
    try:
        validate_config()
        print("\n✅ Configuration is valid!")
    except ValueError as e:
        print(f"\n❌ Configuration errors:\n{e}")
