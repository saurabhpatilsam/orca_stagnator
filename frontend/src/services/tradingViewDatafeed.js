/**
 * Custom datafeed service for TradingView Charting Library.
 * Implements IBasicDatafeed interface to provide tick data from the backend.
 */

import { backtestApiService } from './backtestApiService';
import { priceWebSocket } from './priceWebSocket';

class TradingViewDatafeed {
  constructor() {
    this.supportedResolutions = ['1T', '10T', '100T', '1000T', '1', '5', '15', '30', '60', '240', '1D'];
    this.subscriptions = new Map(); // Store active subscriptions
    this.lastBarTimes = new Map(); // Store last bar time per symbol|resolution
  }

  /**
   * Called by the charting library when it needs datafeed configuration.
   * @param {Function} callback - Callback to provide configuration
   */
  onReady(callback) {
    setTimeout(() => {
      callback({
        supported_resolutions: this.supportedResolutions,
        supports_marks: false,
        supports_timescale_marks: false,
        supports_time: true,
        enabled_features: ['tick_resolution'],
        exchanges: [
          { value: 'CME', name: 'CME', desc: 'Chicago Mercantile Exchange' }
        ],
        symbols_types: [
          { name: 'Futures', value: 'futures' }
        ]
      });
    }, 0);
  }

  /**
   * Resolve symbol information.
   * @param {string} symbolName - Symbol to resolve
   * @param {Function} onResolve - Success callback
   * @param {Function} onError - Error callback
   */
  resolveSymbol(symbolName, onResolve, onError) {
    // Map instrument names to symbol info
    const symbolInfo = {
      NQ: {
        name: 'NQ',
        ticker: 'NQ',
        description: 'E-mini Nasdaq-100',
        type: 'futures',
        session: '24x7',
        timezone: 'America/Chicago',
        exchange: 'CME',
        minmov: 1,
        pricescale: 4, // For 0.25 tick size (1/4 = 0.25)
        has_intraday: true,
        has_ticks: true,
        supported_resolutions: this.supportedResolutions,
        volume_precision: 0,
        data_status: 'streaming'
      },
      ES: {
        name: 'ES',
        ticker: 'ES',
        description: 'E-mini S&P 500',
        type: 'futures',
        session: '24x7',
        timezone: 'America/Chicago',
        exchange: 'CME',
        minmov: 1,
        pricescale: 4, // For 0.25 tick size (1/4 = 0.25)
        has_intraday: true,
        has_ticks: true,
        supported_resolutions: this.supportedResolutions,
        volume_precision: 0,
        data_status: 'streaming'
      },
      MNQ: {
        name: 'MNQ',
        ticker: 'MNQ',
        description: 'Micro E-mini Nasdaq-100',
        type: 'futures',
        session: '24x7',
        timezone: 'America/Chicago',
        exchange: 'CME',
        minmov: 1,
        pricescale: 100,
        has_intraday: true,
        has_ticks: true,
        supported_resolutions: this.supportedResolutions,
        volume_precision: 0,
        data_status: 'streaming'
      },
      MES: {
        name: 'MES',
        ticker: 'MES',
        description: 'Micro E-mini S&P 500',
        type: 'futures',
        session: '24x7',
        timezone: 'America/Chicago',
        exchange: 'CME',
        minmov: 1,
        pricescale: 100,
        has_intraday: true,
        has_ticks: true,
        supported_resolutions: this.supportedResolutions,
        volume_precision: 0,
        data_status: 'streaming'
      }
    };

    const symbol = symbolInfo[symbolName.toUpperCase()];
    
    if (symbol) {
      setTimeout(() => onResolve(symbol), 0);
    } else {
      onError('Symbol not found');
    }
  }

  /**
   * Fetch historical tick data from backend API.
   * @param {Object} symbolInfo - Symbol information
   * @param {string} resolution - Bar resolution
   * @param {Object} periodParams - Period parameters with from/to timestamps
   * @param {Function} onResult - Callback for bar data
   * @param {Function} onError - Error callback
   */
  async getBars(symbolInfo, resolution, periodParams, onResult, onError) {
    try {
      // Convert timestamps from seconds to ISO format
      const dateFrom = new Date(periodParams.from * 1000).toISOString();
      const dateTo = new Date(periodParams.to * 1000).toISOString();

      // Fetch tick data from backend
      const response = await backtestApiService.getTickData({
        instrument: symbolInfo.name,
        dateFrom,
        dateTo,
        resolution
      });

      // Ensure bars are sorted in ascending order and normalize times to numbers
      const bars = (response.bars || []).map(bar => ({
        ...bar,
        time: Number(bar.time)
      }));
      bars.sort((a, b) => a.time - b.time);

      // Store the latest bar time for this symbol/resolution combination
      if (bars.length > 0) {
        const key = `${symbolInfo.name}|${resolution}`;
        const lastBar = bars[bars.length - 1];
        this.lastBarTimes.set(key, lastBar.time);
      }

      // Call onResult with bars and metadata
      onResult(bars, { noData: bars.length === 0 });
      
    } catch (error) {
      console.error('Error fetching bars:', error);
      onError(error.message || 'Failed to fetch data');
    }
  }

  /**
   * Subscribe to real-time data updates.
   * @param {Object} symbolInfo - Symbol information
   * @param {string} resolution - Bar resolution
   * @param {Function} onTick - Callback for new bars
   * @param {string} listenerGuid - Unique subscription ID
   * @param {Function} onResetCacheNeededCallback - Cache reset callback
   */
  subscribeBars(symbolInfo, resolution, onTick, listenerGuid, onResetCacheNeededCallback) {
    console.log(`Subscribing to ${symbolInfo.name} with resolution ${resolution}`);
    
    // Get last bar time from history load
    const key = `${symbolInfo.name}|${resolution}`;
    const lastBarTime = this.lastBarTimes.get(key) || null;
    
    // Store subscription info
    const subscription = {
      symbolInfo,
      resolution,
      onTick,
      lastBarTime,
      accumulatedVolume: 0,
      currentBar: null
    };
    
    // Attempt to use WebSocket if available, fallback to polling
    if (priceWebSocket && priceWebSocket.isConnected) {
      // Map symbols to Tradovate symbols
      const symbolMapping = {
        'NQ': 'NQZ5',
        'ES': 'ESZ5',
        'MNQ': 'MNQZ5',
        'MES': 'MESZ5'
      };
      
      const tradovateSymbol = symbolMapping[symbolInfo.name] || symbolInfo.name;
      
      // Convert resolution to minutes
      let intervalMinutes = 5; // default
      if (resolution.endsWith('T')) {
        // Tick resolutions - use 1 minute updates
        intervalMinutes = 1;
      } else if (!isNaN(resolution)) {
        intervalMinutes = parseInt(resolution);
      }
      
      // Subscribe via WebSocket
      priceWebSocket.subscribeToCandles(tradovateSymbol, intervalMinutes, (candles) => {
        if (candles && candles.length > 0) {
          candles.forEach(candle => {
            const bar = {
              time: candle.time * 1000, // Convert to milliseconds
              open: candle.open,
              high: candle.high,
              low: candle.low,
              close: candle.close,
              volume: candle.volume || 0
            };
            
            // Only send if newer than last bar
            if (!subscription.lastBarTime || bar.time > subscription.lastBarTime) {
              onTick(bar);
              subscription.lastBarTime = bar.time;
            }
          });
        }
      });
      
      subscription.useWebSocket = true;
      subscription.tradovateSymbol = tradovateSymbol;
      subscription.intervalMinutes = intervalMinutes;
    } else {
      // Fallback to polling approach
      const intervalId = setInterval(async () => {
        try {
          const now = new Date();
          const from = subscription.lastBarTime 
            ? new Date(subscription.lastBarTime)
            : new Date(now.getTime() - 60000); // Default to 1 minute ago
          
          const response = await backtestApiService.getTickData({
            instrument: symbolInfo.name,
            dateFrom: from.toISOString(),
            dateTo: now.toISOString(),
            resolution
          });
          
          if (response.bars && response.bars.length > 0) {
            response.bars.forEach(bar => {
              // De-duplicate: only send bars newer than last seen
              if (!subscription.lastBarTime || bar.time > subscription.lastBarTime) {
                onTick(bar);
                subscription.lastBarTime = bar.time;
              }
            });
          }
        } catch (error) {
          console.error('Error fetching real-time data:', error);
        }
      }, 5000); // Poll every 5 seconds
      
      subscription.intervalId = intervalId;
    }
    
    this.subscriptions.set(listenerGuid, subscription);
  }

  /**
   * Unsubscribe from real-time data.
   * @param {string} listenerGuid - Subscription ID to remove
   */
  unsubscribeBars(listenerGuid) {
    console.log(`Unsubscribing ${listenerGuid}`);
    
    const subscription = this.subscriptions.get(listenerGuid);
    if (subscription) {
      if (subscription.intervalId) {
        clearInterval(subscription.intervalId);
      }
      
      // Unsubscribe from WebSocket if using it
      if (subscription.useWebSocket && priceWebSocket) {
        priceWebSocket.unsubscribeFromCandles(
          subscription.tradovateSymbol, 
          subscription.intervalMinutes
        );
      }
    }
    
    this.subscriptions.delete(listenerGuid);
  }
}

// Export singleton instance
export default new TradingViewDatafeed();
