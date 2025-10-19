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
  AlertCircle
} from 'lucide-react';
import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer } from 'recharts';
import toast from 'react-hot-toast';

const Backtesting = () => {
  const [backtestConfig, setBacktestConfig] = useState({
    algorithm: '9 Point',
    instrument: 'ESZ5',
    startDate: new Date(Date.now() - 30 * 24 * 60 * 60 * 1000), // 30 days ago
    endDate: new Date(),
    pointsSpacing: 9,
    maxOrdersPerSide: 5,
    stopLossPoints: 5,
    takeProfitPoints: 5,
    quantityPerOrder: 1,
    initialBalance: 100000
  });

  const [isRunning, setIsRunning] = useState(false);
  const [results, setResults] = useState(null);
  const [progress, setProgress] = useState(0);

  const instruments = [
    { value: 'ESZ5', label: 'ES December 2025' },
    { value: 'NQZ5', label: 'NQ December 2025' },
    { value: 'MESZ5', label: 'MES December 2025' },
    { value: 'MNQZ5', label: 'MNQ December 2025' }
  ];

  const algorithms = [
    { value: '9 Point', label: '9 Point Breakout' },
    { value: 'First Hour', label: 'First Hour Breakout' }
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
    
    // Simulate backtest progress
    const progressInterval = setInterval(() => {
      setProgress(prev => {
        if (prev >= 100) {
          clearInterval(progressInterval);
          return 100;
        }
        return prev + 10;
      });
    }, 300);

    try {
      // Simulate API call to run backtest
      await new Promise(resolve => setTimeout(resolve, 3000));

      // Mock backtest results
      const mockResults = {
        totalTrades: 42,
        winningTrades: 28,
        losingTrades: 14,
        winRate: 66.67,
        totalPnL: 8750.50,
        maxDrawdown: -2150.00,
        sharpeRatio: 1.85,
        profitFactor: 2.15,
        avgWin: 450.25,
        avgLoss: -225.50,
        bestTrade: 1250.00,
        worstTrade: -550.00,
        equityCurve: generateEquityCurve(),
        trades: generateTrades()
      };

      setResults(mockResults);
      toast.success('Backtest completed successfully!');
    } catch (error) {
      toast.error('Failed to run backtest');
      console.error(error);
    } finally {
      setIsRunning(false);
      setProgress(100);
    }
  };

  const generateEquityCurve = () => {
    const data = [];
    let balance = backtestConfig.initialBalance;
    const days = Math.floor((backtestConfig.endDate - backtestConfig.startDate) / (1000 * 60 * 60 * 24));
    
    for (let i = 0; i <= days; i++) {
      const change = (Math.random() - 0.45) * 1000; // Slight positive bias
      balance += change;
      data.push({
        day: i,
        balance: Math.round(balance * 100) / 100,
        date: new Date(backtestConfig.startDate.getTime() + i * 24 * 60 * 60 * 1000).toLocaleDateString()
      });
    }
    return data;
  };

  const generateTrades = () => {
    const trades = [];
    for (let i = 1; i <= 10; i++) {
      const isWin = Math.random() > 0.4;
      trades.push({
        id: i,
        date: new Date(Date.now() - Math.random() * 30 * 24 * 60 * 60 * 1000).toLocaleDateString(),
        side: Math.random() > 0.5 ? 'LONG' : 'SHORT',
        entry: 5900 + Math.random() * 20,
        exit: 5900 + Math.random() * 20 + (isWin ? 5 : -5),
        pnl: isWin ? Math.random() * 500 : -Math.random() * 250,
        status: isWin ? 'WIN' : 'LOSS'
      });
    }
    return trades;
  };

  const downloadResults = () => {
    if (!results) return;

    const csv = [
      ['Metric', 'Value'],
      ['Total Trades', results.totalTrades],
      ['Winning Trades', results.winningTrades],
      ['Losing Trades', results.losingTrades],
      ['Win Rate', `${results.winRate}%`],
      ['Total P&L', `$${results.totalPnL}`],
      ['Max Drawdown', `$${results.maxDrawdown}`],
      ['Sharpe Ratio', results.sharpeRatio],
      ['Profit Factor', results.profitFactor]
    ].map(row => row.join(',')).join('\n');

    const blob = new Blob([csv], { type: 'text/csv' });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = `backtest_${backtestConfig.algorithm}_${new Date().toISOString()}.csv`;
    a.click();
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
        <h1 className="text-3xl font-bold mb-2">Backtesting</h1>
        <p className="text-gray-400">Test your trading strategies with historical data</p>
      </div>

      {/* Configuration Section */}
      <div className="mb-6">
        <h2 className="text-xl font-semibold mb-4">Backtest Configuration</h2>
        
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
            label="Initial Balance"
            value={backtestConfig.initialBalance}
            onChange={(v) => handleConfigChange('initialBalance', v)}
            icon={DollarSign}
            suffix="$"
          />

          <ConfigField
            label="Points Spacing"
            value={backtestConfig.pointsSpacing}
            onChange={(v) => handleConfigChange('pointsSpacing', v)}
            icon={Target}
            suffix="points"
          />

          <ConfigField
            label="Max Orders Per Side"
            value={backtestConfig.maxOrdersPerSide}
            onChange={(v) => handleConfigChange('maxOrdersPerSide', v)}
            icon={Settings}
          />

          <ConfigField
            label="Stop Loss"
            value={backtestConfig.stopLossPoints}
            onChange={(v) => handleConfigChange('stopLossPoints', v)}
            icon={Shield}
            suffix="points"
          />

          <ConfigField
            label="Take Profit"
            value={backtestConfig.takeProfitPoints}
            onChange={(v) => handleConfigChange('takeProfitPoints', v)}
            icon={Target}
            suffix="points"
          />

          <ConfigField
            label="Quantity Per Order"
            value={backtestConfig.quantityPerOrder}
            onChange={(v) => handleConfigChange('quantityPerOrder', v)}
            icon={Settings}
            suffix="contracts"
          />
        </div>

        {/* Run Button */}
        <div className="mt-6">
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
                <div className="animate-spin rounded-full h-5 w-5 border-b-2 border-white"></div>
                Running Backtest... {progress}%
              </>
            ) : (
              <>
                <Play size={20} />
                Run Backtest
              </>
            )}
          </button>
        </div>
      </div>

      {/* Progress Bar */}
      {isRunning && (
        <div className="mb-6">
          <div className="bg-gray-800 rounded-lg p-4 border border-gray-700">
            <div className="flex justify-between mb-2">
              <span className="text-sm text-gray-400">Processing historical data...</span>
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

      {/* Results Section */}
      {results && (
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.5 }}
        >
          <div className="mb-4 flex items-center justify-between">
            <h2 className="text-xl font-semibold">Backtest Results</h2>
            <button
              onClick={downloadResults}
              className="flex items-center gap-2 px-4 py-2 bg-gray-700 hover:bg-gray-600 rounded-lg transition-colors"
            >
              <Download size={18} />
              Export Results
            </button>
          </div>

          {/* Metrics Grid */}
          <div className="grid grid-cols-1 md:grid-cols-3 lg:grid-cols-4 gap-4 mb-6">
            <div className="bg-gray-800 rounded-lg p-4 border border-gray-700">
              <div className="text-sm text-gray-400 mb-1">Total P&L</div>
              <div className={`text-2xl font-bold ${results.totalPnL >= 0 ? 'text-green-500' : 'text-red-500'}`}>
                ${results.totalPnL.toFixed(2)}
              </div>
            </div>
            
            <div className="bg-gray-800 rounded-lg p-4 border border-gray-700">
              <div className="text-sm text-gray-400 mb-1">Win Rate</div>
              <div className="text-2xl font-bold text-white">
                {results.winRate.toFixed(2)}%
              </div>
            </div>
            
            <div className="bg-gray-800 rounded-lg p-4 border border-gray-700">
              <div className="text-sm text-gray-400 mb-1">Total Trades</div>
              <div className="text-2xl font-bold text-white">
                {results.totalTrades}
              </div>
            </div>
            
            <div className="bg-gray-800 rounded-lg p-4 border border-gray-700">
              <div className="text-sm text-gray-400 mb-1">Sharpe Ratio</div>
              <div className="text-2xl font-bold text-white">
                {results.sharpeRatio}
              </div>
            </div>

            <div className="bg-gray-800 rounded-lg p-4 border border-gray-700">
              <div className="text-sm text-gray-400 mb-1">Max Drawdown</div>
              <div className="text-2xl font-bold text-red-500">
                ${results.maxDrawdown.toFixed(2)}
              </div>
            </div>
            
            <div className="bg-gray-800 rounded-lg p-4 border border-gray-700">
              <div className="text-sm text-gray-400 mb-1">Profit Factor</div>
              <div className="text-2xl font-bold text-white">
                {results.profitFactor}
              </div>
            </div>
            
            <div className="bg-gray-800 rounded-lg p-4 border border-gray-700">
              <div className="text-sm text-gray-400 mb-1">Avg Win</div>
              <div className="text-2xl font-bold text-green-500">
                ${results.avgWin.toFixed(2)}
              </div>
            </div>
            
            <div className="bg-gray-800 rounded-lg p-4 border border-gray-700">
              <div className="text-sm text-gray-400 mb-1">Avg Loss</div>
              <div className="text-2xl font-bold text-red-500">
                ${results.avgLoss.toFixed(2)}
              </div>
            </div>
          </div>

          {/* Equity Curve Chart */}
          <div className="mb-6 bg-gray-800 rounded-lg p-4 border border-gray-700">
            <h3 className="text-lg font-semibold mb-4 flex items-center gap-2">
              <BarChart3 className="text-purple-500" />
              Equity Curve
            </h3>
            <ResponsiveContainer width="100%" height={300}>
              <LineChart data={results.equityCurve}>
                <CartesianGrid strokeDasharray="3 3" stroke="#374151" />
                <XAxis dataKey="date" stroke="#9ca3af" />
                <YAxis stroke="#9ca3af" />
                <Tooltip 
                  contentStyle={{ backgroundColor: '#1f2937', border: '1px solid #374151' }}
                  labelStyle={{ color: '#9ca3af' }}
                />
                <Legend />
                <Line 
                  type="monotone" 
                  dataKey="balance" 
                  stroke="#8b5cf6" 
                  strokeWidth={2}
                  dot={false}
                />
              </LineChart>
            </ResponsiveContainer>
          </div>

          {/* Recent Trades Table */}
          <div className="bg-gray-800 rounded-lg border border-gray-700">
            <div className="p-4 border-b border-gray-700">
              <h3 className="text-lg font-semibold flex items-center gap-2">
                <FileText className="text-purple-500" />
                Recent Trades
              </h3>
            </div>
            <div className="overflow-x-auto">
              <table className="w-full">
                <thead>
                  <tr className="border-b border-gray-700">
                    <th className="px-4 py-3 text-left text-sm font-medium text-gray-400">Date</th>
                    <th className="px-4 py-3 text-left text-sm font-medium text-gray-400">Side</th>
                    <th className="px-4 py-3 text-left text-sm font-medium text-gray-400">Entry</th>
                    <th className="px-4 py-3 text-left text-sm font-medium text-gray-400">Exit</th>
                    <th className="px-4 py-3 text-left text-sm font-medium text-gray-400">P&L</th>
                    <th className="px-4 py-3 text-left text-sm font-medium text-gray-400">Status</th>
                  </tr>
                </thead>
                <tbody>
                  {results.trades.map((trade) => (
                    <tr key={trade.id} className="border-b border-gray-700 hover:bg-gray-700/50">
                      <td className="px-4 py-3 text-sm">{trade.date}</td>
                      <td className="px-4 py-3 text-sm">
                        <span className={`px-2 py-1 rounded text-xs ${
                          trade.side === 'LONG' ? 'bg-green-600' : 'bg-red-600'
                        }`}>
                          {trade.side}
                        </span>
                      </td>
                      <td className="px-4 py-3 text-sm">${trade.entry.toFixed(2)}</td>
                      <td className="px-4 py-3 text-sm">${trade.exit.toFixed(2)}</td>
                      <td className={`px-4 py-3 text-sm font-medium ${
                        trade.pnl >= 0 ? 'text-green-500' : 'text-red-500'
                      }`}>
                        ${trade.pnl.toFixed(2)}
                      </td>
                      <td className="px-4 py-3 text-sm">
                        <span className={`px-2 py-1 rounded text-xs ${
                          trade.status === 'WIN' ? 'bg-green-600' : 'bg-red-600'
                        }`}>
                          {trade.status}
                        </span>
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          </div>
        </motion.div>
      )}
    </div>
  );
};

export default Backtesting;
