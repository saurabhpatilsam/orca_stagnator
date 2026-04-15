/**
 * TradingView Dashboard Component
 * Professional multi-chart display for real-time market data
 */

import React, { useState, useEffect, useRef } from 'react';
import { motion } from 'framer-motion';
import {
  TrendingUp,
  TrendingDown,
  Activity,
  BarChart3,
  Maximize2,
  Grid,
  Settings,
  RefreshCw,
  Plus,
  X,
  ChevronDown,
  Monitor,
  Layers,
  DollarSign,
  Clock,
  Zap,
  AlertCircle
} from 'lucide-react';
import TradingViewChart from './TradingViewChart';
import { priceWebSocket } from '../services/priceWebSocket';
import { apiClient } from '../config/api';
import toast from 'react-hot-toast';

const TradingViewDashboard = () => {
  // State management
  const [selectedInstruments, setSelectedInstruments] = useState(['NQ', 'ES']);
  const [layout, setLayout] = useState('2x2'); // '1x1', '2x1', '2x2', '3x2'
  const [selectedTimeframe, setSelectedTimeframe] = useState('5');
  const [marketStatus, setMarketStatus] = useState('closed');
  const [livePrice, setLivePrice] = useState({});
  const [wsConnected, setWsConnected] = useState(false);
  const [activeChart, setActiveChart] = useState(null);
  const [theme, setTheme] = useState('dark');
  const [showSettings, setShowSettings] = useState(false);

  // Available instruments with metadata
  const instruments = [
    { 
      symbol: 'NQ', 
      name: 'E-mini Nasdaq-100',
      tradovateSymbol: 'NQZ5',
      color: '#00d4ff',
      tickSize: 0.25,
      pointValue: 20
    },
    { 
      symbol: 'ES', 
      name: 'E-mini S&P 500',
      tradovateSymbol: 'ESZ5',
      color: '#ff6b6b',
      tickSize: 0.25,
      pointValue: 50
    },
    { 
      symbol: 'MNQ', 
      name: 'Micro E-mini Nasdaq',
      tradovateSymbol: 'MNQZ5',
      color: '#4ecdc4',
      tickSize: 0.25,
      pointValue: 2
    },
    { 
      symbol: 'MES', 
      name: 'Micro E-mini S&P',
      tradovateSymbol: 'MESZ5',
      color: '#f7b731',
      tickSize: 0.25,
      pointValue: 5
    },
    { 
      symbol: 'GC', 
      name: 'Gold Futures',
      tradovateSymbol: 'GCZ5',
      color: '#ffd700',
      tickSize: 0.10,
      pointValue: 100
    },
    { 
      symbol: 'CL', 
      name: 'Crude Oil',
      tradovateSymbol: 'CLZ5',
      color: '#95a5a6',
      tickSize: 0.01,
      pointValue: 1000
    }
  ];

  // Timeframe options
  const timeframes = [
    { value: '1T', label: '1 Tick', type: 'tick' },
    { value: '10T', label: '10 Ticks', type: 'tick' },
    { value: '100T', label: '100 Ticks', type: 'tick' },
    { value: '1', label: '1 Min', type: 'time' },
    { value: '5', label: '5 Min', type: 'time' },
    { value: '15', label: '15 Min', type: 'time' },
    { value: '30', label: '30 Min', type: 'time' },
    { value: '60', label: '1 Hour', type: 'time' },
    { value: '240', label: '4 Hours', type: 'time' },
    { value: '1D', label: '1 Day', type: 'time' }
  ];

  // Layout configurations
  const layoutConfigs = {
    '1x1': { rows: 1, cols: 1, maxCharts: 1 },
    '2x1': { rows: 1, cols: 2, maxCharts: 2 },
    '2x2': { rows: 2, cols: 2, maxCharts: 4 },
    '3x2': { rows: 2, cols: 3, maxCharts: 6 }
  };

  // Initialize WebSocket connection for real-time prices
  useEffect(() => {
    // Try to connect to WebSocket, but don't fail if unavailable
    initializeWebSocket().catch(err => {
      console.log('WebSocket not available, charts will work without live updates:', err.message);
    });
    
    checkMarketStatus();
    
    const interval = setInterval(checkMarketStatus, 60000); // Check every minute
    
    return () => {
      clearInterval(interval);
      if (wsConnected) {
        priceWebSocket.disconnect();
      }
    };
  }, []);

  // Initialize WebSocket connected to Redis local price service
  const initializeWebSocket = async () => {
    try {
      await priceWebSocket.connect();
      setWsConnected(true);
      
      // Make WebSocket available globally for TradingView datafeed
      window.tradovateWebSocket = priceWebSocket;
      
      // Subscribe to price updates for selected instruments
      selectedInstruments.forEach(symbol => {
        const instrument = instruments.find(i => i.symbol === symbol);
        if (instrument) {
          subscribeToPrice(instrument);
        }
      });
      
      toast.success('Connected to Redis live market data');
    } catch (error) {
      console.log('Live WebSocket not available, using historical data only:', error.message);
    }
  };

  // Subscribe to real-time price for an instrument
  const subscribeToPrice = (instrument) => {
    if (!wsConnected) return;
    
    priceWebSocket.subscribeToCandles(
      instrument.tradovateSymbol,
      1, // 1-minute for price updates
      (candles) => {
        if (candles && candles.length > 0) {
          const latestCandle = candles[candles.length - 1];
          setLivePrice(prev => ({
            ...prev,
            [instrument.symbol]: {
              price: latestCandle.close,
              change: latestCandle.close - latestCandle.open,
              changePercent: ((latestCandle.close - latestCandle.open) / latestCandle.open) * 100,
              volume: latestCandle.volume,
              timestamp: new Date(latestCandle.time * 1000)
            }
          }));
        }
      }
    );
  };

  // Check market status
  const checkMarketStatus = () => {
    const now = new Date();
    const day = now.getDay();
    const hour = now.getHours();
    
    // Futures market closed: Friday 5PM ET to Sunday 6PM ET
    if (day === 0 || (day === 5 && hour >= 17) || (day === 6)) {
      setMarketStatus('closed');
    } else if (hour >= 9 && hour < 16) {
      setMarketStatus('open');
    } else {
      setMarketStatus('pre-market');
    }
  };

  // Add/Remove instrument
  const toggleInstrument = (symbol) => {
    if (selectedInstruments.includes(symbol)) {
      setSelectedInstruments(prev => prev.filter(s => s !== symbol));
    } else {
      const maxCharts = layoutConfigs[layout].maxCharts;
      if (selectedInstruments.length < maxCharts) {
        setSelectedInstruments(prev => [...prev, symbol]);
        
        // Subscribe to new instrument if WebSocket connected
        if (wsConnected) {
          const instrument = instruments.find(i => i.symbol === symbol);
          if (instrument) {
            subscribeToPrice(instrument);
          }
        }
      } else {
        toast.error(`Maximum ${maxCharts} charts for this layout`);
      }
    }
  };

  // Change layout
  const changeLayout = (newLayout) => {
    setLayout(newLayout);
    const maxCharts = layoutConfigs[newLayout].maxCharts;
    if (selectedInstruments.length > maxCharts) {
      setSelectedInstruments(prev => prev.slice(0, maxCharts));
    }
  };

  // Render chart grid
  const renderChartGrid = () => {
    const config = layoutConfigs[layout];
    const gridClass = `grid grid-cols-${config.cols} gap-4`;
    
    return (
      <div className={gridClass}>
        {selectedInstruments.slice(0, config.maxCharts).map((symbol, index) => {
          const instrument = instruments.find(i => i.symbol === symbol);
          const price = livePrice[symbol];
          
          return (
            <motion.div
              key={`${symbol}-${index}`}
              initial={{ opacity: 0, scale: 0.9 }}
              animate={{ opacity: 1, scale: 1 }}
              transition={{ delay: index * 0.1 }}
              className={`bg-gray-800/50 backdrop-blur-lg border border-gray-700 rounded-xl overflow-hidden
                ${activeChart === symbol ? 'ring-2 ring-purple-500' : ''}`}
              onClick={() => setActiveChart(symbol)}
            >
              {/* Chart Header */}
              <div className="bg-gray-900/50 border-b border-gray-700 p-3">
                <div className="flex items-center justify-between">
                  <div className="flex items-center gap-3">
                    <div 
                      className="w-2 h-2 rounded-full animate-pulse"
                      style={{ backgroundColor: instrument.color }}
                    />
                    <div>
                      <h3 className="text-white font-semibold">{symbol}</h3>
                      <p className="text-xs text-gray-400">{instrument.name}</p>
                    </div>
                  </div>
                  
                  <div className="flex items-center gap-4">
                    {price && (
                      <div className="text-right">
                        <div className="text-white font-mono font-bold">
                          ${price.price?.toFixed(2) || '--'}
                        </div>
                        <div className={`text-xs flex items-center gap-1 ${
                          price.change >= 0 ? 'text-green-400' : 'text-red-400'
                        }`}>
                          {price.change >= 0 ? (
                            <TrendingUp className="h-3 w-3" />
                          ) : (
                            <TrendingDown className="h-3 w-3" />
                          )}
                          {price.changePercent?.toFixed(2)}%
                        </div>
                      </div>
                    )}
                    
                    <button
                      onClick={(e) => {
                        e.stopPropagation();
                        toggleInstrument(symbol);
                      }}
                      className="p-1 hover:bg-gray-700 rounded transition-colors"
                    >
                      <X className="h-4 w-4 text-gray-400" />
                    </button>
                  </div>
                </div>
              </div>
              
              {/* TradingView Chart */}
              <div className="h-96">
                <TradingViewChart
                  symbol={symbol}
                  interval={selectedTimeframe}
                  containerId={`tv_chart_${symbol}_${index}`}
                  height={384}
                  theme={theme}
                  autosize={true}
                />
              </div>
              
              {/* Chart Footer with Volume and Stats */}
              <div className="bg-gray-900/50 border-t border-gray-700 p-2">
                <div className="flex items-center justify-between text-xs text-gray-400">
                  <div className="flex items-center gap-3">
                    <span>Vol: {price?.volume || '--'}</span>
                    <span>Tick: ${instrument.tickSize}</span>
                    <span>Point: ${instrument.pointValue}</span>
                  </div>
                  <div className="flex items-center gap-1">
                    <Clock className="h-3 w-3" />
                    <span>
                      {price?.timestamp ? 
                        new Date(price.timestamp).toLocaleTimeString() : 
                        '--'
                      }
                    </span>
                  </div>
                </div>
              </div>
            </motion.div>
          );
        })}
        
        {/* Add Chart Button */}
        {selectedInstruments.length < layoutConfigs[layout].maxCharts && (
          <motion.div
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            className="bg-gray-800/30 border-2 border-dashed border-gray-700 rounded-xl
              flex items-center justify-center cursor-pointer hover:bg-gray-800/50 
              transition-all duration-300 min-h-[400px]"
            onClick={() => setShowSettings(true)}
          >
            <div className="text-center">
              <Plus className="h-12 w-12 text-gray-600 mx-auto mb-3" />
              <p className="text-gray-500">Add Chart</p>
            </div>
          </motion.div>
        )}
      </div>
    );
  };

  return (
    <div className="h-full bg-gradient-to-br from-purple-900 to-gray-900 p-6">
      {/* Header */}
      <motion.div
        initial={{ opacity: 0, y: -20 }}
        animate={{ opacity: 1, y: 0 }}
        className="mb-6"
      >
        <div className="flex items-center justify-between">
          <div>
            <h1 className="text-4xl font-bold text-white mb-2 flex items-center gap-3">
              <BarChart3 className="h-10 w-10 text-purple-400" />
              TradingView Charts
            </h1>
            <p className="text-gray-400">
              Professional real-time market analysis with TradingView
            </p>
          </div>
          
          {/* Market Status */}
          <div className="flex items-center gap-4">
            <div className={`px-4 py-2 rounded-lg flex items-center gap-2 ${
              marketStatus === 'open' ? 'bg-green-500/20 text-green-400' :
              marketStatus === 'pre-market' ? 'bg-yellow-500/20 text-yellow-400' :
              'bg-red-500/20 text-red-400'
            }`}>
              <Activity className="h-4 w-4" />
              <span className="font-semibold">
                {marketStatus === 'open' ? 'Market Open' :
                 marketStatus === 'pre-market' ? 'Pre-Market' :
                 'Market Closed'}
              </span>
            </div>
            
            <div className="flex items-center gap-2">
              {wsConnected ? (
                <div className="flex items-center gap-2 text-green-400">
                  <Zap className="h-4 w-4" />
                  <span className="text-sm">Live</span>
                </div>
              ) : (
                <div className="flex items-center gap-2 text-red-400">
                  <AlertCircle className="h-4 w-4" />
                  <span className="text-sm">Offline</span>
                </div>
              )}
            </div>
          </div>
        </div>
      </motion.div>
      
      {/* Control Bar */}
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        className="bg-gray-800/50 backdrop-blur-lg border border-gray-700 rounded-xl p-4 mb-6"
      >
        <div className="flex items-center justify-between">
          {/* Layout Selector */}
          <div className="flex items-center gap-3">
            <span className="text-gray-400 text-sm">Layout:</span>
            <div className="flex gap-2">
              {Object.keys(layoutConfigs).map(layoutKey => (
                <button
                  key={layoutKey}
                  onClick={() => changeLayout(layoutKey)}
                  className={`px-3 py-1 rounded-lg transition-all ${
                    layout === layoutKey
                      ? 'bg-purple-600 text-white'
                      : 'bg-gray-700 text-gray-400 hover:bg-gray-600'
                  }`}
                >
                  <div className="flex items-center gap-1">
                    <Grid className="h-4 w-4" />
                    <span>{layoutKey}</span>
                  </div>
                </button>
              ))}
            </div>
          </div>
          
          {/* Timeframe Selector */}
          <div className="flex items-center gap-3">
            <span className="text-gray-400 text-sm">Timeframe:</span>
            <div className="flex gap-1">
              {timeframes.slice(3, 9).map(tf => (
                <button
                  key={tf.value}
                  onClick={() => setSelectedTimeframe(tf.value)}
                  className={`px-3 py-1 rounded-lg text-sm transition-all ${
                    selectedTimeframe === tf.value
                      ? 'bg-purple-600 text-white'
                      : 'bg-gray-700 text-gray-400 hover:bg-gray-600'
                  }`}
                >
                  {tf.label}
                </button>
              ))}
            </div>
          </div>
          
          {/* Actions */}
          <div className="flex items-center gap-2">
            <button
              onClick={() => setTheme(theme === 'dark' ? 'light' : 'dark')}
              className="p-2 bg-gray-700 hover:bg-gray-600 rounded-lg transition-colors"
              title="Toggle Theme"
            >
              <Monitor className="h-4 w-4 text-gray-400" />
            </button>
            
            <button
              onClick={() => setShowSettings(!showSettings)}
              className="p-2 bg-gray-700 hover:bg-gray-600 rounded-lg transition-colors"
              title="Settings"
            >
              <Settings className="h-4 w-4 text-gray-400" />
            </button>
            
            <button
              onClick={initializeWebSocket}
              className="p-2 bg-gray-700 hover:bg-gray-600 rounded-lg transition-colors"
              title="Refresh Connection"
            >
              <RefreshCw className="h-4 w-4 text-gray-400" />
            </button>
          </div>
        </div>
      </motion.div>
      
      {/* Instrument Selector (Settings Panel) */}
      {showSettings && (
        <motion.div
          initial={{ opacity: 0, y: -20 }}
          animate={{ opacity: 1, y: 0 }}
          className="bg-gray-800/50 backdrop-blur-lg border border-gray-700 rounded-xl p-4 mb-6"
        >
          <div className="flex items-center justify-between mb-4">
            <h3 className="text-white font-semibold">Select Instruments</h3>
            <button
              onClick={() => setShowSettings(false)}
              className="p-1 hover:bg-gray-700 rounded transition-colors"
            >
              <X className="h-4 w-4 text-gray-400" />
            </button>
          </div>
          
          <div className="grid grid-cols-6 gap-3">
            {instruments.map(instrument => {
              const isSelected = selectedInstruments.includes(instrument.symbol);
              const price = livePrice[instrument.symbol];
              
              return (
                <button
                  key={instrument.symbol}
                  onClick={() => toggleInstrument(instrument.symbol)}
                  className={`p-3 rounded-lg border transition-all ${
                    isSelected
                      ? 'bg-purple-600/20 border-purple-500 text-white'
                      : 'bg-gray-700/50 border-gray-600 text-gray-400 hover:bg-gray-700'
                  }`}
                >
                  <div className="text-left">
                    <div className="flex items-center justify-between mb-1">
                      <span className="font-semibold">{instrument.symbol}</span>
                      <div 
                        className="w-2 h-2 rounded-full"
                        style={{ backgroundColor: instrument.color }}
                      />
                    </div>
                    <div className="text-xs text-gray-500">{instrument.name}</div>
                    {price && (
                      <div className="mt-2 text-xs">
                        <span className="font-mono">${price.price?.toFixed(2)}</span>
                        <span className={`ml-2 ${
                          price.change >= 0 ? 'text-green-400' : 'text-red-400'
                        }`}>
                          {price.change >= 0 ? '+' : ''}{price.changePercent?.toFixed(2)}%
                        </span>
                      </div>
                    )}
                  </div>
                </button>
              );
            })}
          </div>
          
          <div className="mt-4 flex items-center justify-between">
            <p className="text-xs text-gray-500">
              Selected: {selectedInstruments.length} / {layoutConfigs[layout].maxCharts}
            </p>
            <button
              onClick={() => setSelectedInstruments([])}
              className="text-xs text-red-400 hover:text-red-300 transition-colors"
            >
              Clear All
            </button>
          </div>
        </motion.div>
      )}
      
      {/* Chart Grid */}
      {renderChartGrid()}
      
      {/* Stats Bar */}
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ delay: 0.3 }}
        className="mt-6 bg-gray-800/50 backdrop-blur-lg border border-gray-700 rounded-xl p-4"
      >
        <div className="flex items-center justify-between">
          <div className="flex items-center gap-6">
            <div className="flex items-center gap-2">
              <Layers className="h-4 w-4 text-gray-400" />
              <span className="text-gray-400 text-sm">Charts:</span>
              <span className="text-white font-semibold">
                {selectedInstruments.length}
              </span>
            </div>
            
            <div className="flex items-center gap-2">
              <Activity className="h-4 w-4 text-gray-400" />
              <span className="text-gray-400 text-sm">Updates:</span>
              <span className="text-white font-semibold">Real-time</span>
            </div>
            
            <div className="flex items-center gap-2">
              <Clock className="h-4 w-4 text-gray-400" />
              <span className="text-gray-400 text-sm">Timeframe:</span>
              <span className="text-white font-semibold">
                {timeframes.find(tf => tf.value === selectedTimeframe)?.label}
              </span>
            </div>
          </div>
          
          <div className="text-xs text-gray-500">
            Last updated: {new Date().toLocaleTimeString()}
          </div>
        </div>
      </motion.div>
    </div>
  );
};

export default TradingViewDashboard;
