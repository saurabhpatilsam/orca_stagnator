import React, { useState, useEffect } from 'react';
import { motion } from 'framer-motion';
import { 
  TrendingUp, 
  TrendingDown, 
  Activity,
  Users,
  CreditCard,
  Play,
  Square,
  AlertCircle
} from 'lucide-react';
import tradingViewService from '../services/tradingViewService';
import { supabase } from '../config/supabase';
import toast from 'react-hot-toast';

const Dashboard = () => {
  const [prices, setPrices] = useState({});
  const [activeAlgorithms, setActiveAlgorithms] = useState([]);
  const [accounts, setAccounts] = useState([]);
  const [priceConnection, setPriceConnection] = useState(null);
  const [loading, setLoading] = useState(true);

  const symbols = ['MNQ', 'NQ', 'ES', 'MES', 'GC', 'MGC'];

  useEffect(() => {
    // Start price updates
    const connection = tradingViewService.startPriceUpdates(symbols, (newPrices) => {
      setPrices(newPrices);
    });
    setPriceConnection(connection);

    // Fetch accounts
    fetchAccounts();
    
    // Fetch active algorithms
    fetchActiveAlgorithms();

    setLoading(false);

    return () => {
      if (connection) {
        tradingViewService.stopPriceUpdates(connection);
      }
    };
  }, []);

  const fetchAccounts = async () => {
    try {
      // Fetch from Supabase
      const { data, error } = await supabase
        .from('accounts')
        .select('*')
        .order('created_at', { ascending: false });

      if (!error && data) {
        setAccounts(data);
      } else {
        // Use mock data if table doesn't exist
        setAccounts([
          { id: 1, name: 'PAAPEX1361890000010', type: 'Demo', balance: 100000, status: 'Active' },
          { id: 2, name: 'PAAPEX1361890000011', type: 'Demo', balance: 50000, status: 'Active' }
        ]);
      }
    } catch (error) {
      console.error('Error fetching accounts:', error);
      // Use mock data
      setAccounts([
        { id: 1, name: 'PAAPEX1361890000010', type: 'Demo', balance: 100000, status: 'Active' },
        { id: 2, name: 'PAAPEX1361890000011', type: 'Demo', balance: 50000, status: 'Active' }
      ]);
    }
  };

  const fetchActiveAlgorithms = async () => {
    try {
      // Fetch from Supabase
      const { data, error } = await supabase
        .from('active_algorithms')
        .select('*')
        .eq('status', 'running');

      if (!error && data) {
        setActiveAlgorithms(data);
      } else {
        // Use mock data if table doesn't exist
        setActiveAlgorithms([]);
      }
    } catch (error) {
      console.error('Error fetching algorithms:', error);
      setActiveAlgorithms([]);
    }
  };

  const stopAlgorithm = async (algorithmId) => {
    try {
      // Update algorithm status in database
      const { error } = await supabase
        .from('active_algorithms')
        .update({ status: 'stopped', stopped_at: new Date() })
        .eq('id', algorithmId);

      if (!error) {
        toast.success('Algorithm stopped successfully');
        fetchActiveAlgorithms();
      } else {
        toast.error('Failed to stop algorithm');
      }
    } catch (error) {
      toast.error('Error stopping algorithm');
      console.error(error);
    }
  };

  const PriceCard = ({ symbol, data }) => {
    const isPositive = parseFloat(data?.change || 0) >= 0;
    
    return (
      <motion.div
        className="bg-gray-800 rounded-xl p-4 border border-gray-700"
        whileHover={{ scale: 1.02 }}
        transition={{ duration: 0.2 }}
      >
        <div className="flex justify-between items-start mb-2">
          <h3 className="text-lg font-bold text-gray-300">{symbol}</h3>
          <div className={`flex items-center ${isPositive ? 'text-green-500' : 'text-red-500'}`}>
            {isPositive ? <TrendingUp size={20} /> : <TrendingDown size={20} />}
          </div>
        </div>
        <div className="text-2xl font-bold mb-1">
          ${data?.price || '0.00'}
        </div>
        <div className={`flex items-center gap-2 text-sm ${isPositive ? 'text-green-500' : 'text-red-500'}`}>
          <span>{isPositive ? '+' : ''}{data?.change || '0.00'}</span>
          <span>({isPositive ? '+' : ''}{data?.changePercent || '0.00'}%)</span>
        </div>
        <div className="mt-2 pt-2 border-t border-gray-700 grid grid-cols-2 gap-2 text-xs text-gray-400">
          <div>High: ${data?.high || '0.00'}</div>
          <div>Low: ${data?.low || '0.00'}</div>
          <div>Bid: ${data?.bid || '0.00'}</div>
          <div>Ask: ${data?.ask || '0.00'}</div>
        </div>
      </motion.div>
    );
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center h-full">
        <div className="text-center">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-500 mx-auto mb-4"></div>
          <p className="text-gray-400">Loading dashboard...</p>
        </div>
      </div>
    );
  }

  return (
    <div className="h-full overflow-auto p-6">
      {/* Header */}
      <div className="mb-6">
        <h1 className="text-3xl font-bold mb-2">Trading Dashboard</h1>
        <p className="text-gray-400">Real-time market data and algorithm monitoring</p>
      </div>

      {/* Price Grid */}
      <div className="mb-8">
        <h2 className="text-xl font-semibold mb-4 flex items-center gap-2">
          <Activity className="text-blue-500" />
          Live Market Prices
        </h2>
        <div className="grid grid-cols-1 md:grid-cols-3 lg:grid-cols-6 gap-4">
          {symbols.map(symbol => (
            <PriceCard key={symbol} symbol={symbol} data={prices[symbol]} />
          ))}
        </div>
      </div>

      {/* Active Algorithms */}
      <div className="mb-8">
        <h2 className="text-xl font-semibold mb-4 flex items-center gap-2">
          <Activity className="text-green-500" />
          Active Algorithms
        </h2>
        <div className="bg-gray-800 rounded-xl border border-gray-700">
          {activeAlgorithms.length > 0 ? (
            <div className="p-4">
              {activeAlgorithms.map((algo) => (
                <div key={algo.id} className="flex items-center justify-between p-4 border-b border-gray-700 last:border-0">
                  <div className="flex items-center gap-4">
                    <div className="w-3 h-3 bg-green-500 rounded-full animate-pulse"></div>
                    <div>
                      <h3 className="font-semibold">{algo.name || '9 Point Algorithm'}</h3>
                      <p className="text-sm text-gray-400">Started: {new Date(algo.started_at || Date.now()).toLocaleString()}</p>
                    </div>
                  </div>
                  <button
                    onClick={() => stopAlgorithm(algo.id)}
                    className="flex items-center gap-2 px-4 py-2 bg-red-600 hover:bg-red-700 rounded-lg transition-colors"
                  >
                    <Square size={16} />
                    Stop
                  </button>
                </div>
              ))}
            </div>
          ) : (
            <div className="p-8 text-center text-gray-400">
              <AlertCircle className="mx-auto mb-2" size={32} />
              <p>No active algorithms running</p>
              <p className="text-sm mt-1">Start an algorithm from the Algorithm section</p>
            </div>
          )}
        </div>
      </div>

      {/* User Accounts */}
      <div>
        <h2 className="text-xl font-semibold mb-4 flex items-center gap-2">
          <Users className="text-purple-500" />
          Trading Accounts
        </h2>
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
          {accounts.map((account) => (
            <motion.div
              key={account.id}
              className="bg-gray-800 rounded-xl p-4 border border-gray-700"
              whileHover={{ scale: 1.02 }}
            >
              <div className="flex items-center gap-3 mb-3">
                <div className="w-10 h-10 bg-purple-600 rounded-full flex items-center justify-center">
                  <CreditCard size={20} />
                </div>
                <div>
                  <h3 className="font-semibold">{account.name}</h3>
                  <p className="text-sm text-gray-400">{account.type} Account</p>
                </div>
              </div>
              <div className="space-y-2 text-sm">
                <div className="flex justify-between">
                  <span className="text-gray-400">Balance:</span>
                  <span className="font-semibold">${(account.balance || 0).toLocaleString()}</span>
                </div>
                <div className="flex justify-between">
                  <span className="text-gray-400">Status:</span>
                  <span className={`px-2 py-1 rounded text-xs ${
                    account.status === 'Active' ? 'bg-green-600' : 'bg-gray-600'
                  }`}>
                    {account.status}
                  </span>
                </div>
              </div>
            </motion.div>
          ))}
        </div>
      </div>
    </div>
  );
};

export default Dashboard;
