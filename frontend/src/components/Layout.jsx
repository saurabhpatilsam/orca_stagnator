import React, { useState } from 'react';
import { motion } from 'framer-motion';
import { 
  LayoutDashboard, 
  Activity, 
  TestTube, 
  Database, 
  LogOut, 
  User,
  Menu,
  X,
  ChevronRight
} from 'lucide-react';
import { useAuth } from '../contexts/AuthContext';

const Layout = ({ children, activeSection, setActiveSection }) => {
  const { user, signOut } = useAuth();
  const [sidebarOpen, setSidebarOpen] = useState(true);

  const menuItems = [
    { id: 'dashboard', label: 'Dashboard', icon: LayoutDashboard },
    { id: 'algorithm', label: 'Algorithm', icon: Activity },
    { id: 'backtesting', label: 'Backtesting', icon: TestTube },
    { id: 'data', label: 'Data', icon: Database }
  ];

  return (
    <div className="min-h-screen bg-gray-900 text-white flex">
      {/* Sidebar */}
      <motion.div 
        className={`bg-gray-800 border-r border-gray-700 transition-all duration-300 ${
          sidebarOpen ? 'w-64' : 'w-20'
        }`}
        initial={{ x: -100 }}
        animate={{ x: 0 }}
      >
        <div className="h-full flex flex-col">
          {/* Logo and Toggle */}
          <div className="p-4 border-b border-gray-700">
            <div className="flex items-center justify-between">
              <motion.h1 
                className={`font-bold text-xl bg-gradient-to-r from-blue-500 to-purple-500 bg-clip-text text-transparent ${
                  !sidebarOpen && 'hidden'
                }`}
                initial={{ opacity: 0 }}
                animate={{ opacity: sidebarOpen ? 1 : 0 }}
              >
                ORCA Trading
              </motion.h1>
              <button
                onClick={() => setSidebarOpen(!sidebarOpen)}
                className="p-2 hover:bg-gray-700 rounded-lg transition-colors"
              >
                {sidebarOpen ? <X size={20} /> : <Menu size={20} />}
              </button>
            </div>
          </div>

          {/* Navigation */}
          <nav className="flex-1 p-4">
            {menuItems.map((item) => (
              <motion.button
                key={item.id}
                onClick={() => setActiveSection(item.id)}
                className={`w-full flex items-center gap-3 px-4 py-3 mb-2 rounded-lg transition-all ${
                  activeSection === item.id
                    ? 'bg-blue-600 text-white shadow-lg shadow-blue-600/30'
                    : 'hover:bg-gray-700'
                }`}
                whileHover={{ x: 5 }}
                whileTap={{ scale: 0.95 }}
              >
                <item.icon size={20} />
                {sidebarOpen && (
                  <span className="flex-1 text-left">{item.label}</span>
                )}
                {sidebarOpen && activeSection === item.id && (
                  <ChevronRight size={16} />
                )}
              </motion.button>
            ))}
          </nav>

          {/* User Section */}
          <div className="p-4 border-t border-gray-700">
            <div className="flex items-center gap-3 mb-3">
              <div className="w-10 h-10 bg-blue-600 rounded-full flex items-center justify-center">
                <User size={20} />
              </div>
              {sidebarOpen && (
                <div className="flex-1">
                  <p className="text-sm font-medium">{user?.email?.split('@')[0]}</p>
                  <p className="text-xs text-gray-400">{user?.email}</p>
                </div>
              )}
            </div>
            <button
              onClick={signOut}
              className="w-full flex items-center gap-3 px-4 py-2 hover:bg-gray-700 rounded-lg transition-colors"
            >
              <LogOut size={20} />
              {sidebarOpen && <span>Sign Out</span>}
            </button>
          </div>
        </div>
      </motion.div>

      {/* Main Content */}
      <div className="flex-1 overflow-hidden">
        <motion.div
          key={activeSection}
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.3 }}
          className="h-full"
        >
          {children}
        </motion.div>
      </div>
    </div>
  );
};

export default Layout;
