import React, { useState } from 'react';
import { Toaster } from 'react-hot-toast';
import { AuthProvider, useAuth } from './contexts/AuthContext';
import Layout from './components/Layout';
import Login from './components/Login';
import Dashboard from './components/Dashboard';
import Algorithm from './components/Algorithm';
import Backtesting from './components/Backtesting';
import DataUpload from './components/DataUpload';
import './App.css';

// Main App Content Component
function AppContent() {
  const { user, loading } = useAuth();
  const [activeSection, setActiveSection] = useState('dashboard');

  // Show loading spinner while checking auth
  if (loading) {
    return (
      <div className="min-h-screen bg-gray-900 flex items-center justify-center">
        <div className="text-center">
          <div className="animate-spin rounded-full h-16 w-16 border-b-2 border-blue-500 mx-auto mb-4"></div>
          <p className="text-gray-400 text-lg">Loading ORCA Trading System...</p>
        </div>
      </div>
    );
  }

  if (!user) {
    return <Login />;
  }

  // Render the active section
  const renderContent = () => {
    switch (activeSection) {
      case 'dashboard':
        return <Dashboard />;
      case 'algorithm':
        return <Algorithm />;
      case 'backtesting':
        return <Backtesting />;
      case 'data':
        return <DataUpload />;
      default:
        return <Dashboard />;
    }
  };

  // Main application layout
  return (
    <Layout activeSection={activeSection} setActiveSection={setActiveSection}>
      {renderContent()}
    </Layout>
  );
}

// Root App Component with Providers
function App() {
  return (
    <AuthProvider>
      <Toaster
        position="top-right"
        toastOptions={{
          duration: 4000,
          style: {
            background: '#1f2937',
            color: '#fff',
            border: '1px solid #374151',
          },
          success: {
            iconTheme: {
              primary: '#10b981',
              secondary: '#fff',
            },
          },
          error: {
            iconTheme: {
              primary: '#ef4444',
              secondary: '#fff',
            },
          },
        }}
      />
      <AppContent />
    </AuthProvider>
  );
}

export default App;
