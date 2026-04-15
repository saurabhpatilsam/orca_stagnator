/**
 * ChartControls Component
 * Provides controls for chart markers, filters, zoom, and export
 */

import React, { useState } from 'react';
import { ZoomIn, Maximize2, Download, ChevronDown, ChevronUp } from 'lucide-react';
import ToggleSwitch from './ui/ToggleSwitch';
import { FILTER_OPTIONS, LEGEND_ITEMS } from '../constants/chartControlConstants';

const ChartControls = ({
  showMarkers = true,
  onToggleMarkers,
  positionFilter = 'All',
  onPositionFilterChange,
  resultFilter = 'All',
  onResultFilterChange,
  onZoomToTrades,
  onResetZoom,
  onExportChart,
  isExporting = false,
  tradeStats = { total: 0, filled: 0, lost: 0, long: 0, short: 0, totalPnL: 0 }
}) => {
  const [legendCollapsed, setLegendCollapsed] = useState(false);

  return (
    <div className="bg-gray-800 rounded-lg border border-gray-700 p-4 mb-4">
      {/* Top Row: Toggle and Filters */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-4 mb-4">
        {/* Marker Toggle */}
        <div className="flex items-center">
          <ToggleSwitch
            enabled={showMarkers}
            onChange={onToggleMarkers}
            label="Show Trade Markers"
            size="medium"
          />
        </div>

        {/* Position Filter */}
        <div>
          <label className="block text-xs font-medium text-gray-400 mb-1">
            Position Type
          </label>
          <select
            value={positionFilter}
            onChange={(e) => onPositionFilterChange(e.target.value)}
            className="w-full bg-gray-700 border border-gray-600 rounded-lg px-3 py-2 text-sm text-white focus:border-purple-500 focus:outline-none"
          >
            {FILTER_OPTIONS.POSITION.map(option => (
              <option key={option.value} value={option.value}>
                {option.label}
              </option>
            ))}
          </select>
        </div>

        {/* Result Filter */}
        <div>
          <label className="block text-xs font-medium text-gray-400 mb-1">
            Result Type
          </label>
          <select
            value={resultFilter}
            onChange={(e) => onResultFilterChange(e.target.value)}
            className="w-full bg-gray-700 border border-gray-600 rounded-lg px-3 py-2 text-sm text-white focus:border-purple-500 focus:outline-none"
          >
            {FILTER_OPTIONS.RESULT.map(option => (
              <option key={option.value} value={option.value}>
                {option.label}
              </option>
            ))}
          </select>
        </div>
      </div>

      {/* Legend Section */}
      <div className="mb-4">
        <button
          onClick={() => setLegendCollapsed(!legendCollapsed)}
          className="flex items-center justify-between w-full text-left text-sm font-medium text-gray-300 hover:text-white transition-colors"
        >
          <span>Chart Legend</span>
          {legendCollapsed ? (
            <ChevronDown size={16} className="text-gray-400" />
          ) : (
            <ChevronUp size={16} className="text-gray-400" />
          )}
        </button>
        
        {!legendCollapsed && (
          <div className="mt-2 grid grid-cols-1 sm:grid-cols-3 gap-2">
            {LEGEND_ITEMS.map(item => (
              <div key={item.id} className="flex items-center gap-2">
                <div
                  className="w-3 h-3 rounded-full"
                  style={{ backgroundColor: item.color }}
                />
                <span className="text-xs text-gray-400">{item.label}</span>
              </div>
            ))}
          </div>
        )}
      </div>

      {/* Bottom Row: Actions and Stats */}
      <div className="flex flex-wrap items-center justify-between gap-4">
        {/* Action Buttons */}
        <div className="flex items-center gap-2">
          <button
            onClick={onZoomToTrades}
            className="flex items-center gap-2 px-3 py-2 bg-gray-700 hover:bg-gray-600 rounded-lg text-sm font-medium transition-colors"
            title="Zoom to Trades"
          >
            <ZoomIn size={18} />
            <span className="hidden sm:inline">Zoom to Trades</span>
          </button>
          
          <button
            onClick={onResetZoom}
            className="flex items-center gap-2 px-3 py-2 bg-gray-700 hover:bg-gray-600 rounded-lg text-sm font-medium transition-colors"
            title="Reset Zoom"
          >
            <Maximize2 size={18} />
            <span className="hidden sm:inline">Reset</span>
          </button>
          
          <button
            onClick={onExportChart}
            disabled={isExporting}
            className={`flex items-center gap-2 px-3 py-2 rounded-lg text-sm font-medium transition-colors ${
              isExporting
                ? 'bg-gray-600 cursor-not-allowed'
                : 'bg-purple-600 hover:bg-purple-700'
            }`}
            title="Export Chart"
          >
            {isExporting ? (
              <>
                <div className="animate-spin rounded-full h-4 w-4 border-b-2 border-white" />
                <span className="hidden sm:inline">Exporting...</span>
              </>
            ) : (
              <>
                <Download size={18} />
                <span className="hidden sm:inline">Export</span>
              </>
            )}
          </button>
        </div>

        {/* Compact Stats Bar */}
        <div className="flex items-center gap-4 text-xs">
          <div className="flex items-center gap-1">
            <span className="text-gray-400">Total:</span>
            <span className="font-semibold text-white">{tradeStats.total}</span>
          </div>
          <div className="flex items-center gap-1">
            <span className="text-gray-400">TP:</span>
            <span className="font-semibold text-green-500">{tradeStats.filled}</span>
          </div>
          <div className="flex items-center gap-1">
            <span className="text-gray-400">SL:</span>
            <span className="font-semibold text-red-500">{tradeStats.lost}</span>
          </div>
          <div className="hidden md:flex items-center gap-1">
            <span className="text-gray-400">P&L:</span>
            <span className={`font-semibold ${tradeStats.totalPnL >= 0 ? 'text-green-500' : 'text-red-500'}`}>
              ${tradeStats.totalPnL.toFixed(2)}
            </span>
          </div>
        </div>
      </div>
    </div>
  );
};

export default ChartControls;
