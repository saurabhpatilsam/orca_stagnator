import React, { useState, useEffect } from 'react';
import { motion } from 'framer-motion';
import { 
  Play, 
  TrendingUp, 
  DollarSign, 
  Target, 
  Shield, 
  Info, 
  CheckCircle, 
  XCircle, 
  ArrowRight,
  Repeat,
  AlertTriangle
} from 'lucide-react';
import { apiClient } from '../config/api';
import toast from 'react-hot-toast';
import instruments from '../config/instruments';

// Instrument tick sizes (minimum price increment)
const INSTRUMENT_TICK_SIZES = {
  'ES': 0.25,      // E-mini S&P 500
  'MES': 0.25,     // Micro E-mini S&P 500
  'NQ': 0.25,      // E-mini Nasdaq
  'MNQ': 0.25,     // Micro E-mini Nasdaq
  'YM': 1.0,       // E-mini Dow
  'MYM': 1.0,      // Micro E-mini Dow
  'RTY': 0.10,     // E-mini Russell 2000
  'M2K': 0.10,     // Micro E-mini Russell 2000
};

// Get tick size for an instrument
const getTickSize = (instrument) => {
  return INSTRUMENT_TICK_SIZES[instrument] || 0.25; // Default to 0.25 for futures
};

// Round price to nearest tick size
const roundToTick = (price, tickSize) => {
  if (tickSize <= 0) return price;
  return Math.round(price / tickSize) * tickSize;
};

const HedgingAlgo = () => {
  // State for hedge configuration
  const [hedgeConfig, setHedgeConfig] = useState({
    account_a_name: '',
    account_b_name: '',
    instrument: 'ES',
    direction: 'long',
    entry_price: 0,
    quantity: 1,
    tp_distance: 10,
    sl_distance: 10,
    hedge_distance: 0
  });

  const [loading, setLoading] = useState(false);
  const [accounts, setAccounts] = useState([]);
  const [loadingAccounts, setLoadingAccounts] = useState(true);
  const [lastResult, setLastResult] = useState(null);

  // Fetch accounts on component mount
  useEffect(() => {
    fetchAccounts();
  }, []);

  const fetchAccounts = async () => {
    setLoadingAccounts(true);
    try {
      const response = await apiClient.get('/api/v1/trading/accounts');
      if (response.accounts && response.accounts.length > 0) {
        const formattedAccounts = response.accounts.map(acc => ({
          value: acc.name || acc.account_name,
          label: `${acc.name || acc.account_name} (${acc.id || acc.account_id})`
        }));
        setAccounts(formattedAccounts);
        
        // Set default accounts if available
        if (formattedAccounts.length >= 2) {
          setHedgeConfig(prev => ({
            ...prev,
            account_a_name: formattedAccounts[0].value,
            account_b_name: formattedAccounts[1].value
          }));
        }
      }
    } catch (error) {
      console.error('Failed to fetch accounts:', error);
      toast.error('Failed to load accounts');
    } finally {
      setLoadingAccounts(false);
    }
  };

  // Calculate Account B entry price based on hedge distance
  const calculateAccountBEntry = () => {
    const { entry_price, hedge_distance, direction, instrument } = hedgeConfig;
    const tickSize = getTickSize(instrument);
    let entryB;
    
    if (direction === 'long') {
      entryB = entry_price - hedge_distance;
    } else {
      entryB = entry_price + hedge_distance;
    }
    
    return roundToTick(entryB, tickSize);
  };

  // Calculate TP/SL for given entry and direction
  const calculateTPSL = (entry, direction, tp_dist, sl_dist) => {
    const tickSize = getTickSize(hedgeConfig.instrument);
    
    if (direction === 'long') {
      return {
        tp: roundToTick(entry + tp_dist, tickSize),
        sl: roundToTick(entry - sl_dist, tickSize)
      };
    } else {
      return {
        tp: roundToTick(entry - tp_dist, tickSize),
        sl: roundToTick(entry + sl_dist, tickSize)
      };
    }
  };

  // Handle configuration changes
  const handleConfigChange = (field, value) => {
    let processedValue = value;
    
    if (field === 'quantity') {
      // Parse as integer with minimum value of 1
      processedValue = Math.max(1, parseInt(value) || 1);
    } else if (field === 'hedge_distance') {
      // Ensure non-negative value
      processedValue = Math.max(0, parseFloat(value) || 0);
    } else if (field === 'entry_price' || field === 'tp_distance' || field === 'sl_distance') {
      // Parse as float for other numeric fields
      processedValue = parseFloat(value) || 0;
    }
    
    setHedgeConfig(prev => ({
      ...prev,
      [field]: processedValue
    }));
  };

  // Start hedge algorithm
  const handleStartHedge = async () => {
    // Validation
    if (!hedgeConfig.account_a_name || !hedgeConfig.account_b_name) {
      toast.error('Please select both accounts');
      return;
    }
    // Prevent same account selection
    if (hedgeConfig.account_a_name === hedgeConfig.account_b_name) {
      toast.error('Account A and Account B must be different');
      return;
    }
    if (!hedgeConfig.instrument) {
      toast.error('Please select an instrument');
      return;
    }
    if (hedgeConfig.entry_price <= 0) {
      toast.error('Please enter a valid entry price');
      return;
    }
    if (hedgeConfig.quantity <= 0) {
      toast.error('Please enter a valid quantity');
      return;
    }

    setLoading(true);
    try {
      const response = await apiClient.post('/api/v1/hedge/start', hedgeConfig);
      
      if (response.status === 'success') {
        toast.success(
          `Hedge placed successfully! Orders: ${response.account_a_result.order_id}, ${response.account_b_result.order_id}`
        );
      } else if (response.status === 'partial') {
        const failedAccount = response.account_a_result.status === 'failed' 
          ? response.account_a_result.account_name 
          : response.account_b_result.account_name;
        const successAccount = response.account_a_result.status === 'success'
          ? response.account_a_result.account_name
          : response.account_b_result.account_name;
        toast(
          `Partial success: ${successAccount} order placed, but ${failedAccount} failed`,
          { icon: '⚠️' }
        );
      } else {
        toast.error('Failed to place hedge orders');
      }
      
      setLastResult(response);
    } catch (error) {
      console.error('Hedge algorithm error:', error);
      toast.error(error.message || 'Failed to start hedge algorithm');
    } finally {
      setLoading(false);
    }
  };

  // Calculate positions for display
  const accountBEntry = calculateAccountBEntry();
  const accountACalc = calculateTPSL(
    hedgeConfig.entry_price,
    hedgeConfig.direction,
    hedgeConfig.tp_distance,
    hedgeConfig.sl_distance
  );
  const accountBCalc = calculateTPSL(
    accountBEntry,
    hedgeConfig.direction === 'long' ? 'short' : 'long',
    hedgeConfig.tp_distance,
    hedgeConfig.sl_distance
  );

  return (
    <div className="p-6 bg-black min-h-screen">
      {/* Header */}
      <div className="mb-6">
        <h1 className="text-3xl font-bold text-white mb-2">Hedging Algorithm</h1>
        <p className="text-gray-400">Place opposite trades on two accounts with configurable hedge distance</p>
      </div>

      {/* Info Panel */}
      <motion.div 
        className="bg-blue-900/20 border border-blue-600 rounded-lg p-4 mb-6"
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
      >
        <div className="flex items-start gap-3">
          <Info className="text-blue-500 mt-1" size={20} />
          <div className="text-sm text-gray-300">
            <p className="mb-2">
              <strong>Hedging Algorithm:</strong> Automatically places opposite trades on two accounts.
            </p>
            <p>
              Example: If Account A goes <strong>LONG at 5000</strong> with hedge distance <strong>5</strong>, 
              Account B will go <strong>SHORT at 4995</strong>.
            </p>
          </div>
        </div>
      </motion.div>

      {/* Form Section */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4 mb-6">
        {/* Account A Selector */}
        <div className="bg-gray-900 border border-gray-800 rounded-lg p-4">
          <div className="flex items-center gap-2 mb-2">
            <DollarSign className="text-blue-500" size={18} />
            <label className="text-sm font-medium text-gray-300">Account A</label>
          </div>
          {loadingAccounts ? (
            <div className="h-10 bg-gray-800 animate-pulse rounded-lg"></div>
          ) : (
            <select
              value={hedgeConfig.account_a_name}
              onChange={(e) => handleConfigChange('account_a_name', e.target.value)}
              className="w-full bg-gray-900 border border-gray-800 text-white rounded-lg px-3 py-2 focus:border-blue-500 focus:outline-none"
              disabled={loading}
            >
              <option value="">Select Account A</option>
              {accounts.map(acc => (
                <option 
                  key={acc.value} 
                  value={acc.value}
                  disabled={acc.value === hedgeConfig.account_b_name}
                >
                  {acc.label}
                </option>
              ))}
            </select>
          )}
        </div>

        {/* Account B Selector */}
        <div className="bg-gray-900 border border-gray-800 rounded-lg p-4">
          <div className="flex items-center gap-2 mb-2">
            <DollarSign className="text-blue-500" size={18} />
            <label className="text-sm font-medium text-gray-300">Account B</label>
          </div>
          {loadingAccounts ? (
            <div className="h-10 bg-gray-800 animate-pulse rounded-lg"></div>
          ) : (
            <select
              value={hedgeConfig.account_b_name}
              onChange={(e) => handleConfigChange('account_b_name', e.target.value)}
              className="w-full bg-gray-900 border border-gray-800 text-white rounded-lg px-3 py-2 focus:border-blue-500 focus:outline-none"
              disabled={loading}
            >
              <option value="">Select Account B</option>
              {accounts.map(acc => (
                <option 
                  key={acc.value} 
                  value={acc.value}
                  disabled={acc.value === hedgeConfig.account_a_name}
                >
                  {acc.label}
                </option>
              ))}
            </select>
          )}
        </div>

        {/* Instrument Selector */}
        <div className="bg-gray-900 border border-gray-800 rounded-lg p-4">
          <div className="flex items-center gap-2 mb-2">
            <TrendingUp className="text-blue-500" size={18} />
            <label className="text-sm font-medium text-gray-300">Instrument</label>
          </div>
          <select
            value={hedgeConfig.instrument}
            onChange={(e) => handleConfigChange('instrument', e.target.value)}
            className="w-full bg-gray-900 border border-gray-800 text-white rounded-lg px-3 py-2 focus:border-blue-500 focus:outline-none"
            disabled={loading}
          >
            {instruments.map(inst => (
              <option key={inst.value} value={inst.value}>{inst.label}</option>
            ))}
          </select>
        </div>

        {/* Direction Toggle */}
        <div className="bg-gray-900 border border-gray-800 rounded-lg p-4">
          <div className="flex items-center gap-2 mb-2">
            <Repeat className="text-blue-500" size={18} />
            <label className="text-sm font-medium text-gray-300">Direction (Account A)</label>
          </div>
          <div className="flex gap-2">
            <button
              onClick={() => handleConfigChange('direction', 'long')}
              className={`flex-1 py-2 rounded-lg font-medium transition-all ${
                hedgeConfig.direction === 'long'
                  ? 'bg-white text-black'
                  : 'bg-gray-900 text-white border border-gray-800 hover:bg-gray-800'
              }`}
              disabled={loading}
            >
              Long
            </button>
            <button
              onClick={() => handleConfigChange('direction', 'short')}
              className={`flex-1 py-2 rounded-lg font-medium transition-all ${
                hedgeConfig.direction === 'short'
                  ? 'bg-white text-black'
                  : 'bg-gray-900 text-white border border-gray-800 hover:bg-gray-800'
              }`}
              disabled={loading}
            >
              Short
            </button>
          </div>
        </div>

        {/* Entry Price */}
        <div className="bg-gray-900 border border-gray-800 rounded-lg p-4">
          <div className="flex items-center gap-2 mb-2">
            <Target className="text-blue-500" size={18} />
            <label className="text-sm font-medium text-gray-300">Entry Price (Account A)</label>
          </div>
          <input
            type="number"
            step={getTickSize(hedgeConfig.instrument)}
            value={hedgeConfig.entry_price}
            onChange={(e) => handleConfigChange('entry_price', e.target.value)}
            className="w-full bg-gray-900 border border-gray-800 text-white rounded-lg px-3 py-2 focus:border-blue-500 focus:outline-none"
            disabled={loading}
            placeholder="5000.00"
          />
        </div>

        {/* Quantity */}
        <div className="bg-gray-900 border border-gray-800 rounded-lg p-4">
          <div className="flex items-center gap-2 mb-2">
            <DollarSign className="text-blue-500" size={18} />
            <label className="text-sm font-medium text-gray-300">Quantity</label>
          </div>
          <input
            type="number"
            min="1"
            step="1"
            value={hedgeConfig.quantity}
            onChange={(e) => handleConfigChange('quantity', e.target.value)}
            className="w-full bg-gray-900 border border-gray-800 text-white rounded-lg px-3 py-2 focus:border-blue-500 focus:outline-none"
            disabled={loading}
          />
        </div>

        {/* TP Distance */}
        <div className="bg-gray-900 border border-gray-800 rounded-lg p-4">
          <div className="flex items-center gap-2 mb-2">
            <Target className="text-blue-500" size={18} />
            <label className="text-sm font-medium text-gray-300">TP Distance (points)</label>
          </div>
          <input
            type="number"
            step={getTickSize(hedgeConfig.instrument)}
            value={hedgeConfig.tp_distance}
            onChange={(e) => handleConfigChange('tp_distance', e.target.value)}
            className="w-full bg-gray-900 border border-gray-800 text-white rounded-lg px-3 py-2 focus:border-blue-500 focus:outline-none"
            disabled={loading}
          />
        </div>

        {/* SL Distance */}
        <div className="bg-gray-900 border border-gray-800 rounded-lg p-4">
          <div className="flex items-center gap-2 mb-2">
            <Shield className="text-blue-500" size={18} />
            <label className="text-sm font-medium text-gray-300">SL Distance (points)</label>
          </div>
          <input
            type="number"
            step={getTickSize(hedgeConfig.instrument)}
            value={hedgeConfig.sl_distance}
            onChange={(e) => handleConfigChange('sl_distance', e.target.value)}
            className="w-full bg-gray-900 border border-gray-800 text-white rounded-lg px-3 py-2 focus:border-blue-500 focus:outline-none"
            disabled={loading}
          />
        </div>

        {/* Hedge Distance */}
        <div className="bg-gray-900 border border-gray-800 rounded-lg p-4">
          <div className="flex items-center gap-2 mb-2">
            <Repeat className="text-blue-500" size={18} />
            <label className="text-sm font-medium text-gray-300">Hedge Distance (points)</label>
          </div>
          <input
            type="number"
            min="0"
            step={getTickSize(hedgeConfig.instrument)}
            value={hedgeConfig.hedge_distance}
            onChange={(e) => handleConfigChange('hedge_distance', e.target.value)}
            className="w-full bg-gray-900 border border-gray-800 text-white rounded-lg px-3 py-2 focus:border-blue-500 focus:outline-none"
            disabled={loading}
            placeholder="0"
          />
        </div>
      </div>

      {/* Calculation Preview Panel */}
      {hedgeConfig.entry_price > 0 && (
        <motion.div 
          className="bg-gray-900 border border-gray-800 rounded-lg p-6 mb-6"
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
        >
          <h3 className="text-xl font-semibold text-white mb-4">Calculated Positions</h3>
          <div className="grid grid-cols-1 md:grid-cols-3 gap-4 items-center">
            {/* Account A */}
            <div className="bg-gray-800 rounded-lg p-4">
              <div className="text-sm text-gray-400 mb-1">Account A</div>
              <div className="text-white font-medium mb-2">{hedgeConfig.account_a_name || 'Not Selected'}</div>
              <div className={`inline-block px-2 py-1 rounded text-xs font-medium mb-2 ${
                hedgeConfig.direction === 'long' ? 'bg-green-600' : 'bg-red-600'
              }`}>
                {hedgeConfig.direction.toUpperCase()}
              </div>
              <div className="space-y-1 text-sm">
                <div className="flex justify-between">
                  <span className="text-gray-400">Entry:</span>
                  <span className="text-white font-medium">{hedgeConfig.entry_price.toFixed(2)}</span>
                </div>
                <div className="flex justify-between">
                  <span className="text-gray-400">TP:</span>
                  <span className="text-green-400">{accountACalc.tp.toFixed(2)}</span>
                </div>
                <div className="flex justify-between">
                  <span className="text-gray-400">SL:</span>
                  <span className="text-red-400">{accountACalc.sl.toFixed(2)}</span>
                </div>
              </div>
            </div>

            {/* Arrow */}
            <div className="flex justify-center">
              <ArrowRight className="text-gray-600" size={32} />
            </div>

            {/* Account B */}
            <div className="bg-gray-800 rounded-lg p-4">
              <div className="text-sm text-gray-400 mb-1">Account B</div>
              <div className="text-white font-medium mb-2">{hedgeConfig.account_b_name || 'Not Selected'}</div>
              <div className={`inline-block px-2 py-1 rounded text-xs font-medium mb-2 ${
                hedgeConfig.direction === 'long' ? 'bg-red-600' : 'bg-green-600'
              }`}>
                {hedgeConfig.direction === 'long' ? 'SHORT' : 'LONG'}
              </div>
              <div className="space-y-1 text-sm">
                <div className="flex justify-between">
                  <span className="text-gray-400">Entry:</span>
                  <span className="text-white font-medium">{accountBEntry.toFixed(2)}</span>
                </div>
                <div className="flex justify-between">
                  <span className="text-gray-400">TP:</span>
                  <span className="text-green-400">{accountBCalc.tp.toFixed(2)}</span>
                </div>
                <div className="flex justify-between">
                  <span className="text-gray-400">SL:</span>
                  <span className="text-red-400">{accountBCalc.sl.toFixed(2)}</span>
                </div>
              </div>
            </div>
          </div>
        </motion.div>
      )}

      {/* Action Button */}
      <div className="flex justify-center mb-6">
        <button
          onClick={handleStartHedge}
          disabled={loading || !hedgeConfig.account_a_name || !hedgeConfig.account_b_name || hedgeConfig.entry_price <= 0}
          className={`bg-white text-black hover:bg-gray-200 px-8 py-4 rounded-lg font-semibold text-lg flex items-center gap-3 transition-all ${
            loading || !hedgeConfig.account_a_name || !hedgeConfig.account_b_name || hedgeConfig.entry_price <= 0
              ? 'opacity-50 cursor-not-allowed'
              : ''
          }`}
        >
          {loading ? (
            <div className="animate-spin rounded-full h-6 w-6 border-b-2 border-black"></div>
          ) : (
            <Play size={24} />
          )}
          Start Hedge Algorithm
        </button>
      </div>

      {/* Results Section */}
      {lastResult && (
        <motion.div 
          className="bg-gray-900 border border-gray-800 rounded-lg p-6 mb-6"
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
        >
          <div className="flex items-center justify-between mb-4">
            <h3 className="text-xl font-semibold text-white">Last Hedge Result</h3>
            <div className={`flex items-center gap-2 px-3 py-1 rounded-lg text-sm font-medium ${
              lastResult.status === 'success' 
                ? 'bg-green-900/20 text-green-400 border border-green-600'
                : lastResult.status === 'partial'
                ? 'bg-yellow-900/20 text-yellow-400 border border-yellow-600'
                : 'bg-red-900/20 text-red-400 border border-red-600'
            }`}>
              {lastResult.status === 'success' && <CheckCircle size={16} />}
              {lastResult.status === 'partial' && <AlertTriangle size={16} />}
              {lastResult.status === 'failed' && <XCircle size={16} />}
              {lastResult.status.toUpperCase()}
            </div>
          </div>
          
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            {/* Account A Result */}
            <div className={`p-4 rounded-lg border ${
              lastResult.account_a_result.status === 'success'
                ? 'bg-green-900/20 border-green-600'
                : 'bg-red-900/20 border-red-600'
            }`}>
              <div className="flex items-center justify-between mb-3">
                <h4 className="font-medium text-white">Account A: {lastResult.account_a_result.account_name}</h4>
                {lastResult.account_a_result.status === 'success' ? (
                  <CheckCircle className="text-green-400" size={20} />
                ) : (
                  <XCircle className="text-red-400" size={20} />
                )}
              </div>
              <div className="space-y-2 text-sm">
                {lastResult.account_a_result.order_id && (
                  <div className="flex justify-between">
                    <span className="text-gray-400">Order ID:</span>
                    <span className="text-white font-mono">{lastResult.account_a_result.order_id}</span>
                  </div>
                )}
                <div className="flex justify-between">
                  <span className="text-gray-400">Direction:</span>
                  <span className="text-white">{lastResult.account_a_result.direction ? lastResult.account_a_result.direction.toUpperCase() : '-'}</span>
                </div>
                <div className="flex justify-between">
                  <span className="text-gray-400">Entry:</span>
                  <span className="text-white">{lastResult.account_a_result.entry_price != null ? lastResult.account_a_result.entry_price.toFixed(2) : '-'}</span>
                </div>
                <div className="flex justify-between">
                  <span className="text-gray-400">TP/SL:</span>
                  <span className="text-white">
                    {lastResult.account_a_result.take_profit != null ? lastResult.account_a_result.take_profit.toFixed(2) : '-'} / {lastResult.account_a_result.stop_loss != null ? lastResult.account_a_result.stop_loss.toFixed(2) : '-'}
                  </span>
                </div>
                {lastResult.account_a_result.error_message && (
                  <div className="mt-2 text-red-400 text-xs">
                    Error: {lastResult.account_a_result.error_message}
                  </div>
                )}
              </div>
            </div>

            {/* Account B Result */}
            <div className={`p-4 rounded-lg border ${
              lastResult.account_b_result.status === 'success'
                ? 'bg-green-900/20 border-green-600'
                : 'bg-red-900/20 border-red-600'
            }`}>
              <div className="flex items-center justify-between mb-3">
                <h4 className="font-medium text-white">Account B: {lastResult.account_b_result.account_name}</h4>
                {lastResult.account_b_result.status === 'success' ? (
                  <CheckCircle className="text-green-400" size={20} />
                ) : (
                  <XCircle className="text-red-400" size={20} />
                )}
              </div>
              <div className="space-y-2 text-sm">
                {lastResult.account_b_result.order_id && (
                  <div className="flex justify-between">
                    <span className="text-gray-400">Order ID:</span>
                    <span className="text-white font-mono">{lastResult.account_b_result.order_id}</span>
                  </div>
                )}
                <div className="flex justify-between">
                  <span className="text-gray-400">Direction:</span>
                  <span className="text-white">{lastResult.account_b_result.direction ? lastResult.account_b_result.direction.toUpperCase() : '-'}</span>
                </div>
                <div className="flex justify-between">
                  <span className="text-gray-400">Entry:</span>
                  <span className="text-white">{lastResult.account_b_result.entry_price != null ? lastResult.account_b_result.entry_price.toFixed(2) : '-'}</span>
                </div>
                <div className="flex justify-between">
                  <span className="text-gray-400">TP/SL:</span>
                  <span className="text-white">
                    {lastResult.account_b_result.take_profit != null ? lastResult.account_b_result.take_profit.toFixed(2) : '-'} / {lastResult.account_b_result.stop_loss != null ? lastResult.account_b_result.stop_loss.toFixed(2) : '-'}
                  </span>
                </div>
                {lastResult.account_b_result.error_message && (
                  <div className="mt-2 text-red-400 text-xs">
                    Error: {lastResult.account_b_result.error_message}
                  </div>
                )}
              </div>
            </div>
          </div>
        </motion.div>
      )}

      {/* Risk Warning */}
      <div className="bg-yellow-900/20 border border-yellow-600 rounded-lg p-4">
        <div className="flex items-start gap-3">
          <AlertTriangle className="text-yellow-500 mt-1" size={20} />
          <div className="text-sm text-gray-300">
            <p className="mb-1">
              <strong>Risk Warning:</strong> Hedging strategies involve placing opposite trades which may not eliminate all risk.
            </p>
            <p>
              Please ensure you understand the risks and have adequate capital before using this algorithm.
            </p>
          </div>
        </div>
      </div>
    </div>
  );
};

export default HedgingAlgo;
