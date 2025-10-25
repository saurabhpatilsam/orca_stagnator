import React, { useState, useEffect } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { 
  TrendingUp, 
  TrendingDown,
  Activity,
  DollarSign,
  Clock,
  RefreshCw,
  AlertCircle
} from 'lucide-react';
import { apiClient } from '../config/api';

const PriceStreaming = ({ instruments }) => {
  const [prices, setPrices] = useState({});
  const [loading, setLoading] = useState(true);
  const [connected, setConnected] = useState(false);
  const [lastUpdate, setLastUpdate] = useState(null);
  const [marketStatus, setMarketStatus] = useState('closed');

  useEffect(() => {
    // Initialize prices with instruments
    const initialPrices = {};
    instruments.forEach(inst => {
      initialPrices[inst.symbol] = {
        bid: 0,
        ask: 0,
        last: 0,
        change: 0,
        changePercent: 0,
        volume: 0,
        high: 0,
        low: 0,
        open: 0,
        timestamp: null
      };
    });
    setPrices(initialPrices);
    
    // Start price streaming
    connectToPriceStream();
    
    return () => {
      disconnectPriceStream();
    };
  }, []);

  const connectToPriceStream = async () => {
    try {
      setLoading(true);
      
      // Connect to backend WebSocket or polling endpoint
      const streamUrl = import.meta.env.VITE_API_URL || 'https://orca-backend-api-production.up.railway.app';
      
      // For now, simulate with polling
      const pollPrices = async () => {
        try {
          const response = await fetch(`${streamUrl}/api/prices/live`, {
            headers: {
              'Authorization': `Bearer ${localStorage.getItem('orca-auth-token')}`
            }
          });
          
          if (response.ok) {
            const data = await response.json();
            setMarketStatus(data.market_status || 'closed');
            
            if (data.prices) {
              updatePrices(data.prices);
            }
            setConnected(true);
          }
        } catch (error) {
          console.error('Price fetch error:', error);
          // Do NOT simulate prices - just show connection error
          setConnected(false);
        }
      };

      // Poll every second for real-time feel
      pollPrices();
      const interval = setInterval(pollPrices, 1000);
      
      // Store interval ID for cleanup
      window.priceStreamInterval = interval;
      
      setLoading(false);
      setConnected(true);
    } catch (error) {
      console.error('Failed to connect to price stream:', error);
      setLoading(false);
      setConnected(false);
    }
  };

  const disconnectPriceStream = () => {
    if (window.priceStreamInterval) {
      clearInterval(window.priceStreamInterval);
    }
    setConnected(false);
  };

  // Removed simulatePrices function - no simulated data allowed

  const updatePrices = (data) => {
    setPrices(prevPrices => ({
      ...prevPrices,
      ...data
    }));
    setLastUpdate(new Date());
  };

  const formatPrice = (price, symbol) => {
    if (!price) return '0.00';
    const decimals = ['GC', 'MGC'].includes(symbol) ? 2 : 2;
    return price.toFixed(decimals);
  };

  const formatNumber = (num) => {
    if (!num) return '0';
    return new Intl.NumberFormat('en-US').format(num);
  };

  const PriceCard = ({ symbol, data, instrument }) => {
    const isPositive = data.change >= 0;
    
    return (
      <motion.div
        layout
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        className="bg-gray-950 border border-gray-900 rounded-lg p-6 hover:border-gray-800 transition-all"
      >
        {/* Header */}
        <div className="flex items-start justify-between mb-4">
          <div>
            <h3 className="text-white text-lg font-bold">{symbol}</h3>
            <p className="text-gray-500 text-xs">{instrument.name}</p>
            <p className="text-gray-600 text-xs">{instrument.exchange}</p>
          </div>
          <div className={`flex items-center space-x-1 ${isPositive ? 'text-green-500' : 'text-red-500'}`}>
            {isPositive ? <TrendingUp className="w-4 h-4" /> : <TrendingDown className="w-4 h-4" />}
            <span className="text-sm font-medium">
              {isPositive ? '+' : ''}{data.changePercent?.toFixed(2) || '0.00'}%
            </span>
          </div>
        </div>

        {/* Price Display */}
        <div className="mb-4">
          <div className="text-3xl font-mono font-bold text-white mb-1">
            {formatPrice(data.last, symbol)}
          </div>
          <div className={`text-sm font-mono ${isPositive ? 'text-green-500' : 'text-red-500'}`}>
            {isPositive ? '+' : ''}{formatPrice(data.change, symbol)}
          </div>
        </div>

        {/* Bid/Ask Spread */}
        <div className="grid grid-cols-2 gap-4 mb-4">
          <div>
            <p className="text-gray-600 text-xs mb-1">BID</p>
            <p className="text-white font-mono text-sm">{formatPrice(data.bid, symbol)}</p>
          </div>
          <div>
            <p className="text-gray-600 text-xs mb-1">ASK</p>
            <p className="text-white font-mono text-sm">{formatPrice(data.ask, symbol)}</p>
          </div>
        </div>

        {/* Additional Data */}
        <div className="grid grid-cols-3 gap-2 pt-4 border-t border-gray-900">
          <div>
            <p className="text-gray-600 text-xs">HIGH</p>
            <p className="text-gray-400 text-xs font-mono">{formatPrice(data.high, symbol)}</p>
          </div>
          <div>
            <p className="text-gray-600 text-xs">LOW</p>
            <p className="text-gray-400 text-xs font-mono">{formatPrice(data.low, symbol)}</p>
          </div>
          <div>
            <p className="text-gray-600 text-xs">VOL</p>
            <p className="text-gray-400 text-xs font-mono">{formatNumber(data.volume)}</p>
          </div>
        </div>

        {/* Update Indicator */}
        <motion.div
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          key={data.timestamp}
          className="mt-4 flex items-center justify-center"
        >
          <div className="w-1 h-1 bg-green-500 rounded-full animate-ping" />
        </motion.div>
      </motion.div>
    );
  };

  return (
    <div className="p-6">
      {/* Header */}
      <div className="mb-6">
        <div className="flex items-center justify-between">
          <div>
            <h2 className="text-2xl font-bold text-white">Live Market Prices</h2>
            <p className="text-gray-500 text-sm mt-1">Real-time streaming from Tradovate</p>
          </div>
          <div className="flex items-center space-x-4">
            {/* Connection Status */}
            <div className="flex items-center space-x-2">
              <div className={`w-2 h-2 rounded-full ${connected ? 'bg-green-500' : 'bg-red-500'} animate-pulse`} />
              <span className="text-gray-400 text-sm">
                {connected ? 'Connected' : 'Disconnected'}
              </span>
            </div>
            
            {/* Last Update */}
            {lastUpdate && (
              <div className="flex items-center space-x-2 text-gray-500 text-sm">
                <Clock className="w-3 h-3" />
                <span>{lastUpdate.toLocaleTimeString()}</span>
              </div>
            )}

            {/* Refresh Button */}
            <button
              onClick={connectToPriceStream}
              className="p-2 bg-gray-900 hover:bg-gray-800 rounded-lg text-gray-400 hover:text-white transition-colors"
            >
              <RefreshCw className="w-4 h-4" />
            </button>
          </div>
        </div>
      </div>

      {/* Loading State */}
      {loading && (
        <div className="flex items-center justify-center py-20">
          <div className="text-center">
            <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-white mx-auto mb-4" />
            <p className="text-gray-400">Connecting to market data...</p>
          </div>
        </div>
      )}

      {/* Price Cards Grid */}
      {!loading && (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
          <AnimatePresence mode="popLayout">
            {instruments.map(inst => (
              <PriceCard
                key={inst.symbol}
                symbol={inst.symbol}
                data={prices[inst.symbol] || {}}
                instrument={inst}
              />
            ))}
          </AnimatePresence>
        </div>
      )}

      {/* Market Status */}
      <div className="mt-8 p-4 bg-gray-950 border border-gray-900 rounded-lg">
        <div className="flex items-center justify-between">
          <div className="flex items-center space-x-3">
            <Activity className="w-5 h-5 text-gray-400" />
            <div>
              <p className="text-white text-sm font-medium">Market Status</p>
              <p className="text-gray-500 text-xs">US Futures Market</p>
            </div>
          </div>
          <div className="text-right">
            <p className={`text-sm font-medium ${marketStatus === 'open' ? 'text-green-500' : 'text-red-500'}`}>
              {marketStatus === 'open' ? 'OPEN' : 'CLOSED'}
            </p>
            <p className="text-gray-600 text-xs">
              {marketStatus === 'open' 
                ? 'Trading Hours: Sun 6PM - Fri 5PM ET' 
                : 'Markets closed on weekends'}
            </p>
          </div>
        </div>
      </div>

      {/* Risk Warning */}
      <div className="mt-4 p-4 bg-yellow-950/20 border border-yellow-900/50 rounded-lg">
        <div className="flex items-start space-x-3">
          <AlertCircle className="w-5 h-5 text-yellow-500 mt-0.5" />
          <div className="flex-1">
            <p className="text-yellow-400 text-sm font-medium">Risk Disclaimer</p>
            <p className="text-gray-400 text-xs mt-1">
              Futures trading involves substantial risk of loss and is not suitable for all investors.
              Past performance is not indicative of future results.
            </p>
          </div>
        </div>
      </div>
    </div>
  );
};

export default PriceStreaming;
