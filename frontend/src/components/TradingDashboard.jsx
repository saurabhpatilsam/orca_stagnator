import React, { useState, useEffect } from 'react';
import { motion } from 'framer-motion';
import { 
  BarChart3, 
  TrendingUp, 
  Activity, 
  DollarSign,
  Upload,
  Settings,
  LogOut,
  Menu,
  X,
  Play,
  Square,
  AlertCircle,
  CheckCircle,
  Repeat
} from 'lucide-react';
import { useAuth } from '../contexts/AuthContext';
import Algorithm from './Algorithm';
import Backtesting from './Backtesting';
import DataUpload from './DataUpload';
import PriceStreaming from './PriceStreaming';
import HedgingAlgo from './HedgingAlgo';
import instruments from '../config/instruments';

const TradingDashboard = () => {
  const { user, signOut } = useAuth();
  const [activeSection, setActiveSection] = useState('prices');
  const [sidebarOpen, setSidebarOpen] = useState(true);
  const [algorithmStatus, setAlgorithmStatus] = useState('stopped');
  
  // Convert shared instruments config to dashboard format
  const instrumentsForDisplay = instruments.map(inst => {
    const [symbol, description] = inst.label.split(' - ');
    return {
      symbol: inst.value,
      name: description,
      exchange: inst.value.startsWith('M') && inst.value !== 'MES' && inst.value !== 'MNQ' ? 'COMEX' : 'CME'
    };
  });

  const menuItems = [
    { id: 'prices', label: 'Live Prices', icon: TrendingUp },
    { id: 'algorithm', label: 'Algorithm', icon: Activity },
    { id: 'hedging', label: 'Hedging Algo', icon: Repeat },
    { id: 'backtesting', label: 'Backtesting', icon: BarChart3 },
    { id: 'upload', label: 'Upload CSV', icon: Upload },
    { id: 'settings', label: 'Settings', icon: Settings }
  ];

  const renderContent = () => {
    switch (activeSection) {
      case 'prices':
        return <PriceStreaming instruments={instrumentsForDisplay} />;
      case 'algorithm':
        return (
          <Algorithm 
            onStatusChange={setAlgorithmStatus}
            instruments={instrumentsForDisplay}
          />
        );
      case 'hedging':
        return <HedgingAlgo />;
      case 'backtesting':
        return <Backtesting instruments={instrumentsForDisplay} />;
      case 'upload':
        return <DataUpload />;
      case 'settings':
        return <SettingsPanel />;
      default:
        return <PriceStreaming instruments={instrumentsForDisplay} />;
    }
  };

  const StatusIndicator = ({ status }) => {
    const getStatusColor = () => {
      switch (status) {
        case 'running': return 'bg-green-500';
        case 'stopped': return 'bg-gray-500';
        case 'error': return 'bg-red-500';
        default: return 'bg-gray-500';
      }
    };

    return (
      <div className="flex items-center space-x-2">
        <div className={`w-2 h-2 rounded-full ${getStatusColor()} animate-pulse`} />
        <span className="text-xs text-gray-400 uppercase">{status}</span>
      </div>
    );
  };

  const SettingsPanel = () => (
    <div className="p-6">
      <h2 className="text-2xl font-bold text-white mb-6">Settings</h2>
      <div className="bg-gray-900 border border-gray-800 rounded-lg p-6">
        <h3 className="text-lg font-semibold text-white mb-4">Trading Configuration</h3>
        <div className="space-y-4">
          <div>
            <label className="text-gray-400 text-sm">Default Account</label>
            <input 
              type="text" 
              className="w-full bg-black border border-gray-800 text-white px-3 py-2 rounded-md mt-1"
              placeholder="PAAPEX1361890000010"
            />
          </div>
          <div>
            <label className="text-gray-400 text-sm">Risk Per Trade (%)</label>
            <input 
              type="number" 
              className="w-full bg-black border border-gray-800 text-white px-3 py-2 rounded-md mt-1"
              placeholder="2"
            />
          </div>
          <div>
            <label className="text-gray-400 text-sm">Max Daily Loss</label>
            <input 
              type="number" 
              className="w-full bg-black border border-gray-800 text-white px-3 py-2 rounded-md mt-1"
              placeholder="5000"
            />
          </div>
        </div>
      </div>
    </div>
  );

  return (
    <div className="min-h-screen bg-black flex">
      {/* Sidebar */}
      <motion.div 
        initial={{ x: 0 }}
        animate={{ x: sidebarOpen ? 0 : -240 }}
        className="w-60 bg-gray-950 border-r border-gray-900 fixed h-full z-40"
      >
        <div className="p-4">
          <div className="flex items-center justify-between mb-8">
            <h1 className="text-xl font-bold text-white">ORCA Trading</h1>
            <button
              onClick={() => setSidebarOpen(!sidebarOpen)}
              className="text-gray-400 hover:text-white lg:hidden"
            >
              <X className="w-5 h-5" />
            </button>
          </div>

          {/* Algorithm Status */}
          <div className="mb-6 p-3 bg-gray-900 rounded-lg border border-gray-800">
            <div className="flex items-center justify-between mb-2">
              <span className="text-xs text-gray-400">Algorithm Status</span>
              <StatusIndicator status={algorithmStatus} />
            </div>
            <div className="text-sm text-white font-mono">
              9-Point Strategy
            </div>
          </div>

          {/* Menu Items */}
          <nav className="space-y-2">
            {menuItems.map((item) => (
              <button
                key={item.id}
                onClick={() => setActiveSection(item.id)}
                className={`w-full flex items-center space-x-3 px-3 py-2 rounded-lg transition-colors ${
                  activeSection === item.id
                    ? 'bg-white text-black'
                    : 'text-gray-400 hover:bg-gray-900 hover:text-white'
                }`}
              >
                <item.icon className="w-5 h-5" />
                <span className="text-sm font-medium">{item.label}</span>
              </button>
            ))}
          </nav>

          {/* User Section */}
          <div className="absolute bottom-0 left-0 right-0 p-4 border-t border-gray-900">
            <div className="flex items-center justify-between mb-3">
              <div>
                <p className="text-white text-sm font-medium">
                  {user?.email?.split('@')[0] || 'Trader'}
                </p>
                <p className="text-gray-400 text-xs">Pro Account</p>
              </div>
            </div>
            <button
              onClick={signOut}
              className="w-full flex items-center justify-center space-x-2 px-3 py-2 bg-gray-900 hover:bg-gray-800 text-gray-400 hover:text-white rounded-lg transition-colors"
            >
              <LogOut className="w-4 h-4" />
              <span className="text-sm">Sign Out</span>
            </button>
          </div>
        </div>
      </motion.div>

      {/* Main Content */}
      <div className={`flex-1 transition-all duration-300 ${sidebarOpen ? 'ml-60' : 'ml-0'}`}>
        {/* Header */}
        <header className="bg-gray-950 border-b border-gray-900 px-6 py-4">
          <div className="flex items-center justify-between">
            <div className="flex items-center space-x-4">
              <button
                onClick={() => setSidebarOpen(!sidebarOpen)}
                className="text-gray-400 hover:text-white"
              >
                <Menu className="w-5 h-5" />
              </button>
              <h2 className="text-xl font-semibold text-white capitalize">
                {activeSection === 'prices' ? 'Live Market Prices' : activeSection}
              </h2>
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
        <main className="bg-black min-h-screen">
          {renderContent()}
        </main>
      </div>
    </div>
  );
};

export default TradingDashboard;
