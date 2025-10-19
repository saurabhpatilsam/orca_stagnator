# 📊 OHLC Data API Research - Tradovate & TradingView

**Research Date:** October 15, 2025  
**Objective:** Find APIs to fetch 30-minute OHLC candle data for NQ futures

---

## 🔍 Research Summary

| API | Historical OHLC | Authentication | Status |
|-----|----------------|----------------|---------|
| **Tradovate /chart/bars** | ✅ Yes | JWT Token (have) | ⚠️ 404 Error |
| **Tradovate /quotes** | ❌ Session only | JWT Token (have) | ✅ Working |
| **TradingView Scanner** | ❌ Current only | None | ⚠️ Limited |
| **TradingView TA Library** | ❌ Current only | None | ⚠️ Limited |
| **TradingView Webhooks** | ❌ Signals only | Premium | ⚠️ One-way |

---

## 1️⃣ Tradovate API Options

### Option A: `/chart/bars` Endpoint (RECOMMENDED BUT 404)

**Endpoint:**
```
GET /chart/bars?symbol={symbol}&chartDescription={json}&locale=en
```

**Chart Description Format:**
```json
{
  "underlyingType": "MinuteBar",
  "elementSize": 30,
  "withHistogram": true
}
```

**Expected Response:**
```json
{
  "s": "ok",
  "d": [
    {
      "t": "2025-10-15T15:00:00.000Z",
      "o": 25000.00,
      "h": 25050.00,
      "l": 24980.00,
      "c": 25030.00,
      "v": 15000
    }
  ]
}
```

**Status:** ⚠️ **Returns 404 Error**

**Possible Reasons:**
1. Endpoint not available in demo environment (`tv-demo.tradovateapi.com`)
2. Endpoint path different (might be `/md/getchart` or `/chart/query`)
3. Requires different authentication
4. Only available in production environment (`live.tradovateapi.com`)

**Documentation Reference:**
- Found in `docs/guides/TRADOVATE_DATA_INTEGRATION.md`
- Used successfully in `automated_trading_daemon.py` for 60-min bars

**Action Items:**
- ✅ Try with production URL (if you have live account)
- ✅ Check Tradovate official API docs for correct endpoint
- ✅ Test with different chart description formats
- ✅ Contact Tradovate support for demo environment capabilities

---

### Option B: `/quotes` Endpoint (WORKING)

**Endpoint:**
```
GET /quotes?locale=en&symbols={symbol}
```

**Response Data:**
```json
{
  "s": "ok",
  "d": [{
    "s": "ok",
    "n": "MNQZ5",
    "v": {
      "lp": 25093.00,      // Last price
      "bid": 25092.75,     // Bid
      "ask": 25093.25,     // Ask
      "open_price": 24752.50,    // Session open
      "high_price": 25117.75,    // Session high
      "low_price": 24740.50,     // Session low
      "volume": 916425     // Session volume
    }
  }]
}
```

**Status:** ✅ **WORKING**

**Limitations:**
- ❌ Returns SESSION-LEVEL data only (entire trading day)
- ❌ Does NOT return individual 30-minute candles
- ✅ Good for current price and session OHLC

**Use Case:** Real-time price monitoring, session statistics

---

## 2️⃣ TradingView API Options

### Option A: Scanner API

**Endpoint:**
```
POST https://scanner.tradingview.com/futures/scan
```

**Payload:**
```json
{
  "symbols": {
    "tickers": ["CME:NQ1!"],
    "query": {"types": []}
  },
  "columns": ["name", "close", "open", "high", "low", "volume"]
}
```

**Status:** ⚠️ **Limited Data**

**Response:** Current session data only (no historical bars)

**Limitations:**
- ❌ No historical OHLC candles
- ❌ Current bar/session data only
- ❌ Unofficial endpoint (may change)
- ✅ No authentication required

---

### Option B: tradingview-ta Library

**Installation:**
```bash
pip install tradingview-ta
```

**Usage:**
```python
from tradingview_ta import TA_Handler, Interval

handler = TA_Handler(
    symbol="NQ1!",
    exchange="CME",
    screener="america",
    interval=Interval.INTERVAL_30_MINUTES
)

analysis = handler.get_analysis()
indicators = analysis.indicators

# Get current bar OHLC
open_price = indicators['open']
high_price = indicators['high']
low_price = indicators['low']
close_price = indicators['close']
```

**Status:** ✅ **Easy to Use**

**Limitations:**
- ❌ Current bar only (no historical candles)
- ❌ Cannot fetch last N bars
- ✅ Includes technical indicators (RSI, MACD, etc.)
- ✅ Good for current market analysis

---

### Option C: TradingView Webhooks

**Setup:**
1. Create alert in TradingView
2. Set webhook URL to your backend
3. Receive signals when alert triggers

**Webhook URL:**
```
POST https://your-backend.com/webhook/tradingview
```

**Payload:**
```json
{
  "symbol": "{{ticker}}",
  "interval": "{{interval}}",
  "close": {{close}},
  "open": {{open}},
  "high": {{high}},
  "low": {{low}},
  "volume": {{volume}},
  "time": "{{time}}"
}
```

**Status:** ✅ **Works for Signals**

**Limitations:**
- ❌ Requires TradingView Premium ($14.95+/month)
- ❌ One-way communication only (alerts → your server)
- ❌ Cannot query historical data
- ✅ Real-time alerts when conditions met

**Use Case:** Trigger trades based on TradingView strategy signals

---

## 3️⃣ Alternative Solutions

### ✅ Option 1: Aggregate Supabase Tick Data (BEST)

**Status:** ✅ **RECOMMENDED**

**Pros:**
- ✅ You already have tick data stored
- ✅ Zero additional cost
- ✅ Full control over aggregation
- ✅ Can create any timeframe (1min, 5min, 30min, etc.)

**Implementation:**

**SQL Function:**
```sql
CREATE OR REPLACE FUNCTION get_30min_ohlc(
    start_time TIMESTAMP,
    end_time TIMESTAMP
)
RETURNS TABLE (
    candle_time TIMESTAMP,
    open DECIMAL,
    high DECIMAL,
    low DECIMAL,
    close DECIMAL,
    volume BIGINT
) AS $$
BEGIN
    RETURN QUERY
    SELECT 
        date_trunc('30 minutes', time) as candle_time,
        FIRST(last ORDER BY time) as open,
        MAX(last) as high,
        MIN(last) as low,
        LAST(last ORDER BY time) as close,
        SUM(volume) as volume
    FROM orca.nq_tick_data
    WHERE time >= start_time AND time < end_time
    GROUP BY date_trunc('30 minutes', time)
    ORDER BY candle_time;
END;
$$ LANGUAGE plpgsql;
```

**Python Usage:**
```python
from supabase import create_client

supabase = create_client(url, key)

# Get last 5 30-minute candles
result = supabase.rpc('get_30min_ohlc', {
    'start_time': '2025-10-15 14:00:00',
    'end_time': '2025-10-15 16:30:00'
}).execute()

candles = result.data
```

**Action:** Create SQL function in Supabase and Python wrapper

---

### ✅ Option 2: Polygon.io API

**Status:** ✅ **Reliable Third-Party**

**Endpoint:**
```
GET https://api.polygon.io/v2/aggs/ticker/{ticker}/range/{multiplier}/{timespan}/{from}/{to}
```

**Example:**
```
GET https://api.polygon.io/v2/aggs/ticker/NQ/range/30/minute/2025-10-15/2025-10-15?apiKey=YOUR_KEY
```

**Response:**
```json
{
  "results": [
    {
      "t": 1697385000000,
      "o": 25000.00,
      "h": 25050.00,
      "l": 24980.00,
      "c": 25030.00,
      "v": 15000
    }
  ]
}
```

**Pricing:**
- Free: 5 calls/minute
- Starter: $99/month (100 calls/minute)
- Developer: $299/month (unlimited)

**Signup:** https://polygon.io/

---

### ✅ Option 3: Alpha Vantage API

**Status:** ⚠️ **Limited Futures Support**

**Endpoint:**
```
GET https://www.alphavantage.co/query?function=TIME_SERIES_INTRADAY&symbol=NQ&interval=30min&apikey=YOUR_KEY
```

**Limitations:**
- ⚠️ Better for stocks than futures
- ⚠️ Limited futures coverage
- ✅ Free tier: 5 calls/minute, 500/day

**Signup:** https://www.alphavantage.co/

---

## 4️⃣ Recommendations

### 🎯 **BEST SOLUTION: Supabase Tick Data Aggregation**

**Why:**
1. ✅ You already have the raw tick data
2. ✅ Zero additional cost
3. ✅ Full control and customization
4. ✅ No API rate limits
5. ✅ Can create any timeframe you need

**Steps:**
1. Create SQL function in Supabase (see above)
2. Grant proper permissions
3. Create Python wrapper function
4. Test with recent data
5. Use in your trading system

---

### 🔄 **BACKUP SOLUTION: Polygon.io**

**Why:**
- ✅ Clean REST API
- ✅ Reliable data source
- ✅ Good documentation
- ⚠️ Costs money after free tier

**Use When:**
- Supabase tick data is incomplete
- Need data from dates before you started collecting
- Need additional markets/instruments

---

### ⚠️ **AVOID: TradingView for Historical Data**

**Reason:**
- ❌ No public API for historical OHLC
- ❌ Only useful for real-time signals (webhooks)
- ❌ Cannot query past candles programmatically

**Use TradingView For:**
- Strategy alerts → webhook → your system
- Chart visualization
- Technical analysis indicators

---

## 5️⃣ Action Plan

### Immediate (Today):

1. **✅ Fix Supabase Schema Access**
   ```sql
   -- Create view in public schema
   CREATE VIEW public.nq_tick_data AS 
   SELECT * FROM orca.nq_tick_data;
   
   GRANT SELECT ON public.nq_tick_data TO anon, authenticated;
   ```

2. **✅ Create OHLC Aggregation Function**
   ```sql
   -- Add function from Option 1 above
   ```

3. **✅ Test with Recent Data**
   ```python
   python3 get_nq_30min_from_supabase.py
   ```

### Short-term (This Week):

4. **⚠️ Investigate Tradovate Chart/Bars Endpoint**
   - Try production URL if you have live account
   - Check official Tradovate API documentation
   - Contact Tradovate support

5. **✅ Sign up for Polygon.io Free Tier**
   - Backup data source
   - Test API integration
   - Evaluate if paid tier is needed

### Long-term (Optional):

6. **⚠️ Set up TradingView Webhooks**
   - For real-time strategy signals
   - Requires TradingView Premium
   - Integrate with your order placement system

---

## 6️⃣ Scripts Created

| Script | Purpose | Status |
|--------|---------|--------|
| `get_nq_realtime.py` | Current NQ price from Tradovate | ✅ Working |
| `get_nq_30min_tradovate.py` | 30-min bars from Tradovate | ⚠️ 404 Error |
| `get_nq_30min_tradingview.py` | TradingView data test | ⚠️ Limited |
| `get_nq_30min_from_supabase.py` | (To create) Aggregate tick data | 🔨 Next Step |

---

## 📞 Support Contacts

**Tradovate Support:**
- Website: https://www.tradovate.com/support/
- Email: support@tradovate.com
- Ask about: Chart/bars endpoint availability in demo environment

**Polygon.io Support:**
- Website: https://polygon.io/docs
- Dashboard: https://polygon.io/dashboard

---

**Last Updated:** October 15, 2025 at 16:00  
**Status:** Research complete, ready for implementation
