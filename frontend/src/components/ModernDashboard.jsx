import React, { useState } from 'react';
import { motion } from 'framer-motion';
import { 
  BarChart3, 
  TrendingUp, 
  Activity, 
  DollarSign,
  ArrowUpRight,
  ArrowDownRight,
  Calendar,
  Clock,
  Settings,
  Bell,
  Search,
  User,
  LogOut,
  ChevronRight,
  Zap,
  Shield,
  Target,
  Award
} from 'lucide-react';
import { useAuth } from '../contexts/AuthContext';
import { Button } from './ui/button';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from './ui/card';
import { Input } from './ui/input';

const ModernDashboard = () => {
  const { user, signOut } = useAuth();
  const [searchQuery, setSearchQuery] = useState('');

  // Mock data for demonstration
  const stats = [
    {
      title: 'Total Profit',
      value: '$42,850',
      change: '+12.5%',
      trend: 'up',
      icon: <DollarSign className="w-5 h-5" />,
      color: 'from-green-500 to-emerald-600'
    },
    {
      title: 'Win Rate',
      value: '68.4%',
      change: '+2.3%',
      trend: 'up',
      icon: <Target className="w-5 h-5" />,
      color: 'from-blue-500 to-cyan-600'
    },
    {
      title: 'Active Trades',
      value: '12',
      change: '+4',
      trend: 'up',
      icon: <Activity className="w-5 h-5" />,
      color: 'from-purple-500 to-pink-600'
    },
    {
      title: 'Risk Score',
      value: 'Low',
      change: 'Stable',
      trend: 'stable',
      icon: <Shield className="w-5 h-5" />,
      color: 'from-orange-500 to-red-600'
    }
  ];

  const recentTrades = [
    { id: 1, symbol: 'ES', type: 'Buy', time: '09:30', price: 4520.25, pnl: 250, status: 'profit' },
    { id: 2, symbol: 'NQ', type: 'Sell', time: '10:15', price: 15280.50, pnl: -75, status: 'loss' },
    { id: 3, symbol: 'ES', type: 'Buy', time: '11:45', price: 4522.75, pnl: 180, status: 'profit' },
    { id: 4, symbol: 'NQ', type: 'Buy', time: '13:20', price: 15285.25, pnl: 320, status: 'profit' },
    { id: 5, symbol: 'ES', type: 'Sell', time: '14:30', price: 4518.50, pnl: 95, status: 'profit' },
  ];

  const achievements = [
    { icon: <Award className="w-6 h-6" />, title: 'First Trade', unlocked: true },
    { icon: <TrendingUp className="w-6 h-6" />, title: '10 Win Streak', unlocked: true },
    { icon: <Zap className="w-6 h-6" />, title: 'Speed Trader', unlocked: false },
    { icon: <DollarSign className="w-6 h-6" />, title: '$100K Profit', unlocked: false },
  ];

  return (
    <div className="min-h-screen bg-gradient-to-br from-gray-900 via-gray-800 to-gray-900">
      {/* Header */}
      <motion.header 
        initial={{ opacity: 0, y: -20 }}
        animate={{ opacity: 1, y: 0 }}
        className="bg-gray-900/50 backdrop-blur-xl border-b border-gray-700/50"
      >
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex justify-between items-center h-16">
            {/* Logo and Search */}
            <div className="flex items-center space-x-8">
              <div className="flex items-center space-x-2">
                <div className="w-8 h-8 bg-gradient-to-r from-purple-600 to-pink-600 rounded-lg flex items-center justify-center">
                  <BarChart3 className="w-5 h-5 text-white" />
                </div>
                <span className="text-xl font-bold text-white">ORCA</span>
              </div>
              
              <div className="relative">
                <Search className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-gray-400" />
                <Input
                  type="text"
                  placeholder="Search markets..."
                  value={searchQuery}
                  onChange={(e) => setSearchQuery(e.target.value)}
                  className="pl-10 w-64 bg-gray-800/50 border-gray-700 text-white placeholder:text-gray-500"
                />
              </div>
            </div>

            {/* User Menu */}
            <div className="flex items-center space-x-4">
              <button className="relative text-gray-300 hover:text-white transition-colors">
                <Bell className="w-5 h-5" />
                <span className="absolute -top-1 -right-1 w-2 h-2 bg-red-500 rounded-full"></span>
              </button>
              
              <button className="text-gray-300 hover:text-white transition-colors">
                <Settings className="w-5 h-5" />
              </button>

              <div className="flex items-center space-x-3 pl-4 border-l border-gray-700">
                <div className="w-8 h-8 bg-gradient-to-r from-purple-600 to-pink-600 rounded-full flex items-center justify-center">
                  <User className="w-4 h-4 text-white" />
                </div>
                <div className="text-sm">
                  <p className="text-white font-medium">{user?.email?.split('@')[0] || 'Trader'}</p>
                  <p className="text-gray-400">Pro Account</p>
                </div>
                <button 
                  onClick={signOut}
                  className="text-gray-400 hover:text-white transition-colors"
                >
                  <LogOut className="w-4 h-4" />
                </button>
              </div>
            </div>
          </div>
        </div>
      </motion.header>

      {/* Main Content */}
      <main className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        {/* Welcome Section */}
        <motion.div 
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.1 }}
          className="mb-8"
        >
          <h1 className="text-3xl font-bold text-white mb-2">
            Welcome back, {user?.email?.split('@')[0] || 'Trader'}! 👋
          </h1>
          <p className="text-gray-400">
            Here's your trading performance overview for today
          </p>
        </motion.div>

        {/* Stats Grid */}
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 mb-8">
          {stats.map((stat, index) => (
            <motion.div
              key={stat.title}
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ delay: 0.1 + index * 0.05 }}
            >
              <Card className="bg-gray-800/50 backdrop-blur border-gray-700/50 hover:bg-gray-800/70 transition-all">
                <CardContent className="p-6">
                  <div className="flex items-start justify-between">
                    <div className="space-y-2">
                      <p className="text-gray-400 text-sm">{stat.title}</p>
                      <p className="text-2xl font-bold text-white">{stat.value}</p>
                      <div className="flex items-center space-x-1">
                        {stat.trend === 'up' ? (
                          <ArrowUpRight className="w-4 h-4 text-green-500" />
                        ) : stat.trend === 'down' ? (
                          <ArrowDownRight className="w-4 h-4 text-red-500" />
                        ) : null}
                        <span className={`text-sm ${
                          stat.trend === 'up' ? 'text-green-500' : 
                          stat.trend === 'down' ? 'text-red-500' : 'text-gray-400'
                        }`}>
                          {stat.change}
                        </span>
                      </div>
                    </div>
                    <div className={`w-12 h-12 rounded-lg bg-gradient-to-r ${stat.color} flex items-center justify-center`}>
                      {stat.icon}
                    </div>
                  </div>
                </CardContent>
              </Card>
            </motion.div>
          ))}
        </div>

        <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
          {/* Trading Chart Area */}
          <motion.div
            initial={{ opacity: 0, x: -20 }}
            animate={{ opacity: 1, x: 0 }}
            transition={{ delay: 0.3 }}
            className="lg:col-span-2"
          >
            <Card className="bg-gray-800/50 backdrop-blur border-gray-700/50">
              <CardHeader>
                <div className="flex justify-between items-center">
                  <div>
                    <CardTitle className="text-white">Market Performance</CardTitle>
                    <CardDescription className="text-gray-400">ES & NQ Futures</CardDescription>
                  </div>
                  <div className="flex space-x-2">
                    <Button variant="ghost" size="sm" className="text-gray-400 hover:text-white">
                      1D
                    </Button>
                    <Button variant="ghost" size="sm" className="text-gray-400 hover:text-white">
                      1W
                    </Button>
                    <Button variant="ghost" size="sm" className="bg-gray-700 text-white">
                      1M
                    </Button>
                    <Button variant="ghost" size="sm" className="text-gray-400 hover:text-white">
                      1Y
                    </Button>
                  </div>
                </div>
              </CardHeader>
              <CardContent>
                <div className="h-96 flex items-center justify-center">
                  <div className="text-center">
                    <BarChart3 className="w-16 h-16 text-gray-600 mx-auto mb-4" />
                    <p className="text-gray-400">Live chart will be displayed here</p>
                    <p className="text-gray-500 text-sm mt-2">Connected to real-time data feed</p>
                  </div>
                </div>
              </CardContent>
            </Card>
          </motion.div>

          {/* Recent Activity */}
          <motion.div
            initial={{ opacity: 0, x: 20 }}
            animate={{ opacity: 1, x: 0 }}
            transition={{ delay: 0.4 }}
          >
            <Card className="bg-gray-800/50 backdrop-blur border-gray-700/50">
              <CardHeader>
                <CardTitle className="text-white">Recent Trades</CardTitle>
                <CardDescription className="text-gray-400">Your latest transactions</CardDescription>
              </CardHeader>
              <CardContent>
                <div className="space-y-3">
                  {recentTrades.map((trade) => (
                    <div key={trade.id} className="flex items-center justify-between p-3 bg-gray-900/50 rounded-lg hover:bg-gray-900/70 transition-colors">
                      <div className="flex items-center space-x-3">
                        <div className={`w-10 h-10 rounded-lg flex items-center justify-center ${
                          trade.type === 'Buy' ? 'bg-green-500/20' : 'bg-red-500/20'
                        }`}>
                          <TrendingUp className={`w-5 h-5 ${
                            trade.type === 'Buy' ? 'text-green-500' : 'text-red-500'
                          }`} />
                        </div>
                        <div>
                          <p className="text-white font-medium">{trade.symbol}</p>
                          <p className="text-gray-400 text-sm">{trade.time} • {trade.type}</p>
                        </div>
                      </div>
                      <div className="text-right">
                        <p className="text-white font-medium">${Math.abs(trade.pnl)}</p>
                        <p className={`text-sm ${
                          trade.status === 'profit' ? 'text-green-500' : 'text-red-500'
                        }`}>
                          {trade.status === 'profit' ? '+' : '-'}{Math.abs(trade.pnl)}
                        </p>
                      </div>
                    </div>
                  ))}
                </div>
                <Button className="w-full mt-4 bg-gray-700 hover:bg-gray-600 text-white">
                  View All Trades
                  <ChevronRight className="w-4 h-4 ml-2" />
                </Button>
              </CardContent>
            </Card>
          </motion.div>
        </div>

        {/* Achievements Section */}
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.5 }}
          className="mt-8"
        >
          <Card className="bg-gray-800/50 backdrop-blur border-gray-700/50">
            <CardHeader>
              <CardTitle className="text-white">Trading Achievements</CardTitle>
              <CardDescription className="text-gray-400">Track your milestones</CardDescription>
            </CardHeader>
            <CardContent>
              <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
                {achievements.map((achievement, index) => (
                  <div
                    key={index}
                    className={`p-4 rounded-lg border transition-all ${
                      achievement.unlocked 
                        ? 'bg-gradient-to-r from-purple-600/20 to-pink-600/20 border-purple-500/50' 
                        : 'bg-gray-900/50 border-gray-700/50 opacity-50'
                    }`}
                  >
                    <div className={`w-12 h-12 rounded-lg mb-2 flex items-center justify-center ${
                      achievement.unlocked 
                        ? 'bg-gradient-to-r from-purple-600 to-pink-600' 
                        : 'bg-gray-800'
                    }`}>
                      {achievement.icon}
                    </div>
                    <p className={`text-sm font-medium ${
                      achievement.unlocked ? 'text-white' : 'text-gray-500'
                    }`}>
                      {achievement.title}
                    </p>
                  </div>
                ))}
              </div>
            </CardContent>
          </Card>
        </motion.div>

        {/* Quick Actions */}
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.6 }}
          className="mt-8 grid grid-cols-1 md:grid-cols-3 gap-4"
        >
          <Button className="h-24 bg-gradient-to-r from-green-600 to-emerald-600 hover:from-green-700 hover:to-emerald-700 text-white">
            <div className="text-center">
              <TrendingUp className="w-8 h-8 mx-auto mb-2" />
              <span className="font-medium">Start Trading</span>
            </div>
          </Button>
          <Button className="h-24 bg-gradient-to-r from-blue-600 to-cyan-600 hover:from-blue-700 hover:to-cyan-700 text-white">
            <div className="text-center">
              <BarChart3 className="w-8 h-8 mx-auto mb-2" />
              <span className="font-medium">Run Backtest</span>
            </div>
          </Button>
          <Button className="h-24 bg-gradient-to-r from-purple-600 to-pink-600 hover:from-purple-700 hover:to-pink-700 text-white">
            <div className="text-center">
              <Activity className="w-8 h-8 mx-auto mb-2" />
              <span className="font-medium">View Analytics</span>
            </div>
          </Button>
        </motion.div>
      </main>
    </div>
  );
};

export default ModernDashboard;
