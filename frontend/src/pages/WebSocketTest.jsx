/**
 * WebSocket Testing Page
 * Test Tradovate WebSocket connection and real-time data
 */

import React, { useState, useEffect } from 'react';
import { motion } from 'framer-motion';
import { 
  Wifi, 
  WifiOff, 
  Activity, 
  AlertCircle,
  CheckCircle,
  Loader2,
  Play,
  Square
} from 'lucide-react';
import { priceWebSocket } from '../services/priceWebSocket';
import { apiClient } from '../config/api';

const WebSocketTest = () => {
  const [isConnected, setIsConnected] = useState(false);
  const [isConnecting, setIsConnecting] = useState(false);
  const [mdToken, setMdToken] = useState(null);
  const [logs, setLogs] = useState([]);
  const [candleData, setCandleData] = useState([]);
  const [subscribed, setSubscribed] = useState(false);
  const [error, setError] = useState(null);
  const [wsStatus, setWsStatus] = useState(null);

  // Add log entry
  const addLog = (message, type = 'info') => {
    const timestamp = new Date().toLocaleTimeString();
    setLogs(prev => [...prev, { timestamp, message, type }].slice(-50)); // Keep last 50
  };

  // Fetch WebSocket status
  const fetchStatus = async () => {
    try {
      const response = await apiClient.get('/api/tradovate/ws-status');
      setWsStatus(response.data);
      addLog(`Status: ${response.data.status} - ${response.data.token_count} tokens available`, 'success');
    } catch (err) {
      addLog(`Failed to fetch status: ${err.message}`, 'error');
    }
  };

  const handleConnect = async () => {
    setIsConnecting(true);
    setError(null);
    addLog('Connecting to Redis Price service...', 'info');

    try {
      // Connect WebSocket
      await priceWebSocket.connect();
      
      setIsConnected(true);
      addLog('✅ WebSocket connected!', 'success');
    } catch (err) {
      setError(err.message);
      addLog(`❌ Connection failed: ${err.message}`, 'error');
    } finally {
      setIsConnecting(false);
    }
  };

  const handleDisconnect = () => {
    priceWebSocket.disconnect();
    setIsConnected(false);
    setSubscribed(false);
    addLog('🔌 WebSocket disconnected', 'warning');
  };

  // Subscribe to candles
  const handleSubscribe = () => {
    if (!isConnected) {
      addLog('Not connected to WebSocket', 'error');
      return;
    }

    addLog('Subscribing to MNQZ5 5-minute candles...', 'info');
    
    priceWebSocket.subscribeToCandles('MNQZ5', 5, (candles) => {
      addLog(`📊 Received ${candles.length} candles`, 'success');
      setCandleData(prev => [...candles, ...prev].slice(0, 100)); // Keep last 100
    });

    setSubscribed(true);
    addLog('✅ Subscribed to real-time candles', 'success');
  };

  // Unsubscribe from candles
  const handleUnsubscribe = () => {
    priceWebSocket.unsubscribeFromCandles('MNQZ5', 5);
    setSubscribed(false);
    addLog('🚫 Unsubscribed from candles', 'warning');
  };

  // Load status on mount
  useEffect(() => {
    fetchStatus();
  }, []);

  return (
    <div className="min-h-screen bg-gradient-to-br from-gray-900 via-purple-900 to-gray-900 p-6">
      <div className="max-w-7xl mx-auto">
        {/* Header */}
        <motion.div
          initial={{ opacity: 0, y: -20 }}
          animate={{ opacity: 1, y: 0 }}
          className="mb-8"
        >
          <h1 className="text-4xl font-bold text-white mb-2 flex items-center gap-3">
            <Activity className="h-10 w-10 text-purple-400" />
            WebSocket Testing Console
          </h1>
          <p className="text-gray-400">
            Test Tradovate WebSocket connection and real-time market data
          </p>
        </motion.div>

        {/* Connection Controls */}
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6 mb-6">
          {/* Connection Panel */}
          <motion.div
            initial={{ opacity: 0, x: -20 }}
            animate={{ opacity: 1, x: 0 }}
            className="bg-gray-800/50 backdrop-blur-lg border border-gray-700 rounded-xl p-6"
          >
            <h2 className="text-xl font-semibold text-white mb-4 flex items-center gap-2">
              {isConnected ? (
                <Wifi className="h-6 w-6 text-green-500" />
              ) : (
                <WifiOff className="h-6 w-6 text-red-500" />
              )}
              Connection
            </h2>

            {/* Status Badge */}
            <div className="mb-4">
              {isConnected ? (
                <div className="flex items-center gap-2 text-green-400">
                  <CheckCircle className="h-5 w-5" />
                  <span>Connected</span>
                </div>
              ) : (
                <div className="flex items-center gap-2 text-red-400">
                  <AlertCircle className="h-5 w-5" />
                  <span>Disconnected</span>
                </div>
              )}
            </div>

            {/* Buttons */}
            <div className="space-y-3">
              <button
                onClick={handleConnect}
                disabled={isConnected || isConnecting}
                className="w-full bg-green-600 hover:bg-green-700 disabled:bg-gray-600 text-white px-4 py-3 rounded-lg transition-all duration-200 flex items-center justify-center gap-2"
              >
                {isConnecting ? (
                  <>
                    <Loader2 className="h-5 w-5 animate-spin" />
                    Connecting...
                  </>
                ) : (
                  <>
                    <Play className="h-5 w-5" />
                    Connect
                  </>
                )}
              </button>

              <button
                onClick={handleDisconnect}
                disabled={!isConnected}
                className="w-full bg-red-600 hover:bg-red-700 disabled:bg-gray-600 text-white px-4 py-3 rounded-lg transition-all duration-200 flex items-center justify-center gap-2"
              >
                <Square className="h-5 w-5" />
                Disconnect
              </button>

              <button
                onClick={fetchStatus}
                className="w-full bg-blue-600 hover:bg-blue-700 text-white px-4 py-3 rounded-lg transition-all duration-200"
              >
                Refresh Status
              </button>
            </div>

            {/* Error Display */}
            {error && (
              <div className="mt-4 p-3 bg-red-900/30 border border-red-500 rounded-lg text-red-300 text-sm">
                {error}
              </div>
            )}
          </motion.div>

          {/* Subscription Panel */}
          <motion.div
            initial={{ opacity: 0, x: 20 }}
            animate={{ opacity: 1, x: 0 }}
            className="bg-gray-800/50 backdrop-blur-lg border border-gray-700 rounded-xl p-6"
          >
            <h2 className="text-xl font-semibold text-white mb-4">
              Subscription Controls
            </h2>

            <div className="space-y-3">
              <button
                onClick={handleSubscribe}
                disabled={!isConnected || subscribed}
                className="w-full bg-purple-600 hover:bg-purple-700 disabled:bg-gray-600 text-white px-4 py-3 rounded-lg transition-all duration-200"
              >
                Subscribe to MNQZ5 (5min)
              </button>

              <button
                onClick={handleUnsubscribe}
                disabled={!subscribed}
                className="w-full bg-orange-600 hover:bg-orange-700 disabled:bg-gray-600 text-white px-4 py-3 rounded-lg transition-all duration-200"
              >
                Unsubscribe
              </button>
            </div>

            {/* WebSocket Status */}
            {wsStatus && (
              <div className="mt-4 p-4 bg-gray-900/50 rounded-lg space-y-2 text-sm">
                <div className="flex justify-between">
                  <span className="text-gray-400">Status:</span>
                  <span className="text-white">{wsStatus.status}</span>
                </div>
                <div className="flex justify-between">
                  <span className="text-gray-400">Tokens:</span>
                  <span className="text-white">{wsStatus.token_count}</span>
                </div>
                <div className="flex justify-between">
                  <span className="text-gray-400">Accounts:</span>
                  <span className="text-white">{wsStatus.available_accounts?.join(', ')}</span>
                </div>
              </div>
            )}
          </motion.div>
        </div>

        {/* Logs Panel */}
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          className="bg-gray-800/50 backdrop-blur-lg border border-gray-700 rounded-xl p-6 mb-6"
        >
          <div className="flex items-center justify-between mb-4">
            <h2 className="text-xl font-semibold text-white">Event Logs</h2>
            <button
              onClick={() => setLogs([])}
              className="text-sm text-gray-400 hover:text-white transition-colors"
            >
              Clear Logs
            </button>
          </div>

          <div className="bg-black/50 rounded-lg p-4 h-64 overflow-y-auto font-mono text-sm">
            {logs.length === 0 ? (
              <p className="text-gray-500">No logs yet...</p>
            ) : (
              logs.map((log, idx) => (
                <div
                  key={idx}
                  className={`mb-1 ${
                    log.type === 'error' ? 'text-red-400' :
                    log.type === 'success' ? 'text-green-400' :
                    log.type === 'warning' ? 'text-yellow-400' :
                    'text-gray-300'
                  }`}
                >
                  <span className="text-gray-500">[{log.timestamp}]</span> {log.message}
                </div>
              ))
            )}
          </div>
        </motion.div>

        {/* Candle Data Panel */}
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          className="bg-gray-800/50 backdrop-blur-lg border border-gray-700 rounded-xl p-6"
        >
          <h2 className="text-xl font-semibold text-white mb-4">
            Real-time Candle Data ({candleData.length} received)
          </h2>

          <div className="bg-black/50 rounded-lg p-4 h-64 overflow-y-auto">
            {candleData.length === 0 ? (
              <p className="text-gray-500">No candle data yet...</p>
            ) : (
              <table className="w-full text-sm">
                <thead className="text-gray-400 border-b border-gray-700">
                  <tr>
                    <th className="text-left p-2">Time</th>
                    <th className="text-right p-2">Open</th>
                    <th className="text-right p-2">High</th>
                    <th className="text-right p-2">Low</th>
                    <th className="text-right p-2">Close</th>
                    <th className="text-right p-2">Volume</th>
                  </tr>
                </thead>
                <tbody className="text-gray-300">
                  {candleData.map((candle, idx) => (
                    <tr key={idx} className="border-b border-gray-800">
                      <td className="p-2">{new Date(candle.time * 1000).toLocaleTimeString()}</td>
                      <td className="text-right p-2">{candle.open?.toFixed(2)}</td>
                      <td className="text-right p-2">{candle.high?.toFixed(2)}</td>
                      <td className="text-right p-2">{candle.low?.toFixed(2)}</td>
                      <td className="text-right p-2">{candle.close?.toFixed(2)}</td>
                      <td className="text-right p-2">{candle.volume || 0}</td>
                    </tr>
                  ))}
                </tbody>
              </table>
            )}
          </div>
        </motion.div>
      </div>
    </div>
  );
};

export default WebSocketTest;
