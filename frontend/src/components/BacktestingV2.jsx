/**
 * Backtesting V2 Component
 * Enhanced backtesting interface with Lightweight Charts integration
 */

import React, { useState } from 'react';
import { motion } from 'framer-motion';
import DatePicker from 'react-datepicker';
import "react-datepicker/dist/react-datepicker.css";
import { 
  Play, 
  Calendar,
  TrendingUp,
  DollarSign,
  Target,
  Shield,
  Settings,
  FileText,
  Download,
  BarChart3,
  AlertCircle,
  Loader2
} from 'lucide-react';
import toast from 'react-hot-toast';
import BacktestChart from './BacktestChart';
import { backtestApiService } from '../services/backtestApiService';

const BacktestingV2 = () => {
  const [backtestConfig, setBacktestConfig] = useState({
    algorithm: '9 Point',
    instrument: 'NQ',
    startDate: new Date(Date.now() - 30 * 24 * 60 * 60 * 1000), // 30 days ago
    endDate: new Date(),
    pointsSpacing: 15,
    exitStrategy: '20_7',
    teamWay: 'BreakThrough',
    initialBalance: 100000
  });

  const [isRunning, setIsRunning] = useState(false);
  const [results, setResults] = useState(null);
  const [runId, setRunId] = useState(null);
  const [progress, setProgress] = useState(0);

  const instruments = [
    { value: 'NQ', label: 'NQ - E-mini Nasdaq-100' },
    { value: 'ES', label: 'ES - E-mini S&P 500' },
    { value: 'MNQ', label: 'MNQ - Micro E-mini Nasdaq-100' },
    { value: 'MES', label: 'MES - Micro E-mini S&P 500' }
  ];

  const algorithms = [
    { value: '9 Point', label: '9 Point Opening Range' },
    { value: 'First Hour', label: 'First Hour Breakout' }
  ];

  const exitStrategies = [
    { value: '20_7', label: '20 points / 7 points' },
    { value: '10_4', label: '10 points / 4 points' },
    { value: '15_5', label: '15 points / 5 points' },
    { value: '25_10', label: '25 points / 10 points' }
  ];

  const teamWays = [
    { value: 'BreakThrough', label: 'BreakThrough' },
    { value: 'Reverse', label: 'Reverse' }
  ];

  const handleConfigChange = (field, value) => {
    setBacktestConfig(prev => ({
      ...prev,
      [field]: value
    }));
  };

  const runBacktest = async () => {
    setIsRunning(true);
    setProgress(0);
    setResults(null);
    setRunId(null);
    
    try {
      // Format dates for API
      const dateFrom = backtestConfig.startDate.toISOString();
      const dateTo = backtestConfig.endDate.toISOString();
      
      // Generate unique run ID
      const newRunId = `BT_${backtestConfig.instrument}_${Date.now()}`;
      setRunId(newRunId);
      
      // Call API to run backtest
      const response = await backtestApiService.runBacktest({
        run_id: newRunId,
        contract: backtestConfig.instrument,
        strategy_name: `${backtestConfig.algorithm}_${backtestConfig.teamWay}`,
        exit_strategy_key: backtestConfig.exitStrategy,
        point_key: `${backtestConfig.pointsSpacing}_7_5`,
        team_way: backtestConfig.teamWay,
        date_from: dateFrom,
        date_to: dateTo,
        metadata: {
          initial_balance: backtestConfig.initialBalance,
          algorithm: backtestConfig.algorithm
        }
      });

      // Simulate progress updates
      const progressInterval = setInterval(() => {
        setProgress(prev => {
          if (prev >= 100) {
            clearInterval(progressInterval);
            return 100;
          }
          return prev + 10;
        });
      }, 500);

      if (response.success) {
        // Store results
        setResults(response.results);
        setProgress(100);
        
        toast.success('Backtest completed successfully!');
      } else {
        throw new Error(response.error || 'Backtest failed');
      }
    } catch (error) {
      console.error('Backtest error:', error);
      toast.error(error.message || 'Failed to run backtest');
      setResults(null);
      setRunId(null);
    } finally {
      setIsRunning(false);
    }
  };

  const downloadResults = () => {
    if (!results) return;

    const csv = [
      ['Metric', 'Value'],
      ['Run ID', runId],
      ['Instrument', backtestConfig.instrument],
      ['Algorithm', backtestConfig.algorithm],
      ['Team Way', backtestConfig.teamWay],
      ['Exit Strategy', backtestConfig.exitStrategy],
      ['Total Trades', results.totalTrades || 0],
      ['Win Rate', `${results.winRate || 0}%`],
      ['Total P&L', `$${results.totalPnL || 0}`],
      ['Max Drawdown', `$${results.maxDrawdown || 0}`]
    ].map(row => row.join(',')).join('\n');

    const blob = new Blob([csv], { type: 'text/csv' });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = `backtest_${runId}.csv`;
    a.click();
    URL.revokeObjectURL(url);
  };

  const ConfigField = ({ label, value, onChange, type = 'number', icon: Icon, options = null, suffix = '' }) => (
    <div className="bg-gray-800 rounded-lg p-4 border border-gray-700">
      <div className="flex items-center gap-2 mb-2">
        {Icon && <Icon className="text-purple-500" size={18} />}
        <label className="text-sm font-medium text-gray-300">{label}</label>
      </div>
      {options ? (
        <select
          value={value}
          onChange={(e) => onChange(e.target.value)}
          className="w-full bg-gray-700 border border-gray-600 rounded-lg px-3 py-2 text-white focus:border-purple-500 focus:outline-none"
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
            className="flex-1 bg-gray-700 border border-gray-600 rounded-lg px-3 py-2 text-white focus:border-purple-500 focus:outline-none"
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
        <h1 className="text-3xl font-bold mb-2">Backtesting V2</h1>
        <p className="text-gray-400">Test your trading strategies with real tick data and advanced visualization</p>
      </div>

      {/* Configuration Section */}
      <div className="mb-6">
        <h2 className="text-xl font-semibold mb-4 flex items-center gap-2">
          <Settings className="text-purple-500" size={24} />
          Backtest Configuration
        </h2>
        
        {/* Date Range Selector */}
        <div className="mb-4 grid grid-cols-1 md:grid-cols-2 gap-4">
          <div className="bg-gray-800 rounded-lg p-4 border border-gray-700">
            <div className="flex items-center gap-2 mb-2">
              <Calendar className="text-purple-500" size={18} />
              <label className="text-sm font-medium text-gray-300">Start Date</label>
            </div>
            <DatePicker
              selected={backtestConfig.startDate}
              onChange={(date) => handleConfigChange('startDate', date)}
              className="w-full bg-gray-700 border border-gray-600 rounded-lg px-3 py-2 text-white focus:border-purple-500 focus:outline-none"
              disabled={isRunning}
            />
          </div>
          
          <div className="bg-gray-800 rounded-lg p-4 border border-gray-700">
            <div className="flex items-center gap-2 mb-2">
              <Calendar className="text-purple-500" size={18} />
              <label className="text-sm font-medium text-gray-300">End Date</label>
            </div>
            <DatePicker
              selected={backtestConfig.endDate}
              onChange={(date) => handleConfigChange('endDate', date)}
              className="w-full bg-gray-700 border border-gray-600 rounded-lg px-3 py-2 text-white focus:border-purple-500 focus:outline-none"
              disabled={isRunning}
            />
          </div>
        </div>

        {/* Parameters Grid */}
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
          <ConfigField
            label="Algorithm"
            value={backtestConfig.algorithm}
            onChange={(v) => handleConfigChange('algorithm', v)}
            icon={Settings}
            options={algorithms}
          />

          <ConfigField
            label="Instrument"
            value={backtestConfig.instrument}
            onChange={(v) => handleConfigChange('instrument', v)}
            icon={TrendingUp}
            options={instruments}
          />

          <ConfigField
            label="Team Way"
            value={backtestConfig.teamWay}
            onChange={(v) => handleConfigChange('teamWay', v)}
            icon={Target}
            options={teamWays}
          />

          <ConfigField
            label="Exit Strategy"
            value={backtestConfig.exitStrategy}
            onChange={(v) => handleConfigChange('exitStrategy', v)}
            icon={Shield}
            options={exitStrategies}
          />

          <ConfigField
            label="Points Spacing"
            value={backtestConfig.pointsSpacing}
            onChange={(v) => handleConfigChange('pointsSpacing', v)}
            icon={Target}
            suffix="points"
          />

          <ConfigField
            label="Initial Balance"
            value={backtestConfig.initialBalance}
            onChange={(v) => handleConfigChange('initialBalance', v)}
            icon={DollarSign}
            suffix="$"
          />
        </div>

        {/* Run Button */}
        <div className="mt-6 flex items-center gap-4">
          <button
            onClick={runBacktest}
            disabled={isRunning}
            className={`flex items-center gap-2 px-6 py-3 rounded-lg font-medium transition-all ${
              isRunning
                ? 'bg-gray-600 cursor-not-allowed'
                : 'bg-purple-600 hover:bg-purple-700'
            }`}
          >
            {isRunning ? (
              <>
                <Loader2 className="animate-spin" size={20} />
                Running Backtest... {progress}%
              </>
            ) : (
              <>
                <Play size={20} />
                Run Backtest
              </>
            )}
          </button>

          {results && (
            <button
              onClick={downloadResults}
              className="flex items-center gap-2 px-4 py-2 bg-gray-700 hover:bg-gray-600 rounded-lg transition-colors"
            >
              <Download size={18} />
              Export Results
            </button>
          )}
        </div>
      </div>

      {/* Progress Bar */}
      {isRunning && (
        <div className="mb-6">
          <div className="bg-gray-800 rounded-lg p-4 border border-gray-700">
            <div className="flex justify-between mb-2">
              <span className="text-sm text-gray-400">Processing tick data...</span>
              <span className="text-sm text-gray-400">{progress}%</span>
            </div>
            <div className="w-full bg-gray-700 rounded-full h-2">
              <motion.div 
                className="bg-purple-600 h-2 rounded-full"
                initial={{ width: 0 }}
                animate={{ width: `${progress}%` }}
                transition={{ duration: 0.3 }}
              />
            </div>
          </div>
        </div>
      )}

      {/* Chart and Results */}
      {runId && (
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.5 }}
        >
          <BacktestChart
            runId={runId}
            contract={backtestConfig.instrument}
            dateFrom={backtestConfig.startDate.toISOString()}
            dateTo={backtestConfig.endDate.toISOString()}
            showChart={true}
            resolution="10T"
          />
        </motion.div>
      )}

      {/* Info Box */}
      <div className="mt-6 bg-blue-900/20 border border-blue-600 rounded-lg p-4">
        <div className="flex items-start gap-3">
          <AlertCircle className="text-blue-500 mt-1" size={20} />
          <div className="text-sm text-gray-300">
            <p className="font-semibold mb-1">Using Real Tick Data</p>
            <p>
              This backtesting engine uses real tick data from your Supabase database. 
              Charts are rendered using TradingView's free Lightweight Charts library for professional visualization.
            </p>
          </div>
        </div>
      </div>
    </div>
  );
};

export default BacktestingV2;
