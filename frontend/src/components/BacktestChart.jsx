/**
 * Backtest Chart Component
 * Displays backtest results with tick data and trade markers
 * Uses TradingView's free Lightweight Charts library
 */

import React, { useState, useEffect } from 'react';
import LightweightChart from './LightweightChart';
import { backtestApiService } from '../services/backtestApiService';
import { tradeMarkerService } from '../services/tradeMarkerService';
import toast from 'react-hot-toast';
import {
  BarChart3,
  Filter,
  RefreshCw,
  AlertTriangle,
  CheckCircle,
  XCircle
} from 'lucide-react';

const BacktestChart = ({
  runId,
  contract,
  dateFrom,
  dateTo,
  showChart = true,
  resolution = '10T'
}) => {
  const [tradeMarkers, setTradeMarkers] = useState([]);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState(null);
  const [stats, setStats] = useState(null);
  const [filters, setFilters] = useState({
    positionType: 'All',
    resultType: 'All'
  });

  // Fetch trade markers when runId changes
  useEffect(() => {
    if (runId) {
      fetchTradeMarkers();
    }
  }, [runId]);

  const fetchTradeMarkers = async () => {
    setIsLoading(true);
    setError(null);
    
    try {
      // Fetch trade markers from backend
      const response = await backtestApiService.getTradeMarkers(runId);
      
      if (response.markers) {
        // Transform markers to chart format
        const transformedMarkers = response.markers.map(marker => 
          tradeMarkerService.transformMarker(marker)
        );
        
        setTradeMarkers(transformedMarkers);
        
        // Calculate statistics
        const stats = calculateStats(transformedMarkers);
        setStats(stats);
        
        toast.success(`Loaded ${transformedMarkers.length} trades`);
      } else {
        setError('No trade data found for this backtest');
      }
    } catch (err) {
      console.error('Error fetching trade markers:', err);
      setError('Failed to load trade data');
      toast.error('Failed to load trade data');
    } finally {
      setIsLoading(false);
    }
  };

  const calculateStats = (markers) => {
    if (!markers || markers.length === 0) return null;

    const wins = markers.filter(m => m.result === 'Filled' && m.pnl > 0);
    const losses = markers.filter(m => m.result === 'Filled' && m.pnl < 0);
    const notTriggered = markers.filter(m => m.result === 'NotTriggered');
    
    const totalPnL = markers.reduce((sum, m) => sum + (m.pnl || 0), 0);
    const winRate = wins.length / (wins.length + losses.length) * 100 || 0;
    const avgWin = wins.length > 0 ? wins.reduce((sum, m) => sum + m.pnl, 0) / wins.length : 0;
    const avgLoss = losses.length > 0 ? losses.reduce((sum, m) => sum + m.pnl, 0) / losses.length : 0;
    
    return {
      totalTrades: markers.length,
      wins: wins.length,
      losses: losses.length,
      notTriggered: notTriggered.length,
      winRate: winRate.toFixed(2),
      totalPnL: totalPnL.toFixed(2),
      avgWin: avgWin.toFixed(2),
      avgLoss: avgLoss.toFixed(2),
      profitFactor: Math.abs(avgWin / avgLoss).toFixed(2)
    };
  };

  const handleFilterChange = (filterType, value) => {
    setFilters(prev => ({
      ...prev,
      [filterType]: value
    }));
  };

  const refreshData = () => {
    fetchTradeMarkers();
  };

  return (
    <div className="space-y-6">
      {/* Header with Controls */}
      <div className="bg-gray-800 rounded-lg p-4 border border-gray-700">
        <div className="flex items-center justify-between mb-4">
          <div className="flex items-center gap-3">
            <BarChart3 className="h-6 w-6 text-purple-500" />
            <h2 className="text-xl font-semibold">Backtest Visualization</h2>
            {runId && (
              <span className="text-sm text-gray-400">
                Run ID: {runId}
              </span>
            )}
          </div>
          
          <button
            onClick={refreshData}
            className="flex items-center gap-2 px-4 py-2 bg-purple-600 hover:bg-purple-700 rounded-lg transition-colors"
            disabled={isLoading}
          >
            <RefreshCw className={`h-4 w-4 ${isLoading ? 'animate-spin' : ''}`} />
            Refresh
          </button>
        </div>

        {/* Filters */}
        <div className="flex gap-4">
          <div className="flex items-center gap-2">
            <Filter className="h-4 w-4 text-gray-400" />
            <span className="text-sm text-gray-400">Filters:</span>
          </div>
          
          <select
            value={filters.positionType}
            onChange={(e) => handleFilterChange('positionType', e.target.value)}
            className="bg-gray-700 border border-gray-600 rounded px-3 py-1 text-sm focus:border-purple-500 focus:outline-none"
          >
            <option value="All">All Positions</option>
            <option value="Long">Long Only</option>
            <option value="Short">Short Only</option>
          </select>
          
          <select
            value={filters.resultType}
            onChange={(e) => handleFilterChange('resultType', e.target.value)}
            className="bg-gray-700 border border-gray-600 rounded px-3 py-1 text-sm focus:border-purple-500 focus:outline-none"
          >
            <option value="All">All Results</option>
            <option value="Filled">Filled</option>
            <option value="Lost">Lost</option>
            <option value="NotTriggered">Not Triggered</option>
          </select>
        </div>
      </div>

      {/* Statistics */}
      {stats && (
        <div className="grid grid-cols-2 md:grid-cols-4 lg:grid-cols-5 gap-4">
          <StatCard
            title="Total Trades"
            value={stats.totalTrades}
            icon={<BarChart3 className="h-5 w-5" />}
            color="text-gray-400"
          />
          <StatCard
            title="Win Rate"
            value={`${stats.winRate}%`}
            icon={<CheckCircle className="h-5 w-5" />}
            color={parseFloat(stats.winRate) >= 50 ? "text-green-500" : "text-red-500"}
          />
          <StatCard
            title="Total P&L"
            value={`$${stats.totalPnL}`}
            icon={<span className="text-sm font-bold">P&L</span>}
            color={parseFloat(stats.totalPnL) >= 0 ? "text-green-500" : "text-red-500"}
          />
          <StatCard
            title="Wins / Losses"
            value={`${stats.wins} / ${stats.losses}`}
            icon={<span className="text-xs">W/L</span>}
            color="text-blue-500"
          />
          <StatCard
            title="Profit Factor"
            value={stats.profitFactor}
            icon={<span className="text-xs">PF</span>}
            color={parseFloat(stats.profitFactor) >= 1 ? "text-green-500" : "text-red-500"}
          />
        </div>
      )}

      {/* Error Display */}
      {error && (
        <div className="bg-red-900/20 border border-red-600 rounded-lg p-4">
          <div className="flex items-center gap-3">
            <AlertTriangle className="h-5 w-5 text-red-500" />
            <p className="text-red-400">{error}</p>
          </div>
        </div>
      )}

      {/* Chart */}
      {showChart && !error && (
        <div className="bg-gray-800 rounded-lg p-4 border border-gray-700">
          <LightweightChart
            symbol={contract || 'NQ'}
            interval={resolution}
            height={500}
            dateFrom={dateFrom}
            dateTo={dateTo}
            tradeMarkers={tradeMarkers}
            showMarkers={true}
            markerFilters={filters}
            theme="dark"
            autosize={true}
          />
        </div>
      )}

      {/* Trade List */}
      {tradeMarkers.length > 0 && (
        <div className="bg-gray-800 rounded-lg border border-gray-700">
          <div className="p-4 border-b border-gray-700">
            <h3 className="text-lg font-semibold">Trade Details</h3>
          </div>
          <div className="overflow-x-auto">
            <table className="w-full">
              <thead>
                <tr className="border-b border-gray-700">
                  <th className="px-4 py-3 text-left text-sm font-medium text-gray-400">Time</th>
                  <th className="px-4 py-3 text-left text-sm font-medium text-gray-400">Type</th>
                  <th className="px-4 py-3 text-left text-sm font-medium text-gray-400">Entry</th>
                  <th className="px-4 py-3 text-left text-sm font-medium text-gray-400">Exit</th>
                  <th className="px-4 py-3 text-left text-sm font-medium text-gray-400">P&L</th>
                  <th className="px-4 py-3 text-left text-sm font-medium text-gray-400">Result</th>
                </tr>
              </thead>
              <tbody>
                {tradeMarkers
                  .filter(m => {
                    if (filters.positionType !== 'All' && m.position_type !== filters.positionType) return false;
                    if (filters.resultType !== 'All' && m.result !== filters.resultType) return false;
                    return true;
                  })
                  .slice(0, 10)
                  .map((marker, idx) => (
                    <TradeRow key={idx} trade={marker} />
                  ))}
              </tbody>
            </table>
          </div>
        </div>
      )}
    </div>
  );
};

// Statistics Card Component
const StatCard = ({ title, value, icon, color }) => (
  <div className="bg-gray-800 rounded-lg p-4 border border-gray-700">
    <div className="flex items-center justify-between mb-2">
      <span className="text-xs text-gray-400">{title}</span>
      <span className={color}>{icon}</span>
    </div>
    <div className={`text-lg font-bold ${color}`}>
      {value}
    </div>
  </div>
);

// Trade Row Component
const TradeRow = ({ trade }) => {
  const formatTime = (timestamp) => {
    return new Date(timestamp).toLocaleString('en-US', {
      month: 'short',
      day: 'numeric',
      hour: '2-digit',
      minute: '2-digit'
    });
  };

  return (
    <tr className="border-b border-gray-700 hover:bg-gray-700/50">
      <td className="px-4 py-3 text-sm">{formatTime(trade.entry_time)}</td>
      <td className="px-4 py-3 text-sm">
        <span className={`px-2 py-1 rounded text-xs ${
          trade.position_type === 'Long' ? 'bg-green-600' : 'bg-red-600'
        }`}>
          {trade.position_type}
        </span>
      </td>
      <td className="px-4 py-3 text-sm">{trade.entry_price.toFixed(2)}</td>
      <td className="px-4 py-3 text-sm">{trade.exit_price.toFixed(2)}</td>
      <td className={`px-4 py-3 text-sm font-medium ${
        trade.pnl >= 0 ? 'text-green-500' : 'text-red-500'
      }`}>
        ${trade.pnl.toFixed(2)}
      </td>
      <td className="px-4 py-3 text-sm">
        <span className={`px-2 py-1 rounded text-xs ${
          trade.result === 'Filled' ? 'bg-green-600' : 
          trade.result === 'Lost' ? 'bg-red-600' : 
          'bg-gray-600'
        }`}>
          {trade.result}
        </span>
      </td>
    </tr>
  );
};

export default BacktestChart;
