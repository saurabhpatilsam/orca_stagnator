import React, { useState, useEffect } from 'react';
import { motion } from 'framer-motion';
import PriceStreaming from './PriceStreaming';
import instruments from '../config/instruments';

const TradingDashboard = () => {
  // Convert shared instruments config to dashboard format
  const instrumentsForDisplay = instruments.map(inst => {
    const [symbol, description] = inst.label.split(' - ');
    return {
      symbol: inst.value,
      name: description,
      exchange: inst.value.startsWith('M') && inst.value !== 'MES' && inst.value !== 'MNQ' ? 'COMEX' : 'CME'
    };
  });

  return (
    <div className="h-full bg-gray-900 overflow-auto">
      {/* Header */}
      <header className="bg-gray-800 border-b border-gray-700 px-6 py-4 sticky top-0 z-10">
        <div className="flex items-center justify-between">
          <div>
            <h2 className="text-2xl font-semibold text-white">Dashboard</h2>
            <p className="text-gray-400 text-sm mt-1">Live Market Overview</p>
          </div>
          <div className="flex items-center space-x-4">
            <span className="text-gray-400 text-sm">
              {new Date().toLocaleTimeString('en-US', { 
                hour: '2-digit', 
                minute: '2-digit', 
                second: '2-digit',
                timeZone: 'America/New_York' 
              })} ET
            </span>
          </div>
        </div>
      </header>

      {/* Content Area */}
      <main className="p-6">
        <PriceStreaming instruments={instrumentsForDisplay} />
      </main>
    </div>
  );
};

export default TradingDashboard;
