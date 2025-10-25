import React, { useState, useEffect } from 'react';
import { motion } from 'framer-motion';
import { 
  Play, 
  Settings, 
  Info,
  TrendingUp,
  DollarSign,
  Target,
  Shield,
  AlertTriangle,
  Check
} from 'lucide-react';
import { apiClient } from '../config/api';
import toast from 'react-hot-toast';

const Algorithm = ({ onStatusChange }) => {
  const [algorithmConfig, setAlgorithmConfig] = useState({
    name: '9 Point',
    instrument: '',
    accountName: '',
    pointsSpacing: 9,
    maxOrdersPerSide: 5,
    stopLossPoints: 5,
    takeProfitPoints: 5,
    quantityPerOrder: 1,
    orderType: 'limit',
    marketOpenHour: 9,
    marketOpenMinute: 30,
    firstHourDuration: 60
  });

  const [isRunning, setIsRunning] = useState(false);
  const [loading, setLoading] = useState(false);
  const [algorithmId, setAlgorithmId] = useState(null);
  const [instruments, setInstruments] = useState([]);
  const [accounts, setAccounts] = useState([]);
  const [loadingData, setLoadingData] = useState(true);

  useEffect(() => {
    fetchInstrumentsAndAccounts();
  }, []);

  const fetchInstrumentsAndAccounts = async () => {
    try {
      setLoadingData(true);
      
      // Fetch instruments
      const instrumentsRes = await fetch('http://localhost:8000/api/instruments');
      const instrumentsData = await instrumentsRes.json();
      
      // Fetch accounts
      const accountsRes = await fetch('http://localhost:8000/api/accounts');
      const accountsData = await accountsRes.json();
      
      if (instrumentsData.instruments) {
        setInstruments(instrumentsData.instruments.map(inst => ({
          value: inst.symbol,
          label: `${inst.symbol} - ${inst.name}`
        })));
        
        // Set first instrument as default
        if (instrumentsData.instruments.length > 0) {
          setAlgorithmConfig(prev => ({
            ...prev,
            instrument: instrumentsData.instruments[0].symbol
          }));
        }
      }
      
      if (accountsData.accounts && accountsData.accounts.length > 0) {
        setAccounts(accountsData.accounts.map(acc => ({
          value: acc.id || acc.account_id,
          label: `${acc.name || acc.account_name} - ${acc.balance ? `$${acc.balance.toLocaleString()}` : 'N/A'}`
        })));
      } else if (accountsData.error) {
        toast.error(accountsData.error);
      }
    } catch (error) {
      toast.error('Failed to fetch instruments and accounts');
      console.error('Error fetching data:', error);
    } finally {
      setLoadingData(false);
    }
  };

  const handleConfigChange = (field, value) => {
    setAlgorithmConfig(prev => ({
      ...prev,
      [field]: value
    }));
  };

  const startAlgorithm = async () => {
    setLoading(true);
    try {
      const response = await apiClient.post('/api/algorithms/start', algorithmConfig);
      
      if (response.success) {
        setIsRunning(true);
        setAlgorithmId(response.algorithmId);
        toast.success(`${algorithmConfig.name} algorithm started successfully!`);
        
        // Update parent component status
        if (onStatusChange) {
          onStatusChange('running');
        }
      }
    } catch (error) {
      toast.error('Failed to start algorithm');
      console.error(error);
    } finally {
      setLoading(false);
    }
  };

  const stopAlgorithm = async () => {
    setLoading(true);
    try {
      // Update algorithm status in Supabase
      const { error } = await supabase
        .from('active_algorithms')
        .update({ status: 'stopped', stopped_at: new Date() })
        .eq('name', algorithmConfig.name)
        .eq('status', 'running');

      if (!error) {
        setIsRunning(false);
        toast.success('Algorithm stopped successfully!');
      }
    } catch (error) {
      toast.error('Failed to stop algorithm');
      console.error(error);
    } finally {
      setLoading(false);
    }
  };

  const ConfigField = ({ label, value, onChange, type = 'number', icon: Icon, options = null, suffix = '' }) => (
    <div className="bg-gray-800 rounded-lg p-4 border border-gray-700">
      <div className="flex items-center gap-2 mb-2">
        {Icon && <Icon className="text-blue-500" size={18} />}
        <label className="text-sm font-medium text-gray-300">{label}</label>
      </div>
      {options ? (
        <select
          value={value}
          onChange={(e) => onChange(e.target.value)}
          className="w-full bg-gray-700 border border-gray-600 rounded-lg px-3 py-2 text-white focus:border-blue-500 focus:outline-none"
          disabled={isRunning}
        >
          {options.map(opt => (
            <option key={opt.value} value={opt.value}>{opt.label}</option>
          ))}
        </select>
      ) : (
        <div className="flex items-center">
          <input
            type={type}
            value={value}
            onChange={(e) => onChange(type === 'number' ? parseFloat(e.target.value) : e.target.value)}
            className="flex-1 bg-gray-700 border border-gray-600 rounded-lg px-3 py-2 text-white focus:border-blue-500 focus:outline-none"
            disabled={isRunning}
          />
          {suffix && <span className="ml-2 text-gray-400">{suffix}</span>}
        </div>
      )}
    </div>
  );

  return (
    <div className="h-full overflow-auto p-6">
      {/* Header */}
      <div className="mb-6">
        <h1 className="text-3xl font-bold mb-2">Algorithm Trading</h1>
        <p className="text-gray-400">Configure and run the 9 Point breakout algorithm</p>
      </div>

      {/* Algorithm Status */}
      <motion.div 
        className={`mb-6 p-4 rounded-xl border ${
          isRunning 
            ? 'bg-green-900/20 border-green-600' 
            : 'bg-gray-800 border-gray-700'
        }`}
        animate={{
          borderColor: isRunning ? ['#10b981', '#22c55e', '#10b981'] : '#374151'
        }}
        transition={{
          duration: 2,
          repeat: isRunning ? Infinity : 0
        }}
      >
        <div className="flex items-center justify-between">
          <div className="flex items-center gap-3">
            <div className={`w-3 h-3 rounded-full ${
              isRunning ? 'bg-green-500 animate-pulse' : 'bg-gray-500'
            }`}></div>
            <div>
              <h2 className="text-xl font-semibold">{algorithmConfig.name} Algorithm</h2>
              <p className="text-sm text-gray-400">
                Status: {isRunning ? 'Running' : 'Stopped'}
              </p>
            </div>
          </div>
          <button
            onClick={isRunning ? stopAlgorithm : startAlgorithm}
            disabled={loading}
            className={`flex items-center gap-2 px-6 py-3 rounded-lg font-medium transition-all ${
              isRunning
                ? 'bg-red-600 hover:bg-red-700'
                : 'bg-green-600 hover:bg-green-700'
            } ${loading ? 'opacity-50 cursor-not-allowed' : ''}`}
          >
            {loading ? (
              <div className="animate-spin rounded-full h-5 w-5 border-b-2 border-white"></div>
            ) : isRunning ? (
              <>
                <Settings size={20} />
                Stop Algorithm
              </>
            ) : (
              <>
                <Play size={20} />
                Start Algorithm
              </>
            )}
          </button>
        </div>
      </motion.div>

      {/* Algorithm Info */}
      <div className="mb-6 bg-blue-900/20 border border-blue-600 rounded-xl p-4">
        <div className="flex items-start gap-3">
          <Info className="text-blue-500 mt-1" size={20} />
          <div className="text-sm text-gray-300">
            <p className="mb-2">
              <strong>First Hour Breakout Strategy:</strong> This algorithm waits for the first hour candle after market open, 
              then places orders at specific intervals above and below the high/low.
            </p>
            <ul className="list-disc list-inside space-y-1">
              <li>Places SHORT orders every {algorithmConfig.pointsSpacing} points above the high</li>
              <li>Places LONG orders every {algorithmConfig.pointsSpacing} points below the low</li>
              <li>Each order has {algorithmConfig.stopLossPoints} points stop loss and {algorithmConfig.takeProfitPoints} points take profit</li>
              <li>Maximum {algorithmConfig.maxOrdersPerSide} orders per side</li>
            </ul>
          </div>
        </div>
      </div>

      {/* Configuration */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
        <ConfigField
          label="Instrument"
          value={algorithmConfig.instrument}
          onChange={(v) => handleConfigChange('instrument', v)}
          icon={TrendingUp}
          options={instruments}
        />

        <ConfigField
          label="Account"
          value={algorithmConfig.accountName}
          onChange={(v) => handleConfigChange('accountName', v)}
          icon={DollarSign}
          options={accounts}
        />

        <ConfigField
          label="Points Spacing"
          value={algorithmConfig.pointsSpacing}
          onChange={(v) => handleConfigChange('pointsSpacing', v)}
          icon={Target}
          suffix="points"
        />

        <ConfigField
          label="Max Orders Per Side"
          value={algorithmConfig.maxOrdersPerSide}
          onChange={(v) => handleConfigChange('maxOrdersPerSide', v)}
          icon={Settings}
        />

        <ConfigField
          label="Stop Loss"
          value={algorithmConfig.stopLossPoints}
          onChange={(v) => handleConfigChange('stopLossPoints', v)}
          icon={Shield}
          suffix="points"
        />

        <ConfigField
          label="Take Profit"
          value={algorithmConfig.takeProfitPoints}
          onChange={(v) => handleConfigChange('takeProfitPoints', v)}
          icon={Check}
          suffix="points"
        />

        <ConfigField
          label="Quantity Per Order"
          value={algorithmConfig.quantityPerOrder}
          onChange={(v) => handleConfigChange('quantityPerOrder', v)}
          icon={Settings}
          suffix="contracts"
        />

        <ConfigField
          label="Market Open Hour"
          value={algorithmConfig.marketOpenHour}
          onChange={(v) => handleConfigChange('marketOpenHour', v)}
          icon={Settings}
          suffix="ET"
        />

        <ConfigField
          label="First Hour Duration"
          value={algorithmConfig.firstHourDuration}
          onChange={(v) => handleConfigChange('firstHourDuration', v)}
          icon={Settings}
          suffix="minutes"
        />
      </div>

      {/* Risk Warning */}
      <div className="mt-6 bg-yellow-900/20 border border-yellow-600 rounded-xl p-4">
        <div className="flex items-start gap-3">
          <AlertTriangle className="text-yellow-500 mt-1" size={20} />
          <div className="text-sm text-gray-300">
            <p className="font-semibold mb-1">Risk Warning</p>
            <p>
              Trading futures involves substantial risk of loss and is not suitable for all investors. 
              Past performance is not indicative of future results. Always use proper risk management.
            </p>
          </div>
        </div>
      </div>
    </div>
  );
};

export default Algorithm;
