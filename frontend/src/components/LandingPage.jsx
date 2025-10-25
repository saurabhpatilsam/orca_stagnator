import React from 'react';
import { Link } from 'react-router-dom';
import { useAuth } from '../contexts/AuthContext';
import { 
  TrendingUp, 
  BarChart3, 
  Shield, 
  Zap, 
  Users, 
  ArrowRight,
  LogIn,
  UserPlus,
  LogOut
} from 'lucide-react';

const LandingPage = () => {
  const { user, signOut } = useAuth();

  const features = [
    {
      icon: <TrendingUp className="h-8 w-8" />,
      title: "Advanced Trading Algorithms",
      description: "Sophisticated 9-point strategy with real-time market analysis"
    },
    {
      icon: <BarChart3 className="h-8 w-8" />,
      title: "Live Market Data",
      description: "Real-time ES/NQ futures data with tick-by-tick precision"
    },
    {
      icon: <Shield className="h-8 w-8" />,
      title: "Risk Management",
      description: "Built-in risk controls and position sizing algorithms"
    },
    {
      icon: <Zap className="h-8 w-8" />,
      title: "High-Frequency Trading",
      description: "Optimized for speed with sub-millisecond execution"
    }
  ];

  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-900 via-blue-900 to-indigo-900">
      {/* Navigation */}
      <nav className="bg-white/10 backdrop-blur-md border-b border-white/20">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex justify-between items-center py-4">
            <div className="flex items-center">
              <div className="flex-shrink-0">
                <h1 className="text-2xl font-bold text-white">ORCA Trading</h1>
              </div>
            </div>
            <div className="flex items-center space-x-4">
              {user ? (
                <div className="flex items-center space-x-4">
                  <span className="text-white/80">Welcome, {user.email}</span>
                  <Link
                    to="/dashboard"
                    className="bg-indigo-600 hover:bg-indigo-700 text-white px-4 py-2 rounded-md text-sm font-medium transition-colors"
                  >
                    Dashboard
                  </Link>
                  <button
                    onClick={signOut}
                    className="flex items-center space-x-2 text-white/80 hover:text-white transition-colors"
                  >
                    <LogOut className="h-4 w-4" />
                    <span>Sign Out</span>
                  </button>
                </div>
              ) : (
                <div className="flex items-center space-x-4">
                  <Link
                    to="/signin"
                    className="flex items-center space-x-2 text-white/80 hover:text-white transition-colors"
                  >
                    <LogIn className="h-4 w-4" />
                    <span>Sign In</span>
                  </Link>
                  <Link
                    to="/signup"
                    className="bg-indigo-600 hover:bg-indigo-700 text-white px-4 py-2 rounded-md text-sm font-medium transition-colors"
                  >
                    Get Started
                  </Link>
                </div>
              )}
            </div>
          </div>
        </div>
      </nav>

      {/* Hero Section */}
      <div className="relative overflow-hidden">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-24">
          <div className="text-center">
            <h1 className="text-4xl md:text-6xl font-bold text-white mb-6">
              Professional Trading
              <span className="block text-transparent bg-clip-text bg-gradient-to-r from-blue-400 to-indigo-400">
                Made Simple
              </span>
            </h1>
            <p className="text-xl text-white/80 mb-8 max-w-3xl mx-auto">
              Advanced algorithmic trading platform for ES/NQ futures with real-time data analysis, 
              backtesting capabilities, and institutional-grade execution.
            </p>
            <div className="flex flex-col sm:flex-row gap-4 justify-center">
              {user ? (
                <Link
                  to="/dashboard"
                  className="inline-flex items-center px-8 py-3 border border-transparent text-base font-medium rounded-md text-white bg-indigo-600 hover:bg-indigo-700 transition-colors"
                >
                  Go to Dashboard
                  <ArrowRight className="ml-2 h-5 w-5" />
                </Link>
              ) : (
                <>
                  <Link
                    to="/signup"
                    className="inline-flex items-center px-8 py-3 border border-transparent text-base font-medium rounded-md text-white bg-indigo-600 hover:bg-indigo-700 transition-colors"
                  >
                    Start Trading
                    <UserPlus className="ml-2 h-5 w-5" />
                  </Link>
                  <Link
                    to="/signin"
                    className="inline-flex items-center px-8 py-3 border border-white/20 text-base font-medium rounded-md text-white hover:bg-white/10 transition-colors"
                  >
                    Sign In
                    <LogIn className="ml-2 h-5 w-5" />
                  </Link>
                </>
              )}
            </div>
          </div>
        </div>
      </div>

      {/* Features Section */}
      <div className="py-24 bg-white/5">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="text-center mb-16">
            <h2 className="text-3xl md:text-4xl font-bold text-white mb-4">
              Why Choose ORCA Trading?
            </h2>
            <p className="text-xl text-white/80 max-w-2xl mx-auto">
              Built by traders, for traders. Our platform combines cutting-edge technology 
              with proven trading strategies.
            </p>
          </div>
          
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-8">
            {features.map((feature, index) => (
              <div
                key={index}
                className="bg-white/10 backdrop-blur-md rounded-lg p-6 border border-white/20 hover:bg-white/20 transition-colors"
              >
                <div className="text-indigo-400 mb-4">
                  {feature.icon}
                </div>
                <h3 className="text-xl font-semibold text-white mb-2">
                  {feature.title}
                </h3>
                <p className="text-white/70">
                  {feature.description}
                </p>
              </div>
            ))}
          </div>
        </div>
      </div>

      {/* CTA Section */}
      <div className="py-24">
        <div className="max-w-4xl mx-auto text-center px-4 sm:px-6 lg:px-8">
          <h2 className="text-3xl md:text-4xl font-bold text-white mb-4">
            Ready to Start Trading?
          </h2>
          <p className="text-xl text-white/80 mb-8">
            Join thousands of traders who trust ORCA for their algorithmic trading needs.
          </p>
          {!user && (
            <Link
              to="/signup"
              className="inline-flex items-center px-8 py-3 border border-transparent text-base font-medium rounded-md text-white bg-indigo-600 hover:bg-indigo-700 transition-colors"
            >
              Create Free Account
              <ArrowRight className="ml-2 h-5 w-5" />
            </Link>
          )}
        </div>
      </div>

      {/* Footer */}
      <footer className="bg-white/5 border-t border-white/20">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
          <div className="text-center text-white/60">
            <p>&copy; 2025 ORCA Trading Platform. All rights reserved.</p>
          </div>
        </div>
      </footer>
    </div>
  );
};

export default LandingPage;
