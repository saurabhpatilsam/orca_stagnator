import React, { useState } from 'react';
import { BrowserRouter as Router, Routes, Route, Navigate } from 'react-router-dom';
import { Toaster } from 'react-hot-toast';
import { AuthProvider, useAuth } from './contexts/AuthContext';
import Layout from './components/Layout';
import LandingPage from './components/LandingPage';
import MinimalSignIn from './components/auth/MinimalSignIn';
import ModernSignUp from './components/auth/ModernSignUp';
import ProtectedRoute from './components/auth/ProtectedRoute';
import TradingDashboard from './components/TradingDashboard';
import Algorithm from './components/Algorithm';
import Backtesting from './components/Backtesting';
import DataUpload from './components/DataUpload';
import HedgingAlgo from './components/HedgingAlgo';
import './App.css';

// Main App Content Component
function AppContent() {
  const [activeSection, setActiveSection] = useState('dashboard');

  // Render the active section for dashboard
  const renderDashboardContent = () => {
    switch (activeSection) {
      case 'dashboard':
        return <ModernDashboard />;
      case 'algorithm':
        return <Algorithm />;
      case 'backtesting':
        return <Backtesting />;
      case 'data':
        return <DataUpload />;
      default:
        return <ModernDashboard />;
    }
  };

  return (
    <Routes>
      {/* Public Routes */}
      <Route path="/" element={<LandingPage />} />
      <Route path="/signin" element={<MinimalSignIn />} />
      <Route path="/signup" element={<ModernSignUp />} />
      
      {/* Protected Routes */}
      <Route 
        path="/dashboard" 
        element={
          <ProtectedRoute>
            <TradingDashboard />
          </ProtectedRoute>
        } 
      />
      
      {/* Additional protected routes */}
      <Route 
        path="/algorithm" 
        element={
          <ProtectedRoute>
            <Algorithm />
          </ProtectedRoute>
        } 
      />
      <Route 
        path="/backtesting" 
        element={
          <ProtectedRoute>
            <Backtesting />
          </ProtectedRoute>
        } 
      />
      <Route 
        path="/data" 
        element={
          <ProtectedRoute>
            <DataUpload />
          </ProtectedRoute>
        } 
      />
      <Route 
        path="/hedging-algo" 
        element={
          <ProtectedRoute>
            <HedgingAlgo />
          </ProtectedRoute>
        } 
      />
      
      {/* Catch all route */}
      <Route path="*" element={<Navigate to="/" replace />} />
    </Routes>
  );
}

// Root App Component with Providers
function App() {
  return (
    <Router>
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
    </Router>
  );
}

export default App;
