// TradingView API Service for real-time price data
class TradingViewService {
  constructor() {
    this.symbols = {
      'MNQ': 'CME_MINI:MNQZ2024', // Micro E-mini Nasdaq-100 December 2024
      'NQ': 'CME_MINI:NQZ2024',   // E-mini Nasdaq-100 December 2024
      'ES': 'CME_MINI:ESZ2024',   // E-mini S&P 500 December 2024
      'MES': 'CME_MINI:MESZ2024', // Micro E-mini S&P 500 December 2024
      'GC': 'COMEX:GCZ2024',      // Gold Futures December 2024
      'MGC': 'COMEX:MGCZ2024'     // Micro Gold Futures December 2024
    };
    
    this.widgets = new Map();
    this.priceCallbacks = new Map();
  }

  // Initialize TradingView widget for a specific container
  initializeWidget(containerId, symbol, callback) {
    // Store callback for price updates
    if (callback) {
      this.priceCallbacks.set(symbol, callback);
    }

    // Create a lightweight widget for price display
    const script = document.createElement('script');
    script.type = 'text/javascript';
    script.src = 'https://s3.tradingview.com/external-embedding/embed-widget-single-quote.js';
    script.async = true;
    script.innerHTML = JSON.stringify({
      symbol: this.symbols[symbol] || symbol,
      width: "100%",
      colorTheme: "dark",
      isTransparent: true,
      locale: "en"
    });

    const container = document.getElementById(containerId);
    if (container) {
      container.appendChild(script);
    }
  }

  // Get mock real-time price data (for development)
  // In production, this would connect to actual TradingView WebSocket
  getMockPriceData(symbol) {
    const basePrices = {
      'MNQ': 20150.25,
      'NQ': 20150.25,
      'ES': 5900.50,
      'MES': 5900.50,
      'GC': 2750.30,
      'MGC': 275.03
    };

    const basePrice = basePrices[symbol] || 100;
    const randomChange = (Math.random() - 0.5) * 10;
    const price = basePrice + randomChange;
    const change = randomChange;
    const changePercent = (randomChange / basePrice) * 100;

    return {
      symbol,
      price: price.toFixed(2),
      change: change.toFixed(2),
      changePercent: changePercent.toFixed(2),
      timestamp: new Date().toISOString(),
      bid: (price - 0.25).toFixed(2),
      ask: (price + 0.25).toFixed(2),
      volume: Math.floor(Math.random() * 10000),
      high: (price + Math.random() * 5).toFixed(2),
      low: (price - Math.random() * 5).toFixed(2),
      open: basePrice.toFixed(2)
    };
  }

  // Simulate real-time price updates
  startPriceUpdates(symbols, onUpdate) {
    const updatePrices = () => {
      const prices = {};
      symbols.forEach(symbol => {
        prices[symbol] = this.getMockPriceData(symbol);
      });
      onUpdate(prices);
    };

    // Initial update
    updatePrices();

    // Update every 1-3 seconds
    return setInterval(updatePrices, Math.random() * 2000 + 1000);
  }

  // Stop price updates
  stopPriceUpdates(intervalId) {
    if (intervalId) {
      clearInterval(intervalId);
    }
  }

  // Get historical data for backtesting
  async getHistoricalData(symbol, from, to, resolution = '30') {
    // This would connect to TradingView's historical data API
    // For now, return mock data
    const data = [];
    const currentDate = new Date(from);
    const endDate = new Date(to);
    
    while (currentDate <= endDate) {
      data.push({
        time: currentDate.toISOString(),
        open: 5900 + Math.random() * 20,
        high: 5920 + Math.random() * 20,
        low: 5880 + Math.random() * 20,
        close: 5900 + Math.random() * 20,
        volume: Math.floor(Math.random() * 10000)
      });
      
      currentDate.setMinutes(currentDate.getMinutes() + parseInt(resolution));
    }
    
    return data;
  }

  // Connect to TradingView WebSocket for real-time data
  connectWebSocket(symbols, onMessage) {
    // In production, this would connect to TradingView's WebSocket
    // For development, we'll simulate with mock data
    console.log('Connecting to TradingView WebSocket for symbols:', symbols);
    
    // Simulate WebSocket connection
    return this.startPriceUpdates(symbols, onMessage);
  }

  // Disconnect WebSocket
  disconnectWebSocket(connection) {
    this.stopPriceUpdates(connection);
  }
}

export default new TradingViewService();
