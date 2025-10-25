BEGIN;

TRUNCATE TABLE orca.nq_candles_1min;
TRUNCATE TABLE orca.nq_candles_5min;
TRUNCATE TABLE orca.nq_candles_10min;
TRUNCATE TABLE orca.nq_candles_15min;
TRUNCATE TABLE orca.nq_candles_30min;
TRUNCATE TABLE orca.nq_candles_1hour;

TRUNCATE TABLE orca.candle_fetch_log;

COMMIT;
