/**
 * Price WebSocket Service
 * Connects to the local Node.js price-service to receive live Redis pub/sub streams.
 */

class PriceWebSocketService {
  constructor() {
    this.ws = null;
    this.isConnected = false;
    this.subscriptions = new Map();
    this.reconnectTimeout = null;
    this.reconnectAttempts = 0;
    this.maxReconnectAttempts = 5;
    this.messageHandlers = new Set();
    this.baseUrl = import.meta.env.VITE_PRICE_WS_URL || 'ws://localhost:4000';
  }

  async connect() {
    if (this.ws && this.ws.readyState === WebSocket.OPEN) {
      console.log('Price WebSocket already connected');
      return;
    }

    return new Promise((resolve, reject) => {
      try {
        this.ws = new WebSocket(this.baseUrl);
        
        this.ws.onopen = () => {
          console.log('✅ Price WebSocket connected to Node service');
          this.isConnected = true;
          this.reconnectAttempts = 0;
          resolve();
        };

        this.ws.onmessage = (event) => {
          try {
            const data = JSON.parse(event.data);
            if (data.type === 'price_update') {
              this.handlePriceUpdate(data);
            }
          } catch (error) {
            console.error('Error parsing WebSocket message:', error);
          }
        };

        this.ws.onerror = (error) => {
          console.error('❌ Price WebSocket error:', error);
          reject(error);
        };

        this.ws.onclose = () => {
          console.log('🔌 Price WebSocket closed');
          this.isConnected = false;
          
          if (this.reconnectAttempts < this.maxReconnectAttempts) {
            this.reconnectAttempts++;
            console.log(`🔄 Reconnecting... Attempt ${this.reconnectAttempts}`);
            this.reconnectTimeout = setTimeout(() => {
              this.connect();
            }, 5000);
          }
        };
      } catch (error) {
        console.error('Failed to create WebSocket:', error);
        reject(error);
      }
    });
  }

  handlePriceUpdate(payload) {
    const { symbol, data } = payload;
    
    // Notify general message handlers (e.g. for hooks)
    for (const handler of this.messageHandlers) {
      handler(symbol, data);
    }
    
    // Notify specific candlestick subscriptions (for TradingView / LightweightCharts)
    for (const [subKey, sub] of this.subscriptions.entries()) {
      // Allow flexible symbol matching (e.g., matching 'MNQ' instead of 'MNQZ5')
      if (sub.symbol === symbol || sub.symbol.startsWith(symbol) || symbol.startsWith(sub.symbol)) {
        if (sub.callback) {
          // Wrap into array of candles since the old Tradovate WS provided an array
          const candle = {
            time: data.time || Date.now() / 1000,
            open: data.open || data.price,
            high: data.high || data.price,
            low: data.low || data.price,
            close: data.close || data.price,
            volume: data.volume || 0,
            price: data.price
          };
          sub.callback([candle]);
        }
      }
    }
  }

  subscribeToCandles(symbol, timeframe, callback) {
    const subscriptionKey = `${symbol}_${timeframe}`;
    
    if (this.subscriptions.has(subscriptionKey)) {
      console.log(`Already subscribed to ${subscriptionKey}`);
      // Update callback just in case
      this.subscriptions.get(subscriptionKey).callback = callback;
      return;
    }

    this.subscriptions.set(subscriptionKey, {
      symbol,
      timeframe,
      callback
    });
    console.log(`📊 Subscribed to ${symbol} internally via PriceWebSocket wrapper`);
  }

  unsubscribeFromCandles(symbol, timeframe) {
    const subscriptionKey = `${symbol}_${timeframe}`;
    if (this.subscriptions.has(subscriptionKey)) {
      this.subscriptions.delete(subscriptionKey);
      console.log(`🚫 Unsubscribed from ${subscriptionKey}`);
    }
  }

  addMessageHandler(handler) {
    this.messageHandlers.add(handler);
    return () => this.messageHandlers.delete(handler);
  }

  disconnect() {
    if (this.reconnectTimeout) {
      clearTimeout(this.reconnectTimeout);
      this.reconnectTimeout = null;
    }
    
    this.subscriptions.clear();
    this.messageHandlers.clear();
    
    if (this.ws) {
      this.ws.close();
      this.ws = null;
    }
    
    this.isConnected = false;
    console.log('🔌 Price WebSocket disconnected manually');
  }
}

export const priceWebSocket = new PriceWebSocketService();
export const tradovateWebSocket = priceWebSocket; // Alias to prevent breakage in un-migrated code
